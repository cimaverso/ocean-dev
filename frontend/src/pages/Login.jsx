/**
 * Login.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Layout dividido:
 *   Izquierda — panel de marca con logo, animación, patrón geométrico
 *   Derecha   — formulario de autenticación
 *
 * Sin dependencias externas de UI — solo AuthContext + react-router
 */

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import logoOcean from "../assets/logo.png";
import "./Login.css";

const Login = () => {
  const navigate              = useNavigate();
  const { login, authError, isAuthenticated } = useAuth();

  const [username,    setUsername]    = useState("");
  const [password,    setPassword]    = useState("");
  const [showPass,    setShowPass]    = useState(false);
  const [isLoading,   setIsLoading]   = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});

  // Redirigir si ya está autenticado
  useEffect(() => {
    if (isAuthenticated) navigate("/inicio", { replace: true });
  }, [isAuthenticated, navigate]);

  // ── Validación local ────────────────────────────────────────────────────
  const validate = () => {
    const errors = {};
    if (!username.trim()) errors.username = "Campo requerido";
    if (!password)        errors.password = "Campo requerido";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // ── Submit ──────────────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate() || isLoading) return;

    setIsLoading(true);
    try {
      await login({ username: username.trim(), password });
      // La redirección la maneja el useEffect de isAuthenticated
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSubmit(e);
  };

  return (
    <div className="login">
      {/* ══════════════════════════════════════════════
          Panel izquierdo — Marca
      ══════════════════════════════════════════════ */}
      <div className="login__brand" aria-hidden="true">
        {/* Decoración */}
        <div className="login__brand-dots" />
        <div className="login__brand-circle login__brand-circle--1" />
        <div className="login__brand-circle login__brand-circle--2" />

        {/* Contenido */}
        <div className="login__brand-content">
          <img src={logoOcean} alt="Ocean" className="login__logo" />

          <div>
            <h1 className="login__brand-title">Ocean</h1>
            <p className="login__brand-subtitle">Sistema de pesaje</p>
          </div>

          <div className="login__brand-divider" />

          <p className="login__brand-tagline">
            Control de ingresos, despachos y servicios de tractocarga
          </p>
        </div>
      </div>

      {/* ══════════════════════════════════════════════
          Panel derecho — Formulario
      ══════════════════════════════════════════════ */}
      <div className="login__form-panel">
        <div className="login__form-container">

          {/* Encabezado */}
          <div className="login__form-header">
            <p className="login__form-greeting">Bienvenido</p>
            <h2 className="login__form-title">Inicia sesión</h2>
          </div>

          {/* Formulario */}
          <form onSubmit={handleSubmit} noValidate>
            <div className="login__fields">

              {/* Usuario */}
              <div className="login__field">
                <label className="login__field-label" htmlFor="username">
                  Usuario
                </label>
                <div className="login__field-wrapper">
                  <input
                    id="username"
                    type="text"
                    className={`login__field-input${fieldErrors.username ? " login__field-input--error" : ""}`}
                    value={username}
                    onChange={(e) => {
                      setUsername(e.target.value);
                      if (fieldErrors.username) setFieldErrors((p) => ({ ...p, username: "" }));
                    }}
                    onKeyDown={handleKeyDown}
                    placeholder="Nombre de usuario"
                    autoComplete="username"
                    autoFocus
                    disabled={isLoading}
                    aria-invalid={Boolean(fieldErrors.username)}
                  />
                  <span className="login__field-icon">
                    <i className="bi bi-person" aria-hidden="true" />
                  </span>
                </div>
                {fieldErrors.username && (
                  <span style={{ fontSize: "var(--text-xs)", color: "var(--error)" }}>
                    {fieldErrors.username}
                  </span>
                )}
              </div>

              {/* Contraseña */}
              <div className="login__field">
                <label className="login__field-label" htmlFor="password">
                  Contraseña
                </label>
                <div className="login__field-wrapper">
                  <input
                    id="password"
                    type={showPass ? "text" : "password"}
                    className={`login__field-input${fieldErrors.password ? " login__field-input--error" : ""}`}
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      if (fieldErrors.password) setFieldErrors((p) => ({ ...p, password: "" }));
                    }}
                    onKeyDown={handleKeyDown}
                    placeholder="••••••••"
                    autoComplete="current-password"
                    disabled={isLoading}
                    aria-invalid={Boolean(fieldErrors.password)}
                  />
                  <span className="login__field-icon">
                    <i className="bi bi-lock" aria-hidden="true" />
                  </span>
                  <button
                    type="button"
                    className="login__field-toggle"
                    onClick={() => setShowPass((p) => !p)}
                    aria-label={showPass ? "Ocultar contraseña" : "Mostrar contraseña"}
                    tabIndex={-1}
                  >
                    <i className={`bi ${showPass ? "bi-eye-slash" : "bi-eye"}`} aria-hidden="true" />
                  </button>
                </div>
                {fieldErrors.password && (
                  <span style={{ fontSize: "var(--text-xs)", color: "var(--error)" }}>
                    {fieldErrors.password}
                  </span>
                )}
              </div>
            </div>

            {/* Error del backend */}
            {authError && (
              <div className="login__error" role="alert">
                <i className="bi bi-exclamation-triangle-fill" aria-hidden="true" />
                <span>{authError}</span>
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              className="login__submit"
              disabled={isLoading}
              style={{ marginTop: authError ? "var(--space-4)" : "0" }}
            >
              {isLoading ? (
                <>
                  <span className="login__spinner" aria-hidden="true" />
                  Verificando...
                </>
              ) : (
                <>
                  <i className="bi bi-box-arrow-in-right" aria-hidden="true" />
                  Ingresar
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="login__form-footer">
            Ocean &copy; {new Date().getFullYear()} — Sistema de pesaje
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;