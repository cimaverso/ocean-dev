/**
 * Sidebar.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * - Colapsable: persiste estado en localStorage
 * - Íconos: Bootstrap Icons (npm install bootstrap-icons)
 * - Tooltips automáticos cuando está colapsado
 * - Ítem activo detectado por ruta actual
 */

import React, { useState, useEffect } from "react";
import { NavLink, useLocation } from "react-router-dom";
import logoOcean from "../../assets/logo.png"; // ajusta si el nombre difiere
import "./Sidebar.css";

// ── Definición de navegación ──────────────────────────────────────────────────
const NAV_ITEMS = [
  {
    section: "Principal",
    items: [
      {
        to:      "/inicio",
        label:   "Inicio",
        icon:    "bi-house",
        tooltip: "Inicio",
      },
      {
        to:      "/registro",
        label:   "Registro",
        icon:    "bi-journal-text",
        tooltip: "Registro",
      },
      {
        to:      "/formulario",
        label:   "Formulario",
        icon:    "bi-file-earmark-plus",
        tooltip: "Formulario",
      },
    ],
  },
  {
    section: "Consultas",
    items: [
      {
        to:      "/consultas",
        label:   "Consultas",
        icon:    "bi-search",
        tooltip: "Consultas",
      },
      {
        to:      "/soporte",
        label:   "Soporte",
        icon:    "bi-headset",
        tooltip: "Soporte",
      },
    ],
  },
];

// ─────────────────────────────────────────────────────────────────────────────

const Sidebar = () => {
  const location = useLocation();

  const [collapsed, setCollapsed] = useState(() => {
    return localStorage.getItem("sidebar-collapsed") === "true";
  });

  // Persistir estado de colapso
  useEffect(() => {
    localStorage.setItem("sidebar-collapsed", String(collapsed));
  }, [collapsed]);

  const toggleCollapse = () => setCollapsed((prev) => !prev);

  return (
    <aside
      className={`sidebar${collapsed ? " sidebar--collapsed" : ""}`}
      aria-label="Navegación principal"
    >
      {/* ── Marca ── */}
      <div className="sidebar__brand">
        <img
          src={logoOcean}
          alt="Ocean"
          className="sidebar__brand-logo"
        />
        <span className="sidebar__brand-name">Ocean</span>
      </div>

      {/* ── Navegación ── */}
      <nav className="sidebar__nav" aria-label="Menú principal">
        {NAV_ITEMS.map(({ section, items }) => (
          <div key={section}>
            <div className="sidebar__section-label">{section}</div>

            {items.map(({ to, label, icon, tooltip }) => {
              const isActive = location.pathname.startsWith(to);

              return (
                <NavLink
                  key={to}
                  to={to}
                  className={`sidebar__item${isActive ? " sidebar__item--active" : ""}`}
                  data-tooltip={tooltip}
                  aria-label={collapsed ? label : undefined}
                  aria-current={isActive ? "page" : undefined}
                  end={to === "/inicio"}
                >
                  <i className={`bi ${icon} sidebar__icon`} aria-hidden="true" />
                  <span className="sidebar__label">{label}</span>
                </NavLink>
              );
            })}
          </div>
        ))}
      </nav>

      {/* ── Footer: botón colapsar ── */}
      <div className="sidebar__footer">
        <button
          className="sidebar__collapse-btn"
          onClick={toggleCollapse}
          aria-label={collapsed ? "Expandir menú" : "Colapsar menú"}
          title={collapsed ? "Expandir" : "Colapsar"}
        >
          <i className="bi bi-chevron-left" aria-hidden="true" />
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;