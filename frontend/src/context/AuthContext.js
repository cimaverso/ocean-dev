/**
 * AuthContext.js — Contexto de autenticación
 * Proyecto Ocean — Sistema de pesaje
 *
 * Contrato de contexto (no cambiar nombres — App.js y componentes dependen):
 *   isAuthenticated, authError, userName, userRole, userId,
 *   login(credentials), logout(), getToken()
 */

import React, { createContext, useContext, useState, useEffect } from "react";
import { authAPI } from "../api/api";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authError, setAuthError]             = useState(null);
  const [userName, setUserName]               = useState("");
  const [userRole, setUserRole]               = useState("");
  const [userId, setUserId]                   = useState(null);
  const [loginAttempts, setLoginAttempts]     = useState(0);
  const [isLoading, setIsLoading]             = useState(true);

  // ── Restaurar sesión al recargar ──────────────────────────────────────────
  useEffect(() => {
    const token   = localStorage.getItem("token");
    const storedUserId   = localStorage.getItem("userId");
    const storedUserName = localStorage.getItem("userName");
    const storedUserRole = localStorage.getItem("userRole");

    if (token && storedUserId) {
      setIsAuthenticated(true);
      setUserId(storedUserId);
      setUserName(storedUserName || "");
      setUserRole(storedUserRole || "");
    }

    setIsLoading(false);
  }, []);

  // ── Helpers ───────────────────────────────────────────────────────────────

  const persistSession = (data) => {
    localStorage.setItem("token",         data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    localStorage.setItem("userRole",      data.role);
    localStorage.setItem("userId",        data.user_id);
    localStorage.setItem("userName",      data.username ?? "");
  };

  const clearSession = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("userRole");
    localStorage.removeItem("userId");
    localStorage.removeItem("userName");
  };

  const resetAuthState = () => {
    setIsAuthenticated(false);
    setUserName("");
    setUserRole("");
    setUserId(null);
  };

  // ── login ─────────────────────────────────────────────────────────────────

  const login = async (credentials) => {
    setAuthError(null);

    try {
      const response = await authAPI.login(credentials);
      const data     = response.data;

      // Backend puede devolver usuario bloqueado con status 200
      if (data.state && data.state.toLowerCase() === "bloqueado") {
        setAuthError("Usuario bloqueado. Comuníquese con el administrador.");
        return;
      }

      // Sesión válida
      setIsAuthenticated(true);
      setUserName(data.username ?? credentials.username ?? "");
      setUserRole(data.role);
      setUserId(data.user_id);
      setLoginAttempts(0);
      persistSession(data);

    } catch (error) {
      const newAttempts = loginAttempts + 1;
      setLoginAttempts(newAttempts);

      // Backend indica usuario bloqueado dentro del error
      const errorState = error.response?.data?.state;
      if (errorState && errorState.toLowerCase() === "bloqueado") {
        setAuthError("Usuario bloqueado. Comuníquese con el administrador.");
        clearSession();
        resetAuthState();
        return;
      }

      // Sin respuesta del servidor
      if (!error.response) {
        setAuthError("Error: No se recibió respuesta del servidor.");
        return;
      }

      // Intentos fallidos progresivos
      if (newAttempts < 3) {
        setAuthError(
          "Contraseña incorrecta. Advertencia: después de tres intentos su usuario será bloqueado."
        );
      } else {
        setAuthError("Usuario bloqueado. Comuníquese con el administrador.");
      }

      clearSession();
      resetAuthState();
    }
  };

  // ── logout ────────────────────────────────────────────────────────────────

  /**
   * Retorna Promise para que App.js pueda encadenar .then()
   * El logout siempre limpia la sesión local, incluso si el backend falla.
   */
  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      // Error en el backend no impide cerrar la sesión local
      console.error("Error durante el logout:", error);
    } finally {
      clearSession();
      resetAuthState();
    }
  };

  // ── getToken ──────────────────────────────────────────────────────────────

  /**
   * El refresh automático ya está en el interceptor de api.js.
   * getToken solo expone el token actual para los componentes que
   * necesitan pasarlo explícitamente (abrir/cerrar registro/tiquete).
   */
  const getToken = () => {
    return localStorage.getItem("token") || null;
  };

  // ── Contexto ──────────────────────────────────────────────────────────────

  if (isLoading) return null; // Evita flash de login mientras restaura sesión

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        authError,
        userName,
        userRole,
        userId,
        login,
        logout,
        getToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);