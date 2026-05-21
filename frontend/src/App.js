/**
 * App.js
 * Proyecto Ocean — Sistema de pesaje
 *
 * - Aplica el tema (dark/light) desde localStorage al montar
 * - Rutas protegidas por isAuthenticated
 * - Logout via Electron onLogout
 * - routes.js eliminado — todo el routing vive aquí
 */

import React, { useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

import Login     from "./pages/Login";
import Inicio    from "./pages/Inicio";
import Registro  from "./pages/Registro";
import Consultas from "./pages/Consultas";
import Formulario from "./pages/Formulario";
import Soporte   from "./pages/Soporte";

const App = () => {
  const { isAuthenticated, logout } = useAuth();

  // ── Aplicar tema guardado al montar ──────────────────────────────────────
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
  }, []);

  // ── Logout desde Electron (botón nativo de la ventana) ───────────────────
  useEffect(() => {
    if (!window.electron) return;

    window.electron.onLogout(async () => {
      await logout();
      window.close();
    });
  }, [logout]);

  return (
    <Routes>
      {/* Pública */}
      <Route path="/login" element={<Login />} />

      {/* Protegidas */}
      {isAuthenticated ? (
        <>
          <Route path="/inicio"    element={<Inicio />}     />
          <Route path="/registro"  element={<Registro />}   />
          <Route path="/consultas" element={<Consultas />}  />
          <Route path="/formulario" element={<Formulario />} />
          <Route path="/soporte"   element={<Soporte />}    />
          <Route path="*"          element={<Navigate to="/inicio" replace />} />
        </>
      ) : (
        <Route path="*" element={<Navigate to="/login" replace />} />
      )}
    </Routes>
  );
};

export default App;