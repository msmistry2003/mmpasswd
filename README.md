# MMPasswd - Professional Password Manager

A safe, modern, and local password manager built with Python and CustomTkinter. Designed with a sleek interface, it gives you full control over your data without cloud dependency.

## 🚀 Features

### 🔒 Security First
- **Zero-Knowledge Local Storage**: Your data lives in an encrypted `vault.kdbx` file on your machine.
- **KeePass Integration**: Uses the industry-standard KDBX format (AES-256 encryption).
- **Auto-Lock**: Automatically locks the application after inactivity (customizable).
- **Privacy Mode**: Sensitive fields are hidden by default.

### 🔑 Password Management
- **Add & Organize**: Create new passwords with ease.
- **Quick Copy**: One-click copy for usernames and passwords.
- **Search**: Instant search by website or username.
- **Favorites**: Mark your most-used services for quick access.

- **Import**: Easily migrate from other managers via CSV import (Settings > Data).

### 🎨 Modern Experience
- **Dark/Light Mode**: Choose the theme that fits your workflow.
- **Website Icons**: Automatically detects and displays icons for popular websites.
- **Password Strength**: Visual strength indicator helps you create better passwords.

## ⬇️ Download

For most users, it is recommended to use the **Standalone Installer**:
*   **[Download MMPasswd_Installer.exe](https://github.com/REPLACE_WITH_YOUR_REPO/releases/latest)** (Windows)
    *   One-click installation.
    *   Creates Desktop and Start Menu shortcuts.
    *   Includes all dependencies.

## �🛠️ Installation (Developers)

### Prerequisites
- Python 3.8+
- pip

### Setup
1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the application**:
    ```bash
    python src/mmpasswd/main.py
    ```

3.  **First Run**: You will be asked to create a **Master Password**.
    > ⚠️ **IMPORTANT**: Do not lose this password. Since your data is encrypted locally, there is no "Forgot Password" feature.

## 📂 Project Structure

```
.
├── src/                # Application Source
│   ├── mmpasswd/       # Core package
│   │   ├── core/       # Logic (Crypto, DB)
│   │   ├── ui/         # Interface (Windows, Styles)
│   │   └── main.py     # Entry Point
├── requirements.txt    # Dependencies
├── normal.png          # App Branding
└── README.md           # Documentation
```

## ⚙️ Tech Stack
- **UI**: CustomTkinter
- **Security**: PyKeePass, Cryptography (Fernet/AES)
- **Database**: KDBX (KeePass Format)
