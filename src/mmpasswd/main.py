import os
import sys

# Ensure src is in path so imports work if run from here
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mmpasswd.ui.login import LoginWindow
from mmpasswd.ui.app import PasswordManagerApp
import customtkinter as ctk

def main():
    # Initialize Settings
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = None
    
    def start_app(security_manager):
        nonlocal app
        app = PasswordManagerApp(security_manager)
        app.mainloop()

    # Flow: Login Window -> On Success -> Main App
    
    # KDBX Manager
    kdbx_manager = None
    
    while True:
        kdbx_manager = None # Reset
        
        try:
            def on_login(mgr):
                nonlocal kdbx_manager
                kdbx_manager = mgr
                
            # Launch Login
            login_window = LoginWindow(on_login)
            login_window.mainloop()
            
            # Transition to Main App if login successful
            if kdbx_manager:
                try:
                    app = PasswordManagerApp(kdbx_manager)
                    app.mainloop()
                    # Check if lock requested (vs exit)
                    if not getattr(app, 'is_locked', False):
                        break
                except Exception as e:
                    print(f"CRITICAL APP ERROR: {e}")
                    import traceback
                    traceback.print_exc()
                    break
            else:
                # User closed login window
                break
        except Exception as e:
            print(f"MAIN LOOP ERROR: {e}")
            break

if __name__ == "__main__":
    main()
