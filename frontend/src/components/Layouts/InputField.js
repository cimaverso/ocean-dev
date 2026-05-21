/**
 * InputField.js
 * Proyecto Ocean — Sistema de pesaje
 *
 * Props:
 *   label       {string}    — Etiqueta del campo
 *   id          {string}    — ID del input (accesibilidad)
 *   type        {string}    — Tipo HTML: text | number | date | time | email | password
 *   value       {any}       — Valor controlado
 *   onChange    {Function}  — (e) => void
 *   placeholder {string}    — Placeholder
 *   disabled    {boolean}   — Deshabilitar
 *   readOnly    {boolean}   — Solo lectura
 *   tabIndex    {number}    — Tab order
 *   icon        {string}    — Clase Bootstrap Icons (ej: "bi-search")
 *   onAction    {Function}  — Si se provee, muestra botón de acción a la derecha
 *   actionIcon  {string}    — Ícono del botón de acción (default: "bi-cursor")
 *   actionTitle {string}    — Tooltip del botón de acción
 *   isTextarea  {boolean}   — Renderizar como textarea
 *   rows        {number}    — Filas del textarea (default: 3)
 *   variant     {string}    — "number" | "highlight" | "" — estilos especiales
 *   layout      {string}    — "row" (default) | "column"
 *   error       {string}    — Mensaje de error
 *   hint        {string}    — Mensaje de ayuda
 *   className   {string}    — Clase extra para el contenedor
 */

import React from "react";
import "./InputField.css";

const InputField = ({
  label,
  id,
  type        = "text",
  value       = "",
  onChange,
  placeholder = "",
  disabled    = false,
  readOnly    = false,
  tabIndex,
  icon        = "",
  onAction    = null,
  actionIcon  = "bi-cursor",
  actionTitle = "Acción",
  isTextarea  = false,
  rows        = 3,
  variant     = "",
  layout      = "row",
  error       = "",
  hint        = "",
  className   = "",
}) => {
  const hasIcon   = Boolean(icon);
  const hasAction = Boolean(onAction);

  const wrapperClass = [
    "input-field__wrapper",
    hasIcon   ? "input-field__wrapper--icon-left" : "",
    hasAction ? "input-field__wrapper--action"    : "",
  ]
    .filter(Boolean)
    .join(" ");

  const inputClass = [
    isTextarea ? "input-field__textarea" : "input-field__input",
    variant === "number"    ? "input-field__input--number"    : "",
    variant === "highlight" ? "input-field__input--highlight" : "",
    error                   ? "input-field__input--error"     : "",
  ]
    .filter(Boolean)
    .join(" ");

  const containerClass = [
    "input-field",
    layout === "column" ? "input-field--column" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={containerClass}>
      {label && (
        <label className="input-field__label" htmlFor={id}>
          {label}
        </label>
      )}

      <div className={wrapperClass}>
        {/* Ícono izquierdo */}
        {hasIcon && (
          <span className="input-field__icon-left" aria-hidden="true">
            <i className={`bi ${icon}`} />
          </span>
        )}

        {/* Input o Textarea */}
        {isTextarea ? (
          <textarea
            id={id}
            className={inputClass}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            disabled={disabled}
            readOnly={readOnly}
            tabIndex={tabIndex}
            rows={rows}
            aria-invalid={Boolean(error)}
            aria-describedby={
              error ? `${id}-error` : hint ? `${id}-hint` : undefined
            }
          />
        ) : (
          <input
            id={id}
            type={type}
            className={inputClass}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            disabled={disabled}
            readOnly={readOnly}
            tabIndex={tabIndex}
            aria-invalid={Boolean(error)}
            aria-describedby={
              error ? `${id}-error` : hint ? `${id}-hint` : undefined
            }
          />
        )}

        {/* Botón de acción (ej: leer peso de báscula) */}
        {hasAction && (
          <button
            type="button"
            className="input-field__action-btn"
            onClick={onAction}
            title={actionTitle}
            aria-label={actionTitle}
            tabIndex={-1}
          >
            <i className={`bi ${actionIcon}`} aria-hidden="true" />
          </button>
        )}
      </div>

      {/* Mensajes */}
      {error && (
        <span id={`${id}-error`} className="input-field__error" role="alert">
          {error}
        </span>
      )}
      {!error && hint && (
        <span id={`${id}-hint`} className="input-field__hint">
          {hint}
        </span>
      )}
    </div>
  );
};

export default InputField;