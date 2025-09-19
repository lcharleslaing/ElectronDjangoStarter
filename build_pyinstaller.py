#!/usr/bin/env python3
"""
Build script for creating a standalone .exe using PyInstaller.
Creates a single executable that bundles Django + Electron.
"""
import os
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
