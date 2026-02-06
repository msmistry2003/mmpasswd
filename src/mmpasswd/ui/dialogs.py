import customtkinter as ctk
from .styles import COLORS

class CustomDialog(ctk.CTkToplevel):
    def __init__(self, title, message, type="info", callback=None):
        super().__init__()
        self.callback = callback
        self.result = False
        
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Center on screen
        self.update_idletasks()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (200)
        y = (hs/2) - (100)
        self.geometry('+%d+%d' % (x, y))
        
        # UI
        self.configure(fg_color=COLORS["bg"])
        
        # Icon/Color
        color = COLORS["primary"]
        icon_text = "ℹ️"
        if type == "error":
            color = COLORS["danger"]
            icon_text = "❌"
        elif type == "warning":
            color = COLORS["warning"]
            icon_text = "⚠️"
        elif type == "question":
            color = COLORS["primary"]
            icon_text = "❓"

        # Content
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icon
        ctk.CTkLabel(container, text=icon_text, font=("Segoe UI Emoji", 32)).pack(pady=(0, 10))
        
        # Message
        ctk.CTkLabel(container, text=message, font=("Segoe UI", 13), 
                     wraplength=360, text_color=COLORS["text"]).pack(pady=(0, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(pady=20) # Defaults to center anchor
        
        if type == "question":
            # Center the buttons by packing them without expanding the frame too much
            ctk.CTkButton(btn_frame, text="Yes", width=100, height=32, fg_color=COLORS["primary"],
                          text_color="#FFFFFF", font=("Segoe UI", 14, "bold"),
                          command=self.on_yes).pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="No", width=100, height=32, fg_color="transparent", border_width=1,
                          border_color=COLORS["text_dim"], text_color=COLORS["text"], font=("Segoe UI", 14, "bold"),
                          command=self.on_no).pack(side="left", padx=10)
        else:
            ctk.CTkButton(btn_frame, text="OK", width=100, height=32, fg_color=color,
                          text_color="#FFFFFF", font=("Segoe UI", 14, "bold"),
                          command=self.on_ok).pack(anchor="center")
                          
        self.grab_set()
        
    def on_ok(self):
        self.result = True
        if self.callback: self.callback(True)
        self.destroy()
        
    def on_yes(self):
        self.result = True
        if self.callback: self.callback(True)
        self.destroy()
        
    def on_no(self):
        self.result = False
        if self.callback: self.callback(False)
        self.destroy()

# Helper wrappers to mimic messagebox API
# Note: These are non-blocking by default in CTk unless we wait_window, 
# but replacing existing blocking calls requires wait_window logic.

def showinfo(title, message, parent=None):
    dlg = CustomDialog(title, message, "info")
    dlg.wait_window()
    return True

def showerror(title, message, parent=None):
    dlg = CustomDialog(title, message, "error")
    dlg.wait_window()
    return True

def showwarning(title, message, parent=None):
    dlg = CustomDialog(title, message, "warning")
    dlg.wait_window()
    return True

def askyesno(title, message, parent=None):
    dlg = CustomDialog(title, message, "question")
    dlg.wait_window()
    return dlg.result
