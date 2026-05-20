/* import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authError, setAuthError] = useState(null);
  const [userName, setUserName] = useState('');
  const [userRole, setUserRole] = useState('');
  const [userId, setUserId] = useState(() => localStorage.getItem('userId')); // Recuperar userId del localStorage al cargar
  const [loginAttempts, setLoginAttempts] = useState(0); // Nuevo estado para llevar el contador de intentos

  useEffect(() => {
    // Verificar si hay un token válido al cargar el componente
    const token = localStorage.getItem('token');
    const storedUserId = localStorage.getItem('userId');

    if (token && storedUserId) {
      setIsAuthenticated(true);
      setUserId(storedUserId);
    }
  }, []);

  const login = async (credentials) => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/login', credentials, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      // Si el backend devuelve un estado, lo evaluamos:
      // Por ejemplo, response.data.state puede ser "activo" o "bloqueado"
      if (response.data.state && response.data.state.toLowerCase() === 'bloqueado') {
        setAuthError('Usuario bloqueado. Comuníquese con el administrador.');
        return;
      }

      // Login correcto: reiniciamos contador de intentos y establecemos los estados
      setIsAuthenticated(true);
      setAuthError(null);
      setUserName(credentials.username);
      setUserRole(response.data.role);
      setUserId(response.data.user_id);
      setLoginAttempts(0); // Reiniciamos los intentos al iniciar sesión correctamente

      // Guardar los datos en localStorage
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('userRole', response.data.role);
      localStorage.setItem('userId', response.data.user_id);
    } catch (error) {
      // Si hay error al iniciar sesión, incrementamos el contador de intentos
      const newAttempts = loginAttempts + 1;
      setLoginAttempts(newAttempts);

      // Si el backend envía un estado de usuario bloqueado, se muestra ese mensaje
      if (error.response && error.response.data && error.response.data.state) {
        if (error.response.data.state.toLowerCase() === 'bloqueado') {
          setAuthError('Usuario bloqueado. Comuníquese con el administrador.');
          return;
        }
      }

      // Dependiendo del número de intentos fallidos se muestran mensajes diferentes
      if (newAttempts < 3) {
        setAuthError('Contraseña incorrecta. Advertencia: después de tres intentos, su usuario será bloqueado.');
      } else {
        setAuthError('Usuario bloqueado. Comuníquese con el administrador.');
      }

      setIsAuthenticated(false);
      setUserName('');
      setUserRole('');
      setUserId(null);

      // También puedes optar por limpiar los tokens si existen
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('userRole');
      localStorage.removeItem('userId');

      // Si deseas diferenciar otros tipos de error (sin respuesta del servidor, etc.)
      if (!error.response) {
        setAuthError('Error: No se recibió respuesta del servidor');
      }
    }
  };

  const logout = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No se encontró el token. Debe iniciar sesión primero.');
      }

      await axios.post('http://127.0.0.1:5000/logout', {}, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      setIsAuthenticated(false);
      setUserName('');
      setUserRole('');
      setUserId(null);
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('userRole');
      localStorage.removeItem('userId');
    } catch (error) {
      console.error('Error durante el logout:', error);
      setIsAuthenticated(false);
      setUserName('');
      setUserRole('');
      setUserId(null);
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('userRole');
      localStorage.removeItem('userId');
    }
  };

  const refreshAccessToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No se encontró el refresh token. Debe iniciar sesión nuevamente.');
      }

      const response = await axios.post('http://127.0.0.1:5000/refresh', {}, {
        headers: {
          'Authorization': `Bearer ${refreshToken}`
        }
      });

      const newAccessToken = response.data.access_token;
      localStorage.setItem('token', newAccessToken);
      return newAccessToken;
    } catch (error) {
      setIsAuthenticated(false);
      logout();
      setAuthError('No se pudo renovar el token. Debe iniciar sesión nuevamente.');
      return null;
    }
  };

  const getToken = async () => {
    let token = localStorage.getItem('token');
    if (!token) {
      token = await refreshAccessToken();
      if (!token) {
        setAuthError('La sesión ha expirado. Por favor, inicia sesión nuevamente.');
        return null;
      }
    }
    return token;
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, authError, userName, userRole, userId, login, logout, getToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext); */

 


import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(() => localStorage.getItem('isAuthenticated') === 'true');
  const [authError, setAuthError] = useState(null);
  const [userName, setUserName] = useState(() => localStorage.getItem('userName') || 'Usuario Ficticio');
  const [userRole, setUserRole] = useState(() => localStorage.getItem('userRole') || 'admin');
  const [userId, setUserId] = useState(() => localStorage.getItem('userId') || '12345');
 
  useEffect(() => {
    if (isAuthenticated) {
      localStorage.setItem('isAuthenticated', 'true');
      localStorage.setItem('userName', userName);
      localStorage.setItem('userRole', userRole);
      localStorage.setItem('userId', userId);
    }
  }, [isAuthenticated, userName, userRole, userId]);

  const login = async () => {
    setIsAuthenticated(true);
    setAuthError(null);
    setUserName('Usuario Ficticio');
    setUserRole('admin');
    setUserId('12345');
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('userName', 'Usuario Ficticio');
    localStorage.setItem('userRole', 'admin');
    localStorage.setItem('userId', '12345');
  };

  const logout = () => {
    setIsAuthenticated(false);
    setUserName('');
    setUserRole('');
    setUserId(null);
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('userName');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userId');
  };

  const getToken = async () => {
    return 'fake-token-12345'; // Token falso para pruebas
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, authError, userName, userRole, userId, login, logout, getToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext); 
