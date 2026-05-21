/**
 * TarjetaInicio.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Tarjeta de métrica para el dashboard.
 *
 * Props:
 *   label     {string}  — Nombre de la métrica
 *   value     {string|number} — Valor principal
 *   unit      {string}  — Unidad opcional (ej: "Kg", "registros")
 *   icon      {string}  — Clase Bootstrap Icons (ej: "bi-truck")
 *   variant   {string}  — "ingreso"|"despacho"|"servicio"|"transito"|"peso"
 *   trend     {number}  — Porcentaje de cambio (positivo/negativo/0)
 *   trendLabel{string}  — Texto descriptivo de la tendencia
 *   isLoading {boolean} — Skeleton
 */

import React from "react";
import "./TarjetaInicio.css";

const TarjetaInicio = ({
  label      = "",
  value      = "—",
  unit       = "",
  icon       = "bi-bar-chart",
  variant    = "",
  trend      = null,
  trendLabel = "vs ayer",
  isLoading  = false,
}) => {
  const cardClass = [
    "metric-card",
    variant   ? `metric-card--${variant}` : "",
    isLoading ? "metric-card--skeleton"   : "",
  ]
    .filter(Boolean)
    .join(" ");

  const trendDir =
    trend === null ? null
    : trend > 0   ? "up"
    : trend < 0   ? "down"
    : "flat";

  const trendIcon =
    trendDir === "up"   ? "bi-arrow-up-short"
    : trendDir === "down" ? "bi-arrow-down-short"
    : "bi-dash";

  return (
    <div className={cardClass}>
      {/* Header */}
      <div className="metric-card__header">
        <span className="metric-card__label">{label}</span>
        <div className="metric-card__icon" aria-hidden="true">
          <i className={`bi ${icon}`} />
        </div>
      </div>

      {/* Valor */}
      <div>
        <span className="metric-card__value">
          {isLoading ? "———" : value}
        </span>
        {unit && !isLoading && (
          <span className="metric-card__unit">{unit}</span>
        )}
      </div>

      {/* Footer tendencia */}
      <div className="metric-card__footer">
        {trend !== null && !isLoading && (
          <span className={`metric-card__trend metric-card__trend--${trendDir}`}>
            <i className={`bi ${trendIcon}`} aria-hidden="true" />
            {Math.abs(trend)}%
          </span>
        )}
        <span>{isLoading ? "Cargando..." : trendLabel}</span>
      </div>
    </div>
  );
};

export default TarjetaInicio;