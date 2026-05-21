/**
 * index.js
 * Proyecto Ocean — Sistema de pesaje
 *
 * Punto de entrada de la aplicación React.
 * Importa estilos globales y Bootstrap Icons antes de montar el árbol.
 */

import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

// ── Estilos globales ──────────────────────────────────────────────────────
import "bootstrap-icons/font/bootstrap-icons.css";
import "./index.css";

// ── App ───────────────────────────────────────────────────────────────────
import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);