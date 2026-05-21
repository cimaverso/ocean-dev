/**
 * FormSection.js
 * Proyecto Ocean — Sistema de pesaje
 *
 * Contenedor visual con cabecera azul para agrupar campos de formulario.
 *
 * Props:
 *   title       {string}    — Título de la sección (requerido)
 *   icon        {string}    — Clase Bootstrap Icons opcional (ej: "bi-person")
 *   children    {ReactNode} — Contenido del cuerpo
 *   variant     {string}    — "" | "compact" | "flat"
 *   action      {ReactNode} — Elemento opcional en el lado derecho del header
 *                             Ej: <button>+ Añadir</button>
 *   className   {string}    — Clase extra para el contenedor
 */

import React from "react";
import "./Nuevo.jsx";

const FormSection = ({
  title,
  icon      = "",
  children,
  variant   = "",
  action    = null,
  className = "",
}) => {
  const containerClass = [
    "form-section",
    variant === "compact" ? "form-section--compact" : "",
    variant === "flat"    ? "form-section--flat"    : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={containerClass}>
      {/* ── Cabecera ── */}
      {title && (
        <div className="form-section__header">
          {icon && (
            <span className="form-section__header-icon" aria-hidden="true">
              <i className={`bi ${icon}`} />
            </span>
          )}
          <h3 className="form-section__title">{title}</h3>
          {action && (
            <div className="form-section__header-action">{action}</div>
          )}
        </div>
      )}

      {/* ── Cuerpo ── */}
      <div className="form-section__body">
        {children}
      </div>
    </div>
  );
};

export default FormSection;