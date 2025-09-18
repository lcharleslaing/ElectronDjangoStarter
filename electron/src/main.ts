import { app, BrowserWindow, shell, ipcMain } from 'electron';
import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import * as dotenv from 'dotenv';
import treeKill from 'tree-kill';

// Load environment variables
dotenv.config();

const DJANGO_PORT = process.env.ELECTRON_DJANGO_PORT || process.env.DEV_PORT || '8111';
const DJANGO_URL = `http://127.0.0.1:${DJANGO_PORT}`;

let mainWindow: BrowserWindow | null = null;
let djangoProcess: ChildProcess | null = null;

function createWindow(): void {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        fullscreen: false,
        fullscreenable: true,
        resizable: true,
        frame: true,
        title: 'Django + Electron Starter',
        autoHideMenuBar: true,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        show: false
    });

    mainWindow.once('ready-to-show', () => {
        // Maximize to give full-screen feel while preserving native window controls (close/minimize)
        mainWindow?.maximize();
        mainWindow?.show();
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });
}

async function waitForDjango(): Promise<void> {
    const maxRetries = 30;
    const retryDelay = 1000;

    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(`${DJANGO_URL}/api/health/`);
            if (response.ok) {
                console.log('Django is ready');
                return;
            }
        } catch (error) {
            console.log(`Waiting for Django... (${i + 1}/${maxRetries})`);
        }
        await new Promise(resolve => setTimeout(resolve, retryDelay));
    }
    throw new Error('Django failed to start within timeout');
}

function startDjango(): void {
    const backendPath = path.join(__dirname, '../../backend');
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

    console.log('Starting Django...');
    djangoProcess = spawn(pythonCmd, ['manage.py', 'runserver', `127.0.0.1:${DJANGO_PORT}`], {
        cwd: backendPath,
        stdio: 'pipe'
    });

    djangoProcess.stdout?.on('data', (data) => {
        console.log(`Django: ${data}`);
    });

    djangoProcess.stderr?.on('data', (data) => {
        console.error(`Django error: ${data}`);
    });

    djangoProcess.on('error', (error) => {
        console.error('Failed to start Django:', error);
    });
}

async function saveWindowBounds(): Promise<void> {
    if (!mainWindow) return;

    try {
        const bounds = mainWindow.getBounds();
        const isMaximized = mainWindow.isMaximized();
        const windowData = {
            x: bounds.x,
            y: bounds.y,
            width: bounds.width,
            height: bounds.height,
            isMaximized
        };

        const response = await fetch(`${DJANGO_URL}/api/preferences/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ window_bounds: windowData })
        });

        if (!response.ok) {
            console.warn('Failed to save window bounds');
        }
    } catch (error) {
        console.warn('Error saving window bounds:', error);
    }
}

app.whenReady().then(async () => {
    startDjango();
    await waitForDjango();
    createWindow();

    if (mainWindow) {
        mainWindow.loadURL(DJANGO_URL);
    }
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

app.on('before-quit', async () => {
    await saveWindowBounds();

    if (djangoProcess) {
        console.log('Stopping Django...');
        treeKill(djangoProcess!.pid as number, 'SIGTERM', (err?: Error) => {
            if (err) {
                console.error('Error stopping Django:', err);
            }
        });
    }
});

// Renderer requests to quit app
ipcMain.on('app:quit', () => {
    app.quit();
});
