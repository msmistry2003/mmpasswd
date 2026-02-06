import customtkinter as ctk
from tkinter import filedialog
from . import dialogs as messagebox
import csv
from .styles import COLORS, THEMES
from ..core.import_export import ImportExportManager

class SettingsView(ctk.CTkScrollableFrame):
    def __init__(self, parent, kdbx_manager, app_instance):
        super().__init__(parent, fg_color="transparent")
        self.kdbx_manager = kdbx_manager
        self.app = app_instance # Reference to main app for callbacks
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header with Back Button
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20)) # Removed padx=20 to match main view alignment
        
        ctk.CTkButton(header_frame, text="←", width=40, 
                    fg_color="transparent", hover_color=COLORS["input_bg"],
                    text_color=COLORS["text"], font=("Segoe UI", 16, "bold"),
                    command=lambda: self.app.switch_view('all', is_back=True)).pack(side="left")
                    
        ctk.CTkLabel(header_frame, text="Settings", font=("Segoe UI", 24, "bold"), 
                   text_color=COLORS["text"]).pack(side="left", padx=10)

        # --- Appearance ---
        self.create_section("Appearance")
        
        # Theme Title
        theme_frame = ctk.CTkFrame(self, fg_color=COLORS["input_bg"])
        theme_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(theme_frame, text="Theme", font=("Segoe UI", 14, "bold"), 
                     text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(15, 5))
        
        current_theme = getattr(self.app, 'current_theme', 'Dark')
        self.theme_var = ctk.StringVar(value=current_theme)
        
        seg_button = ctk.CTkSegmentedButton(theme_frame, values=["Dark", "Light"],
                                            command=self.app.apply_theme,
                                            height=30, # Reduced from 40
                                            width=300, # Constrained width
                                            font=("Segoe UI", 12, "bold"),
                                            selected_color=COLORS["primary"],
                                            selected_hover_color=COLORS["primary_hover"])
        seg_button.set(current_theme)
        seg_button.pack(padx=20, pady=(0, 20)) # Removed fill="x" to make it smaller/centered

        # --- Security ---
        self.create_section("Security")
        
        sec_frame = ctk.CTkFrame(self, fg_color=COLORS["input_bg"])
        sec_frame.pack(fill="x", pady=(0, 20))
        
        # Auto Lock
        ctk.CTkLabel(sec_frame, text="Auto-Lock Timeout", font=("Segoe UI", 14, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(sec_frame, text="Lock the app after seconds of inactivity", text_color=COLORS["text_dim"]).pack(anchor="w", padx=20)
        
        self.timeout_entry = ctk.CTkEntry(sec_frame, fg_color=COLORS["bg"], text_color=COLORS["text"], width=100)
        self.timeout_entry.pack(anchor="w", padx=20, pady=10)
        self.timeout_entry.insert(0, str(self.app.lock_timeout))
        
        ctk.CTkButton(sec_frame, text="Update", fg_color=COLORS["primary"], 
                      text_color=COLORS["text_button"],
                      command=self.update_timeout).pack(anchor="w", padx=20, pady=(0, 20))

        # --- Data ---
        self.create_section("Data Management")
        
        data_frame = ctk.CTkFrame(self, fg_color=COLORS["input_bg"])
        data_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(data_frame, text="Import Passwords", font=("Segoe UI", 14, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(data_frame, text="Import data from a simplified CSV file.", text_color=COLORS["text_dim"]).pack(anchor="w", padx=20)
        
        ctk.CTkButton(data_frame, text="📥 Import from CSV", fg_color=COLORS["sidebar"],
                      text_color=COLORS["text"], 
                      border_width=1, border_color=COLORS["text_dim"],
                      command=self.import_data).pack(anchor="w", padx=20, pady=20)

    def create_section(self, title):
        ctk.CTkLabel(self, text=title, font=("Segoe UI", 18, "bold"), text_color=COLORS["text_dim"]).pack(anchor="w", pady=(10, 5))

    def change_theme(self, theme_name):
        self.app.apply_theme(theme_name)

    def update_timeout(self):
        try:
            val = int(self.timeout_entry.get())
            if val < 5:
                messagebox.showerror("Error", "Timeout too short (min 5s)")
                return
            self.app.lock_timeout = val
            self.app.reset_lock_timer()
            
            # Persist to DB
            self.kdbx_manager.set_config("lock_timeout", val)
            
            messagebox.showinfo("Success", "Auto-Lock timeout updated.")
        except ValueError:
             messagebox.showerror("Error", "Invalid number")

    def import_data(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filename:
            try:
                count = ImportExportManager.import_csv(self.kdbx_manager, filename)
                messagebox.showinfo("Success", f"Imported {count} passwords.")
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {e}")
