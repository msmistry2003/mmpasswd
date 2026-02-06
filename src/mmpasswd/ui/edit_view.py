import customtkinter as ctk
from . import dialogs as messagebox
from .styles import COLORS
from ..core.utils import generate_password, secure_copy, check_password_strength

class EditView(ctk.CTkScrollableFrame):
    def __init__(self, parent, kdbx_manager, app_instance, entry=None, password=""):
        super().__init__(parent, fg_color="transparent")
        self.kdbx_manager = kdbx_manager
        self.app = app_instance
        self.entry = entry
        self.password_val = password
        self.fields = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        title = "Edit Password" if self.entry else "Add New Password"
        ctk.CTkLabel(self, text=title, font=("Segoe UI", 32, "bold"), text_color=COLORS["text"]).pack(anchor="w", pady=(0, 30))
        
        self.add_input("Username", "username", self.entry['username'] if self.entry and self.entry.get('username') else "")
        
        self.add_input("Password", "password", self.password_val if self.password_val else "", is_secret=True)
        self.add_input("Website", "website", self.entry['website'] if self.entry and self.entry.get('website') else "")
        self.add_input("Notes", "notes", self.entry['notes'] if self.entry and self.entry.get('notes') else "")
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=40)
        
        ctk.CTkButton(btn_frame, text="Save", fg_color=COLORS["primary"], 
                      text_color=COLORS["text_button"],
                      command=self.save).pack(side="left", padx=(0, 20))
                      
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="transparent", 
                      text_color=COLORS["text"], border_width=1, border_color=COLORS["text_dim"],
                      hover_color=COLORS["input_bg"],
                      command=self.cancel).pack(side="left")

    def add_input(self, label, key, default="", is_secret=False):
        ctk.CTkLabel(self, text=label, text_color=COLORS["text_dim"]).pack(anchor="w", padx=20, pady=(10, 5))
        
        if is_secret:
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(fill="x", padx=20)
            
            e = ctk.CTkEntry(frame, fg_color=COLORS["input_bg"], text_color=COLORS["text"], show="*")
            e.pack(side="left", fill="x", expand=True)
            
            # Strength Indicator
            strength_frame = ctk.CTkFrame(self, fg_color="transparent")
            strength_frame.pack(fill="x", padx=20, pady=(2, 10))
            
            bar = ctk.CTkProgressBar(strength_frame, height=4, width=100)
            bar.set(0)
            bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
            
            lbl_strength = ctk.CTkLabel(strength_frame, text="", font=("Segoe UI", 11))
            lbl_strength.pack(side="left")
            
            def update_strength(event=None):
                pwd = e.get()
                score, label, color = check_password_strength(pwd)
                bar.set(score / 4)
                bar.configure(progress_color=color)
                lbl_strength.configure(text=label, text_color=color)
                
            e.bind("<KeyRelease>", update_strength)
            
            def toggle():
                if e.cget("show") == "*":
                    e.configure(show="")
                else:
                    e.configure(show="*")
            
            ctk.CTkButton(frame, text="👁", width=30, fg_color=COLORS["sidebar"], 
                          text_color=COLORS["text"],
                          command=toggle).pack(side="left", padx=5)
            
            def generate():
                pwd = generate_password()
                e.delete(0, 'end')
                e.insert(0, pwd)
                e.configure(show="")
                update_strength()
                
            ctk.CTkButton(frame, text="🎲", width=30, fg_color=COLORS["warning"], 
                          text_color=COLORS["text_button"],
                          command=generate).pack(side="left")
            
        else:
            e = ctk.CTkEntry(self, fg_color=COLORS["input_bg"], text_color=COLORS["text"])
            e.pack(fill="x", padx=20)
            
        e.insert(0, default)
        e.bind("<Return>", lambda event: self.save())
        self.fields[key] = e

    def save(self):
        data = {k: v.get() for k, v in self.fields.items()}
        if not data['username'] or not data['password']:
            messagebox.showerror("Error", "Username and Password are required.")
            return
            
        try:
            if self.entry:
                self.kdbx_manager.update_entry(self.entry['id'], data)
            else:
                self.kdbx_manager.add_entry(data)
                
            self.app.load_passwords()
            
            # If editing, update details view before showing it
            if self.entry:
                fresh_entry = self.kdbx_manager.get_entry(self.entry['id'])
                if fresh_entry:
                    self.app.show_detail(fresh_entry)
            
            # Return to previous view
            # If adding, maybe go to new entry? For now just go back.
            self.cancel() 

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def cancel(self):
        # Redirect to "All Items" as requested by user to avoid blank screen issues
        self.app.switch_view('all')
