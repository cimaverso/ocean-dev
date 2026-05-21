/**
 * BotonesVista.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Props:
 *   showTransito  {Function} — Activa vista tránsito
 *   showHistorial {Function} — Activa vista historial
 *   viewType      {string}   — "transito" | "historial"
 *   countTransito {number}   — Cantidad de registros en tránsito
 *   countHistorial{number}   — Cantidad de registros en historial
 */

import React from "react";
import "./BotonesVista.css";

const BotonesVista = ({
  showTransito,
  showHistorial,
  viewType,
  countTransito  = null,
  countHistorial = null,
}) => (
  <div className="vista-tabs" role="tablist" aria-label="Vista de registros">
    {/* ── Tránsito ── */}
    <button
      role="tab"
      aria-selected={viewType === "transito"}
      className={`vista-tab${viewType === "transito" ? " vista-tab--active" : ""}`}
      onClick={showTransito}
    >
      <span className="vista-tab__icon">
        <i className="bi bi-truck" aria-hidden="true" />
      </span>
      Tránsito
      {countTransito !== null && (
        <span className="vista-tab__badge">{countTransito}</span>
      )}
    </button>

    {/* ── Historial ── */}
    <button
      role="tab"
      aria-selected={viewType === "historial"}
      className={`vista-tab${viewType === "historial" ? " vista-tab--active" : ""}`}
      onClick={showHistorial}
    >
      <span className="vista-tab__icon">
        <i className="bi bi-clock-history" aria-hidden="true" />
      </span>
      Historial
      {countHistorial !== null && (
        <span className="vista-tab__badge">{countHistorial}</span>
      )}
    </button>
  </div>
);

export default BotonesVista;