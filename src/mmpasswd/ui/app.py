import customtkinter as ctk
from . import dialogs as messagebox
import os
from datetime import datetime
from .styles import COLORS, get_website_icon, THEMES
from ..core.utils import generate_password, secure_copy, check_password_strength
from .settings_view import SettingsView
from .edit_view import EditView

class PasswordManagerApp(ctk.CTk):
    def __init__(self, kdbx_manager):
        super().__init__()
        
        self.kdbx_manager = kdbx_manager
        
        # Set Icon
        import sys
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = "D:\\cyber\\mmpasswd"
            
        icon_path = os.path.join(base_path, "app.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(default=icon_path)
        elif os.path.exists("app.ico"):
             self.iconbitmap(default="app.ico")
        
        # Load Theme
        # 1. Try local config (for login screen)
        import json
        self.local_config_file = os.path.abspath("config.json")
        saved_theme = "Dark"
        
        # Debug print
        # Debug print removed
        
        try:
            if os.path.exists(self.local_config_file):
                with open(self.local_config_file, 'r') as f:
                    data = json.load(f)
                    saved_theme = data.get("theme", "Dark")
                    pass
        except Exception as e:
            pass
        
        self.current_theme = saved_theme
        # Validate entry
        if self.current_theme not in THEMES:
            self.current_theme = "Dark"
            
        # Applying startup theme
        self.apply_theme(self.current_theme, first_run=True)
        
        self.current_view = "all"
        self.selected_id = None
        
        try:
            # Auto-Lock
            saved_timeout = self.kdbx_manager.get_config("lock_timeout")
            self.lock_timeout = int(saved_timeout) if saved_timeout else 300
        except Exception as e:
            pass
            self.lock_timeout = 300
            
        self.lock_timer = None
        
        self.setup_ui()
        self.load_passwords()
        
        # Start timer AFTER UI is ready
        self.bind_all("<Any-KeyPress>", self.reset_lock_timer)
        self.bind_all("<Any-ButtonPress>", self.reset_lock_timer)
        self.reset_lock_timer()

    def reset_lock_timer(self, event=None):
        if not self.winfo_exists(): return
        if self.lock_timer:
            self.after_cancel(self.lock_timer)
        self.lock_timer = self.after(self.lock_timeout * 1000, self.lock_app)
    
    def lock_app(self):
        if not self.winfo_exists(): return
        self.is_locked = True
        # Close any open dialogs (toplevels)
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkToplevel):
                widget.destroy()
                
        self.destroy()
        # Main.py loop will end? No, main.py logic needs to handle re-login.
        # Main.py logic:
        # login -> app -> destroy -> END
        # We need a way to restart login.
        # The clean way: app returns a status code?
        # Or main.py runs a loop: while True: login(); if success: app(); else: break
        pass 
        
    def setup_ui(self):
        self.title("MMPasswd - Password Manager")
        self.geometry("1100x700")
        self.configure(fg_color=COLORS["bg"])
        
        # Maximize
        self.after(100, lambda: self.state('zoomed'))

        # Main Layout
        self.main_container = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        self.main_container.pack(fill="both", expand=True)

        self.create_sidebar()
        self.create_content_area()

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self.main_container, fg_color=COLORS["sidebar"], width=280, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Header
        ctk.CTkLabel(sidebar, text="👤 MMPasswd", font=("Segoe UI", 20, "bold")).pack(pady=(30, 5), padx=20, anchor="w")
        ctk.CTkLabel(sidebar, text="Secure Vault", font=("Segoe UI", 12), text_color=COLORS["text_dim"]).pack(padx=20, anchor="w")

        # New Item Button
        ctk.CTkButton(sidebar, text="+ New Item", font=("Segoe UI", 13, "bold"),
                     fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                     text_color=COLORS["text_button"],
                     command=self.open_add_dialog).pack(pady=20, padx=20, fill="x")

        # Navigation
        self.nav_buttons = {}
        # Cleaned up views for KDBX simplicity, though 'deleted'
        nav_items = [
            ("all", "📋 All Items"),
            ("favorites", "⭐ Favorites"),
            ("deleted", "🗑 Recently Deleted")
        ]

        for view_id, label in nav_items:
            btn = ctk.CTkButton(sidebar, text=label, fg_color="transparent", anchor="w",
                              hover_color=COLORS["input_bg"], height=40,
                              font=("Segoe UI", 13, "bold"), # Bold for visibility
                              text_color=COLORS["text"],
                              command=lambda v=view_id: self.switch_view(v))
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[view_id] = btn

        # Settings Link (Bottom)
        btn = ctk.CTkButton(sidebar, text="⚙️ Settings", fg_color="transparent", anchor="w",
                      hover_color=COLORS["input_bg"], height=32,
                      font=("Segoe UI", 13, "bold"), 
                      text_color=COLORS["text"],
                      command=lambda: self.switch_view('settings'))
        btn.pack(side="bottom", fill="x", padx=10, pady=20)
        self.nav_buttons['settings'] = btn

    def create_content_area(self):
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Search Frame (Back Button + Search)
        self.search_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["input_bg"], height=40)
        self.search_frame.pack(fill="x", pady=(0, 20))
        
        # Back Button
        self.back_btn = ctk.CTkButton(self.search_frame, text="←", width=40, 
                                    fg_color="transparent", hover_color=COLORS["sidebar"],
                                    text_color=COLORS["text"], font=("Segoe UI", 16, "bold"),
                                    command=self.go_back)
        self.back_btn.pack(side="left", padx=(5, 0), pady=2)
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search passwords...",
                                       fg_color="transparent", border_width=0, text_color=COLORS["text"])
        self.search_entry.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_passwords())

        # Split View (List + Detail)
        self.split_view = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.split_view.pack(fill="both", expand=True)

        # Navigation History
        self.view_history = []
        self.is_navigating_back = False
        
        # List
        self.list_frame = ctk.CTkScrollableFrame(self.split_view, fg_color=COLORS["input_bg"], width=300)
        self.list_frame.pack(side="left", fill="both", padx=(0, 20))

        # Detail
        self.detail_frame = ctk.CTkFrame(self.split_view, fg_color=COLORS["input_bg"])
        self.detail_frame.pack(side="right", fill="both", expand=True)
        self.show_empty_detail()

    def go_back(self):
        if self.view_history:
            prev_view = self.view_history.pop()
            self.switch_view(prev_view, is_back=True)
        else:
            # Fallback if history empty (e.g. startup) -> All Items
            if self.current_view != 'all':
                self.switch_view('all', is_back=True)

    def switch_view(self, view_id, is_back=False):
        # Push to history if not going back and not refreshing same view
        # Exclude 'edit' from history to avoid blank screens/state issues
        if not is_back and view_id != self.current_view and view_id != 'edit':
            self.view_history.append(self.current_view)
            # Limit history
            if len(self.view_history) > 10:
                self.view_history.pop(0)

        self.current_view = view_id
        
        # Reset UI (Hide everything first)
        self.split_view.pack_forget()
        if hasattr(self, 'settings_view'):
            self.settings_view.pack_forget()
        if hasattr(self, 'edit_view'):
            self.edit_view.pack_forget()
        if hasattr(self, 'search_frame'):
            self.search_frame.pack_forget()
        
        # Highlight logic
        for vid, btn in self.nav_buttons.items():
            is_active = (vid == view_id)
            btn.configure(fg_color=COLORS["input_bg"] if is_active else "transparent")
            
        # Logic for views
        if view_id == 'settings':
            if not hasattr(self, 'settings_view') or not self.settings_view.winfo_exists():
                self.settings_view = SettingsView(self.content_frame, self.kdbx_manager, self)
            self.settings_view.pack(fill="both", expand=True)
            
        elif view_id == 'edit':
            # Edit view logic is handled by show_edit_view mostly, but if we switch back?
            # usually we don't switch TO edit from sidebar, but if we did:
             pass
             
        else:
            # Standard List Views (All, Favorites, Deleted)
            # 1. Pack Search
            if hasattr(self, 'search_frame'):
                self.search_frame.pack(fill="x", pady=(0, 20))
                
            # 2. Pack Split View
            self.split_view.pack(fill="both", expand=True)
            
            self.load_passwords()
            self.show_empty_detail()

    def load_passwords(self):
        # Clear list
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        search_query = self.search_entry.get().strip()
        
        for entry in self.kdbx_manager.get_search_results(self.current_view, search_query if search_query else None):
            self.create_list_item(entry)

    def create_list_item(self, entry):
        display_name = entry.get('website') or entry.get('username') or "Untitled"
        icon = get_website_icon(display_name)
        
        # Add Star if favorite
        if entry.get('is_favorite', 0) == 1:
            display_name += " ⭐"
        
        btn = ctk.CTkButton(self.list_frame, 
                          text=f"{icon}  {display_name}\n      {entry['username']}", 
                          fg_color="transparent", hover_color=COLORS["sidebar"],
                          anchor="w", height=60,
                          text_color=COLORS["text"],
                          command=lambda: self.show_detail(entry))
        btn.pack(fill="x", pady=1)

    def show_empty_detail(self):
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.detail_frame, text="Select an item to view details", 
                    text_color=COLORS["text_dim"]).pack(expand=True)
        self.selected_id = None

    def show_detail(self, entry):
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
        
        self.selected_id = entry['id']
        
        # Password is now directly available via KDBX manager (decrypted)
        password = entry['password']

        # Header
        header = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=30)
        
        display_name = entry.get('website') or entry.get('username') or "Untitled"
        icon = get_website_icon(display_name)
        ctk.CTkLabel(header, text=icon, font=("Segoe UI", 48)).pack(side="left", padx=(0, 20))
        
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", fill="x")
        ctk.CTkLabel(title_box, text=display_name, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        ctk.CTkLabel(title_box, text=entry['username'], text_color=COLORS["text_dim"]).pack(anchor="w")

        # Actions
        if self.current_view == 'deleted':
             self.create_deleted_actions(header, entry)
        else:
             self.create_normal_actions(header, entry)

        # Fields
        fields_frame = ctk.CTkScrollableFrame(self.detail_frame, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=20)
        
        self.add_field(fields_frame, "Username", entry['username'])
        self.add_field(fields_frame, "Password", "•" * len(password) if password else "", 
                      copy_val=password, is_password=True)
        self.add_field(fields_frame, "Website", entry['website'], link=True)
        self.add_field(fields_frame, "Notes", entry['notes'])

    def add_field(self, parent, label, value, copy_val=None, is_password=False, link=False):
        if not value and not is_password: return
        
        f = ctk.CTkFrame(parent, fg_color=COLORS["sidebar"], corner_radius=6)
        f.pack(fill="x", pady=5)
        
        ctk.CTkLabel(f, text=label, font=("Segoe UI", 13, "bold"), text_color=COLORS["text_dim"]).pack(anchor="w", padx=15, pady=(10,0))
        
        val_frame = ctk.CTkFrame(f, fg_color="transparent")
        val_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        val_lbl = ctk.CTkLabel(val_frame, text=value, font=("Segoe UI", 16), text_color=COLORS["text"])
        val_lbl.pack(side="left")
        
        # Strength Indicator for Details
        if is_password:
             strength_frame = ctk.CTkFrame(f, fg_color="transparent")
             strength_frame.pack(fill="x", padx=15, pady=(0, 10))
             
             bar = ctk.CTkProgressBar(strength_frame, height=4, width=150)
             bar.pack(side="left", padx=(0, 10))
             
             lbl_strength = ctk.CTkLabel(strength_frame, text="", font=("Segoe UI", 11))
             lbl_strength.pack(side="left")
             
             # Calculate once
             score, label, color = check_password_strength(copy_val if copy_val else "")
             bar.set(score / 4)
             bar.configure(progress_color=color)
             lbl_strength.configure(text=label, text_color=color)
        
        if copy_val or is_password:
            def copy():
                if is_password:
                    secure_copy(copy_val if copy_val else value)
                    messagebox.showinfo("Secure Copy", f"{label} copied! Will clear in 30s.")
                else:
                    self.clipboard_clear()
                    self.clipboard_append(copy_val if copy_val else value)
                    messagebox.showinfo("Copied", f"{label} copied!")

            ctk.CTkButton(val_frame, text="Copy", width=50, height=24, fg_color=COLORS["primary"],
                        command=copy).pack(side="right")
            
            if is_password:
                # Eye Toggle for Detail View
                def toggle_visibility():
                    if val_lbl.cget("text").startswith("•"):
                        val_lbl.configure(text=copy_val)
                    else:
                        val_lbl.configure(text="•" * len(copy_val))
                
                ctk.CTkButton(val_frame, text="👁", width=30, height=24, fg_color=COLORS["sidebar"],
                            command=toggle_visibility).pack(side="right", padx=5)

    def create_normal_actions(self, parent, entry):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(side="right", anchor="n")
        
        # Edit
        ctk.CTkButton(btn_frame, text="✎", width=40, fg_color=COLORS["sidebar"], 
                    command=lambda: self.open_edit_dialog(entry)).pack(side="left", padx=5)
        
        # Favorite
        is_fav = entry['is_favorite'] == 1
        fav_color = COLORS["warning"] if is_fav else COLORS["sidebar"]
        ctk.CTkButton(btn_frame, text="⭐", width=40, fg_color=fav_color,
                    command=lambda: self.toggle_favorite(entry)).pack(side="left", padx=5)

        # Delete
        ctk.CTkButton(btn_frame, text="🗑", width=40, fg_color=COLORS["danger"],
                    command=lambda: self.delete_entry(entry)).pack(side="left", padx=5)

    def create_deleted_actions(self, parent, entry):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(side="right", anchor="n")
        
        # Restore Button (Icon + Text, cleaner look)
        ctk.CTkButton(btn_frame, text="Restore", fg_color=COLORS["success"], 
                      text_color=COLORS["text_button"], width=80, height=30,
                      command=lambda: self.restore_entry_action(entry)).pack(side="left", padx=5)
        
        # Delete Forever (Outline style for less visual noise until hovered, or just red)
        # Making it red outline or cleaner red button
        ctk.CTkButton(btn_frame, text="Delete", fg_color="transparent", 
                      border_width=1, border_color=COLORS["danger"],
                      text_color=COLORS["danger"], hover_color=COLORS["input_bg"],
                      width=80, height=30,
                      command=lambda: self.hard_delete_entry(entry)).pack(side="left", padx=5)

    # --- Actions ---
    
    def toggle_favorite(self, entry):
        current_val = int(entry.get('is_favorite', 0))
        new_val = 0 if current_val == 1 else 1
        
        self.kdbx_manager.update_entry(entry['id'], {'is_favorite': new_val})
        
        self.load_passwords()
        
        if self.selected_id == entry['id']:
            fresh_entry = self.kdbx_manager.get_entry(entry['id'])
            if fresh_entry:
                self.show_detail(fresh_entry)

    def delete_entry(self, entry):
        if messagebox.askyesno("Delete", "Move to trash?"):
            self.kdbx_manager.delete_entry(entry['id'])
            self.load_passwords()
            self.show_empty_detail()

    def restore_entry_action(self, entry):
        self.kdbx_manager.restore_entry(entry['id'])
        self.load_passwords()
        self.show_empty_detail()
        messagebox.showinfo("Restored", "Item restored to All Items.")

    def hard_delete_entry(self, entry):
        if messagebox.askyesno("Delete Forever", "This action cannot be undone."):
            self.kdbx_manager.delete_entry(entry['id'], soft=False)
            self.load_passwords()
            self.show_empty_detail()

    # --- Dialogs ---

    # --- Dialogs / Views ---

    def apply_theme(self, theme_name, first_run=False):
        if theme_name in THEMES:
            self.current_theme = theme_name
            
            # Save to DB
            if not first_run:
                self.kdbx_manager.set_config("theme", theme_name)
                
            # Save to Local Config (for Login Screen)
            import json
            try:
                with open(self.local_config_file, 'w') as f:
                    json.dump({"theme": theme_name}, f)
            except: pass
                
            theme = THEMES[theme_name]
            ctk.set_appearance_mode(theme["mode"])
            COLORS.clear()
            COLORS.update(theme["colors"])
            
            # If first run, don't destroy UI as it's not built yet or handled by init
            if first_run:
                return

            # Clear references
            if hasattr(self, 'settings_view'): del self.settings_view
            if hasattr(self, 'edit_view'): del self.edit_view
                
            self.main_container.destroy()
            self.main_container = ctk.CTkFrame(self, fg_color=COLORS["bg"])
            self.main_container.pack(fill="both", expand=True)
            self.create_sidebar()
            self.create_content_area()
            
            # Restore view
            if self.current_view in ['settings', 'edit']:
                # Edit state might be lost, just go back to settings or list
                if self.current_view == 'edit': 
                    self.switch_view('all')
                else:
                    self.switch_view(self.current_view)
            else:
                self.switch_view(self.current_view)

    def open_add_dialog(self):
        self.show_edit_view(None)

    def open_edit_dialog(self, entry):
        self.show_edit_view(entry)

    def show_edit_view(self, entry):
        # Determine password to pre-fill
        pwd = ""
        if entry:
            pwd = entry['password'] # Already accessible
            
        self.switch_view('edit')
        
        # Create/Update Edit View
        if hasattr(self, 'edit_view'):
            self.edit_view.destroy()
            
        self.edit_view = EditView(self.content_frame, self.kdbx_manager, self, entry, pwd)
        self.edit_view.pack(fill="both", expand=True)
