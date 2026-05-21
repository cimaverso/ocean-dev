/**
 * Header.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Props: ninguna — lee contexto y ruta automáticamente
 * Expone: toggle de tema vía atributo data-theme en <html>
 */

import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import logoOcean from "../../assets/logo.png"; // ajusta nombre si difiere
import "./Header.css";

// ── Mapa de rutas a nombres legibles ─────────────────────────────────────────
const PAGE_NAMES = {
  "/inicio":    "Inicio",
  "/registro":  "Registro",
  "/consultas": "Consultas",
  "/formulario":"Formulario",
  "/soporte":   "Soporte",
};

// ── Iniciales desde nombre ────────────────────────────────────────────────────
const getInitials = (name = "") => {
  const parts = name.trim().split(" ").filter(Boolean);
  if (parts.length === 0) return "U";
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
};

// ── Íconos SVG inline (sin dependencia de heroicons en este componente) ───────
const IconSun = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
    strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <circle cx="12" cy="12" r="5" />
    <line x1="12" y1="1"  x2="12" y2="3"  />
    <line x1="12" y1="21" x2="12" y2="23" />
    <line x1="4.22"  y1="4.22"  x2="5.64"  y2="5.64"  />
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
    <line x1="1"  y1="12" x2="3"  y2="12" />
    <line x1="21" y1="12" x2="23" y2="12" />
    <line x1="4.22"  y1="19.78" x2="5.64"  y2="18.36" />
    <line x1="18.36" y1="5.64"  x2="19.78" y2="4.22"  />
  </svg>
);

const IconMoon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
    strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
  </svg>
);

const IconLogout = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
    strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
    <polyline points="16 17 21 12 16 7" />
    <line x1="21" y1="12" x2="9" y2="12" />
  </svg>
);

// ─────────────────────────────────────────────────────────────────────────────

const Header = () => {
  const location = useLocation();
  const navigate  = useNavigate();
  const { userName, userRole, logout } = useAuth();

  const [isDark, setIsDark] = useState(() => {
    return localStorage.getItem("theme") === "dark";
  });

  // Aplicar tema al montar y al cambiar
  useEffect(() => {
    const html = document.documentElement;
    if (isDark) {
      html.setAttribute("data-theme", "dark");
      localStorage.setItem("theme", "dark");
    } else {
      html.removeAttribute("data-theme");
      localStorage.setItem("theme", "light");
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark((prev) => !prev);

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const pageName = PAGE_NAMES[location.pathname] ?? "";

  return (
    <header className="header" role="banner">
      {/* ── Izquierda ── */}
      <div className="header__left">
        <img
          src={logoOcean}
          alt="Ocean"
          className="header__logo"
        />
        {pageName && (
          <>
            <span className="header__divider" aria-hidden="true" />
            <span className="header__page-name">{pageName}</span>
          </>
        )}
      </div>

      {/* ── Derecha ── */}
      <div className="header__right">
        {/* Toggle dark/light */}
        <button
          className="header__theme-toggle"
          onClick={toggleTheme}
          aria-label={isDark ? "Cambiar a modo claro" : "Cambiar a modo oscuro"}
          title={isDark ? "Modo claro" : "Modo oscuro"}
        >
          {isDark ? <IconSun /> : <IconMoon />}
        </button>

        {/* Usuario */}
        <div className="header__user">
          <div
            className="header__user-avatar"
            aria-hidden="true"
            title={userName}
          >
            {getInitials(userName)}
          </div>
          <div className="header__user-info">
            <span className="header__user-name">{userName || "Usuario"}</span>
            <span className="header__user-role">{userRole  || "—"}</span>
          </div>
        </div>

        {/* Logout */}
        <button
          className="header__logout"
          onClick={handleLogout}
          aria-label="Cerrar sesión"
          title="Cerrar sesión"
        >
          <IconLogout />
        </button>
      </div>
    </header>
  );
};

export default Header;