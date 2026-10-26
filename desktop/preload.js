// Tells pages they are running inside the desktop app (the download page shows the installed version). Nothing else is exposed.
const { contextBridge } = require('electron');
const arg = (process.argv || []).find(a => a.startsWith('--adamas-version=')) || '';
contextBridge.exposeInMainWorld('adamasDesktop', { version: arg.split('=')[1] || '', platform: process.platform });
