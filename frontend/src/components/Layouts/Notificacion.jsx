/**
 * Notificacion.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Exporta dos componentes:
 *
 * 1. <Notification /> — Toast auto-cerrante (esquina inferior derecha)
 *    Props:
 *      message   {string}    — Texto del toast. Si está vacío no renderiza.
 *      type      {string}    — "success" | "error" | "warning" | "info"
 *      duration  {number}    — ms antes de auto-cerrar (default: 4000). 0 = no auto-cierra
 *      onClose   {Function}  — Callback al cerrar
 *
 * 2. <ConfirmModal /> — Modal de confirmación (reemplaza onConfirm/onCancel del original)
 *    Props:
 *      isOpen    {boolean}
 *      message   {string}
 *      type      {string}    — "error" | "warning" | "info" | "success"
 *      onConfirm {Function}
 *      onCancel  {Function}
 *      confirmLabel {string} — default "Confirmar"
 *      cancelLabel  {string} — default "Cancelar"
 *
 * Uso típico en componentes:
 *   const [notif, setNotif] = useState({ message: "", type: "" });
 *   <Notification
 *     message={notif.message}
 *     type={notif.type}
 *     onClose={() => setNotif({ message: "", type: "" })}
 *   />
 */

import React, { useEffect, useState, useCallback } from "react";
import "./Notificacion.css";

// ── Configuración por tipo ────────────────────────────────────────────────────
const TYPE_CONFIG = {
  success: {
    icon:  "bi-check-circle-fill",
    title: "Éxito",
  },
  error: {
    icon:  "bi-x-circle-fill",
    title: "Error",
  },
  warning: {
    icon:  "bi-exclamation-triangle-fill",
    title: "Advertencia",
  },
  info: {
    icon:  "bi-info-circle-fill",
    title: "Información",
  },
};

// ═════════════════════════════════════════════════════════════════════════════
// Toast
// ═════════════════════════════════════════════════════════════════════════════

export const Notification = ({
  message  = "",
  type     = "info",
  duration = 4000,
  onClose,
}) => {
  const [visible,  setVisible]  = useState(false);
  const [exiting,  setExiting]  = useState(false);

  const close = useCallback(() => {
    setExiting(true);
    // Esperar que termine la animación de salida antes de limpiar
    setTimeout(() => {
      setVisible(false);
      setExiting(false);
      onClose?.();
    }, 320);
  }, [onClose]);

  // Mostrar cuando llega un mensaje nuevo
  useEffect(() => {
    if (!message) {
      setVisible(false);
      return;
    }
    setVisible(true);
    setExiting(false);

    if (duration > 0) {
      const timer = setTimeout(close, duration);
      return () => clearTimeout(timer);
    }
  }, [message, duration, close]);

  if (!visible || !message) return null;

  const config = TYPE_CONFIG[type] ?? TYPE_CONFIG.info;

  return (
    <div className="toast-container" role="region" aria-live="polite" aria-label="Notificaciones">
      <div
        className={`toast toast--${type}${exiting ? " toast--exiting" : ""}`}
        role="alert"
      >
        {/* Ícono */}
        <i className={`bi ${config.icon} toast__icon`} aria-hidden="true" />

        {/* Contenido */}
        <div className="toast__content">
          <div className="toast__title">{config.title}</div>
          <div className="toast__message">{message}</div>
        </div>

        {/* Cerrar */}
        <button
          className="toast__close"
          onClick={close}
          aria-label="Cerrar notificación"
        >
          <i className="bi bi-x" aria-hidden="true" />
        </button>

        {/* Barra de progreso auto-close */}
        {duration > 0 && (
          <div
            className="toast__progress"
            style={{ animationDuration: `${duration}ms` }}
            aria-hidden="true"
          />
        )}
      </div>
    </div>
  );
};

// ═════════════════════════════════════════════════════════════════════════════
// Modal de confirmación
// ═════════════════════════════════════════════════════════════════════════════

export const ConfirmModal = ({
  isOpen       = false,
  message      = "¿Estás seguro?",
  type         = "warning",
  onConfirm,
  onCancel,
  confirmLabel = "Confirmar",
  cancelLabel  = "Cancelar",
}) => {
  // Bloquear scroll del body cuando está abierto
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [isOpen]);

  if (!isOpen) return null;

  const config = TYPE_CONFIG[type] ?? TYPE_CONFIG.warning;

  return (
    <div
      className="confirm-overlay"
      onClick={(e) => { if (e.target === e.currentTarget) onCancel?.(); }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-title"
    >
      <div className="confirm-modal">
        {/* Ícono */}
        <div className={`confirm-modal__icon confirm-modal__icon--${type}`}>
          <i className={`bi ${config.icon}`} aria-hidden="true" />
        </div>

        {/* Texto */}
        <h3 className="confirm-modal__title" id="confirm-title">
          {config.title}
        </h3>
        <p className="confirm-modal__message">{message}</p>

        {/* Acciones */}
        <div className="confirm-modal__actions">
          <button
            className="confirm-modal__cancel"
            onClick={onCancel}
          >
            {cancelLabel}
          </button>
          <button
            className={`confirm-modal__confirm${type === "error" ? " confirm-modal__confirm--error" : ""}`}
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};

// Export default para compatibilidad con imports existentes
export default Notification;