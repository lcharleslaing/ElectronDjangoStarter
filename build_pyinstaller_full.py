#!/usr/bin/env python3
"""
Full PyInstaller build script for creating a standalone .exe.
"""
import os
import sys
import subprocess
import threading
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"

def run(cmd):
    """Run a command and return exit code."""
    return subprocess.call(cmd, shell=True)

def ensure_django_ready():
    """Ensure Django is ready and return Python executable."""
    print("Installing backend requirements ...")
    code = run("pip install -r backend/requirements.txt")
    if code != 0:
        print("Failed to install requirements", file=sys.stderr)
        sys.exit(code)
    
    print("Applying migrations ...")
    code = run("python backend/manage.py migrate")
    if code != 0:
        print("Migrations failed", file=sys.stderr)
        sys.exit(code)
    
    return Path(sys.executable)

def install_pyinstaller(python_exe: Path) -> None:
    """Install PyInstaller if not already installed."""
    try:
        subprocess.check_output([str(python_exe), "-c", "import PyInstaller"], stderr=subprocess.DEVNULL)
        print("PyInstaller already installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("PyInstaller not found. Installing PyInstaller ...")
        code = run([str(python_exe), "-m", "pip", "install", "pyinstaller"])
        if code != 0:
            print("Failed to install PyInstaller", file=sys.stderr)
            sys.exit(code)
        print("PyInstaller installed successfully.")

def create_main_script() -> Path:
    """Create a main.py script that starts Django and Electron."""
    main_script = PROJECT_ROOT / "main.py"
    content = '''import os
import sys
import subprocess
import threading
import time
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
electron_path = Path(__file__).parent / "electron"
sys.path.insert(0, str(backend_path))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def start_django():
    """Start Django in a separate thread."""
    try:
        import django
        from django.core.management import execute_from_command_line
        django.setup()
        
        # Run migrations
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Start server
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8111'])
    except Exception as e:
        print(f"Django error: {e}")
        input("Press Enter to exit...")

def wait_for_django_and_start_electron():
    """Wait for Django to be ready, then start Electron."""
    import urllib.request
    import urllib.error
    
    for i in range(30):
        try:
            with urllib.request.urlopen('http://127.0.0.1:8111/api/health/', timeout=2) as resp:
                if resp.status == 200:
                    print("Django is ready! Starting Electron...")
                    start_electron()
                    return
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            pass
        time.sleep(1)
    print("Django failed to start within 30 seconds")

def start_electron():
    """Start Electron application."""
    try:
        # Create main.js for Electron
        main_js = electron_path / "main.js"
        main_js_content = """const { app, BrowserWindow } = require('electron');

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true
        }
    });

    mainWindow.loadURL('http://127.0.0.1:8111');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});"""
        main_js.write_text(main_js_content)
        
        # Find electron executable
        possible_paths = [
            electron_path / "electron.exe",
            electron_path / "node_modules" / ".bin" / "electron.exe",
            electron_path / "node_modules" / "electron" / "dist" / "electron.exe",
            Path("electron.exe"),
            Path("electron")
        ]
        
        electron_exe = None
        for path in possible_paths:
            if path.exists():
                electron_exe = path
                break
        
        if not electron_exe:
            print("No Electron found. Installing...")
            try:
                subprocess.run(["npm", "install", "electron"], cwd=electron_path, check=True)
                print("Electron installed successfully")
                
                # Try again
                for path in possible_paths:
                    if path.exists():
                        electron_exe = path
                        break
            except Exception as e:
                print(f"Failed to install Electron: {e}")
                return
        
        if electron_exe:
            print(f"Starting Electron: {electron_exe}")
            process = subprocess.Popen(
                [str(electron_exe), str(main_js)], 
                cwd=electron_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(3)
            
            if process.poll() is None:
                print("Electron started successfully!")
            else:
                stdout, stderr = process.communicate()
                print(f"Electron failed. stdout: {stdout.decode()}")
                print(f"Electron failed. stderr: {stderr.decode()}")
        else:
            print("No Electron executable found!")
        
    except Exception as e:
        print(f"Error starting Electron: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting Django + Electron Starter...")
    
    # Start Django in background thread
    django_thread = threading.Thread(target=start_django, daemon=True)
    django_thread.start()
    
    # Wait for Django and start Electron
    wait_for_django_and_start_electron()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\nShutting down...")
'''
    
    with open(main_script, 'w') as f:
        f.write(content)
    
    return main_script

def build_exe(python_exe: Path, main_script: Path, app_name: str) -> Path:
    """Build the .exe using PyInstaller."""
    print(f"Building .exe with PyInstaller as '{app_name}'...")
    
    # PyInstaller command
    cmd = [
        str(python_exe), "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        f"--name={app_name}",
        "--add-data=backend;backend",
        "--add-data=electron;electron",
        "--hidden-import=django",
        "--hidden-import=config",
        "--hidden-import=accounts",
        "--hidden-import=preferences", 
        "--hidden-import=projects",
        str(main_script)
    ]
    
    code = run(cmd)
    if code != 0:
        print("PyInstaller build failed", file=sys.stderr)
        sys.exit(code)
    
    exe_path = DIST_DIR / f"{app_name}.exe"
    if exe_path.exists():
        return exe_path
    else:
        print(f"Expected .exe not found at {exe_path}", file=sys.stderr)
        sys.exit(1)

def pick_directory() -> Path:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        directory = filedialog.askdirectory(title="Select directory for shortcut")
        root.destroy()
        if directory:
            return Path(directory)
        else:
            print("No directory selected. Aborting.")
            sys.exit(1)
    except ImportError:
        print("tkinter not available. Please install it or specify directory manually.")
        sys.exit(1)

def create_shortcut(shortcut_path: Path, target_path: Path, icon_path: Path = None):
    """Create a Windows shortcut."""
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(target_path)
        if icon_path:
            shortcut.IconLocation = str(icon_path)
        shortcut.save()
    except ImportError:
        print("pywin32 not available. Install it with: pip install pywin32")
        sys.exit(1)

def delete_shortcut(shortcut_path: Path):
    """Delete a shortcut file."""
    try:
        if shortcut_path.exists():
            shortcut_path.unlink()
            print(f"Deleted shortcut: {shortcut_path}")
    except Exception as exc:
        print(f"Failed to delete shortcut {shortcut_path}: {exc}", file=sys.stderr)

def main() -> None:
    if os.name != "nt":
        print("This helper is intended for Windows (.exe build).")
        sys.exit(1)

    # Ask for app name first
    try:
        app_name = input("Enter App name (e.g., MyApp): ").strip()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
    if not app_name:
        app_name = "DjangoElectronStarter"

    # Pick destination directory for the shortcut
    print("Select directory to save the app shortcut:")
    dest_dir = pick_directory()

    # Prepare backend
    python_exe = ensure_django_ready()
    install_pyinstaller(python_exe)
    
    # Create main script
    main_script = create_main_script()
    
    # Build .exe with custom name
    exe_path = build_exe(python_exe, main_script, app_name)
    
    # Copy electron files to dist directory
    print("Copying Electron files to dist directory...")
    electron_src = PROJECT_ROOT / "electron"
    electron_dst = DIST_DIR / "electron"
    
    if electron_dst.exists():
        import shutil
        shutil.rmtree(electron_dst)
    
    import shutil
    shutil.copytree(electron_src, electron_dst)
    print("Electron files copied successfully.")

    # Create shortcut
    shortcut = dest_dir / f"{app_name}.lnk"

    # Check if shortcut already exists
    if shortcut.exists():
        try:
            overwrite = input(f"Shortcut already exists at {shortcut}. Overwrite? (y/N): ").strip().lower()
            if overwrite in ('y', 'yes'):
                delete_shortcut(shortcut)
            else:
                print("Skipping shortcut creation.")
                return
        except KeyboardInterrupt:
            print("\nAborted.")
            sys.exit(1)

    print(f"Creating shortcut: {shortcut}")
    create_shortcut(shortcut, exe_path, icon_path=exe_path)
    print("Done.")
    print(f"Shortcut created at: {shortcut}")
    print(f"Executable created at: {exe_path}")

if __name__ == "__main__":
    main()
