import customtkinter as ctk
from . import dialogs as messagebox
import os
from ..core.keepass_db import KeePassDatabaseManager
from ..core.utils import check_password_strength
from .styles import COLORS
import base64

class LoginWindow(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        self.kdbx_manager = KeePassDatabaseManager()
        self.on_login_success = on_login_success
        
        # Set Icon
        import sys
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = "D:\\cyber\\mmpasswd" # Hardcoded for this environment
            
        icon_path = os.path.join(base_path, "app.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(default=icon_path)
            self.title("MMPasswd - Login")
        else:
            if os.path.exists("app.ico"):
                self.iconbitmap(default="app.ico")
        
        # Brute Force Protection
        self.failed_attempts = 0
        self.lockout_until = None
        
        # Load Theme
        import json
        try:
            if os.path.exists("config.json"):
                with open("config.json", 'r') as f:
                    data = json.load(f)
                    theme = data.get("theme", "Dark")
                    ctk.set_appearance_mode(theme)
                    if theme == "Light":
                        from .styles import THEMES, COLORS
                        COLORS.clear()
                        COLORS.update(THEMES[theme]["colors"])
        except: pass
        
        self.setup_ui()
        
    def setup_ui(self):
        self.title("MMPasswd - Login")
        w = 420
        h = 550
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.configure(fg_color=COLORS["bg"])
        self.resizable(False, False)
        
        # Check if setup is needed
        self.is_setup = not self.kdbx_manager.is_setup()
        
        # Logo/Header
        title_text = "Create Master Password" if self.is_setup else "Unlock Vault"
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(main_container, text="🛡️", font=("Segoe UI Emoji", 64), justify="center").pack(pady=(0, 10), anchor="center")
        ctk.CTkLabel(main_container, text="MMPasswd", font=("Segoe UI", 24, "bold"), text_color=COLORS["text"]).pack()
        ctk.CTkLabel(main_container, text=title_text, font=("Segoe UI", 16), text_color=COLORS["text_dim"]).pack(pady=(0, 20))
        
        self.password_entry = ctk.CTkEntry(main_container, placeholder_text="Master Password", 
                                         show="*", width=280, height=35)
        self.password_entry.pack(pady=10)
        self.password_entry.focus()
        
        if self.is_setup:
            self.confirm_entry = ctk.CTkEntry(main_container, placeholder_text="Confirm Password", show="*", width=280)
            self.confirm_entry.pack(pady=10)
            
            strength_frame = ctk.CTkFrame(main_container, fg_color="transparent")
            strength_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            bar = ctk.CTkProgressBar(strength_frame, height=4)
            bar.set(0)
            bar.pack(fill="x", pady=(0, 5))
            
            lbl_strength = ctk.CTkLabel(strength_frame, text="", font=("Segoe UI", 11))
            lbl_strength.pack()
            
            def update_strength(event=None):
                pwd = self.password_entry.get()
                score, label, color = check_password_strength(pwd)
                bar.set(score / 4)
                bar.configure(progress_color=color)
                lbl_strength.configure(text=label, text_color=color)
                
            self.password_entry.bind("<KeyRelease>", update_strength)
            
            ctk.CTkLabel(main_container, text="⚠️ Warning: If you lose this password,\nyour data cannot be recovered.", 
                         text_color=COLORS["warning"], font=("Segoe UI", 12)).pack(pady=(10, 10))
            
            btn_text = "Create Vault"
            cmd = self.create_vault
            self.confirm_entry.bind("<Return>", lambda e: self.create_vault())
        else:
            btn_text = "Unlock"
            cmd = self.unlock_vault
            self.password_entry.bind("<Return>", lambda e: self.unlock_vault())
            
        self.error_label = ctk.CTkLabel(main_container, text="", text_color=COLORS["danger"], 
                                      font=("Segoe UI", 12, "bold"), wraplength=300)
        self.error_label.pack(pady=(0, 5))

        ctk.CTkButton(main_container, text=btn_text, command=cmd, 
                     fg_color=COLORS["primary"], text_color=COLORS["text_button"],
                     hover_color=COLORS["primary_hover"], width=280, height=32, font=("Segoe UI", 14, "bold")).pack(pady=(10, 0))
    
    def create_vault(self):
        pwd = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not pwd:
             self.show_error("Password cannot be empty.")
             return
             
        score, label, _ = check_password_strength(pwd)
        if score < 3:
             self.show_error(f"Weak Password ({label}).\nUse mix of chars/digits/symbols.")
             return

        if pwd != confirm:
            self.show_error("Passwords do not match.")
            return

        if self.kdbx_manager.is_setup(): 
            if not messagebox.askyesno("Warning", "Vault exists! Overwrite?"):
                return
            
            try:
                self.kdbx_manager.create_database(pwd)
                self.on_login_success(self.kdbx_manager)
                self.destroy()
            except Exception as e:
                self.show_error(f"Failed: {e}")

    def show_error(self, message):
        self.error_label.configure(text=message)
        self.password_entry.configure(border_color=COLORS["danger"])
        
    def unlock_vault(self):
        self.password_entry.configure(border_color=COLORS["input_bg"])
        self.error_label.configure(text="")
        
        if self.lockout_until:
            from datetime import datetime
            remaining = (self.lockout_until - datetime.now()).total_seconds()
            if remaining > 0:
                self.show_error(f"Locked. Try again in {int(remaining)}s.")
                return
            else:
                self.lockout_until = None
                self.failed_attempts = 0

        pwd = self.password_entry.get()
        if not pwd: return
        
        if self.kdbx_manager.load_database(pwd):
            self.on_login_success(self.kdbx_manager)
            self.destroy()
        else:
            self.failed_attempts += 1
            if self.failed_attempts >= 5:
                from datetime import datetime, timedelta
                self.lockout_until = datetime.now() + timedelta(seconds=30)
                self.show_error("Too many failed attempts.\nLocked for 30s.")
            else:
                remaining = 5 - self.failed_attempts
                self.show_error(f"Invalid Password.\n{remaining} attempts remaining.")
            self.password_entry.delete(0, 'end')

