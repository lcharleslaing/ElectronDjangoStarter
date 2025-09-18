import { contextBridge, ipcRenderer } from 'electron';

// Minimal preload for security - no node APIs exposed to renderer
contextBridge.exposeInMainWorld('electronAPI', {
    platform: process.platform,
    closeApp: () => ipcRenderer.send('app:quit'),
});

// Type declaration for renderer
declare global {
    interface Window {
        electronAPI: {
            platform: string;
            closeApp: () => void;
        };
    }
}
