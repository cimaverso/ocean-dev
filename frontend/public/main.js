const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');

const createWindow = async () => {
  const { default: isDev } = await import('electron-is-dev');

  const mainWindow = new BrowserWindow({
    minWidth: 1200,
    height: 810, 
    titleBarStyle: 'Ocean Coal',
    icon: path.join(__dirname, '..', 'src', 'assets', 'app_icon.ico'),    
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),      
      nodeIntegration: false,       
      experimentalFeatures: true,
      contextIsolation: true,     
    }    
  })  

  mainWindow.on('close', (event) => {
    event.preventDefault(); // Prevenir el cierre de la ventana
    mainWindow.webContents.send('app-logout'); // Enviar un mensaje al renderer
  });

  const startUrl = isDev
    ? 'http://localhost:3000'  // En modo desarrollo, cargamos la app React
    : `file://${path.join(__dirname, '..', 'src', 'index.js')}`;

  mainWindow.loadURL(startUrl);
};

 const emptyMenu = Menu.buildFromTemplate([]);
  Menu.setApplicationMenu(emptyMenu); 

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

