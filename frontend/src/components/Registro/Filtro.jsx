/**
 * Filtro.jsx — FilterSection
 * Proyecto Ocean — Sistema de pesaje
 *
 * Props:
 *   data          {Array}    — Datos crudos desde el padre (Registro.jsx)
 *   onFilter      {Function} — (filteredData) => void — devuelve datos filtrados
 *   isLoading     {boolean}  — Estado de carga
 *   onRefresh     {Function} — Callback para refrescar datos desde el padre
 *   consultaTipo  {string}   — "transito" | "historial"
 *
 * ELIMINADO:
 *   - fetch interno con axios (el padre es dueño de los datos)
 *   - setTableData directo (reemplazado por onFilter)
 */

import React, { useState, useEffect, useMemo, useCallback } from "react";
import "./Filtro.css";

const FilterSection = ({
  data         = [],
  onFilter,
  isLoading    = false,
  onRefresh,
  consultaTipo = "transito",
}) => {
  const [placa,              setPlaca]              = useState("");
  const [resultadosPorPagina, setResultadosPorPagina] = useState("todos");
  // null = sin filtro de tipo, "INGRESO"|"DESPACHO"|"SERVICIOS" = filtro activo
  const [tipoFiltro,         setTipoFiltro]         = useState(null);

  // ── Contadores por tipo ────────────────────────────────────────────────
  const counts = useMemo(() => ({
    ingresos:  data.filter((i) => (i.tipo || "").toUpperCase() === "INGRESO").length,
    despachos: data.filter((i) => (i.tipo || "").toUpperCase() === "DESPACHO").length,
    servicios: data.filter((i) =>
      ["SERVICIO", "SERVICIOS"].includes((i.tipo || "").toUpperCase())
    ).length,
  }), [data]);

  // ── Lógica de filtrado ─────────────────────────────────────────────────
  const filteredData = useMemo(() => {
    let result = data;

    // Filtrar por placa
    if (placa.trim()) {
      result = result.filter((item) =>
        (item.placa || "").toUpperCase().includes(placa.toUpperCase())
      );
    }

    // Filtrar por tipo si hay filtro activo
    if (tipoFiltro) {
      result = result.filter((item) =>
        (item.tipo || "").toUpperCase() === tipoFiltro ||
        (tipoFiltro === "SERVICIOS" && (item.tipo || "").toUpperCase() === "SERVICIO")
      );
    }

    // Paginación
    if (resultadosPorPagina !== "todos") {
      result = result.slice(0, Number(resultadosPorPagina));
    }

    return result;
  }, [data, placa, tipoFiltro, resultadosPorPagina]);

  // Notificar al padre cuando cambia el filtrado
  useEffect(() => {
    onFilter?.(filteredData);
  }, [filteredData, onFilter]);

  // Limpiar filtros al cambiar de vista
  useEffect(() => {
    setPlaca("");
    setTipoFiltro(null);
    setResultadosPorPagina("todos");
  }, [consultaTipo]);

  // ── Toggle filtro por tipo ─────────────────────────────────────────────
  const handleTipoClick = useCallback((tipo) => {
    setTipoFiltro((prev) => (prev === tipo ? null : tipo));
  }, []);

  const handleClearPlaca = () => setPlaca("");

  return (
    <div className="filtro" role="search" aria-label="Filtros de registros">

      {/* ── Búsqueda por placa ── */}
      <div className="filtro__search">
        <div className="filtro__search-wrapper">
          <span className="filtro__search-icon">
            <i className="bi bi-search" aria-hidden="true" />
          </span>
          <input
            type="text"
            className="filtro__search-input"
            value={placa}
            onChange={(e) => setPlaca(e.target.value)}
            placeholder="Buscar por placa..."
            aria-label="Buscar por placa"
            maxLength={10}
            spellCheck={false}
          />
          {placa && (
            <button
              className="filtro__search-clear"
              onClick={handleClearPlaca}
              aria-label="Limpiar búsqueda"
            >
              <i className="bi bi-x" aria-hidden="true" />
            </button>
          )}
        </div>
      </div>

      {/* ── Contadores clicables por tipo ── */}
      <div className="filtro__counters" role="group" aria-label="Filtrar por tipo">
        <button
          className={`filtro__counter filtro__counter--ingreso${
            tipoFiltro && tipoFiltro !== "INGRESO" ? " filtro__counter--inactive" : ""
          }`}
          onClick={() => handleTipoClick("INGRESO")}
          aria-pressed={tipoFiltro === "INGRESO"}
          title="Filtrar solo ingresos"
        >
          <i className="bi bi-arrow-down-circle" aria-hidden="true" />
          Ingresos
          <span className="filtro__counter-value">{counts.ingresos}</span>
        </button>

        <button
          className={`filtro__counter filtro__counter--despacho${
            tipoFiltro && tipoFiltro !== "DESPACHO" ? " filtro__counter--inactive" : ""
          }`}
          onClick={() => handleTipoClick("DESPACHO")}
          aria-pressed={tipoFiltro === "DESPACHO"}
          title="Filtrar solo despachos"
        >
          <i className="bi bi-arrow-up-circle" aria-hidden="true" />
          Despachos
          <span className="filtro__counter-value">{counts.despachos}</span>
        </button>

        <button
          className={`filtro__counter filtro__counter--servicio${
            tipoFiltro && tipoFiltro !== "SERVICIOS" ? " filtro__counter--inactive" : ""
          }`}
          onClick={() => handleTipoClick("SERVICIOS")}
          aria-pressed={tipoFiltro === "SERVICIOS"}
          title="Filtrar solo servicios"
        >
          <i className="bi bi-gear" aria-hidden="true" />
          Servicios
          <span className="filtro__counter-value">{counts.servicios}</span>
        </button>
      </div>

      {/* ── Paginación + Refresh ── */}
      <div className="filtro__pagination">
        <span className="filtro__pagination-label">Mostrar</span>
        <select
          className="filtro__pagination-select"
          value={resultadosPorPagina}
          onChange={(e) => setResultadosPorPagina(e.target.value)}
          aria-label="Resultados por página"
        >
          <option value="todos">Todos</option>
          <option value={10}>10</option>
          <option value={25}>25</option>
          <option value={50}>50</option>
        </select>

        {onRefresh && (
          <button
            className={`filtro__refresh${isLoading ? " filtro__refresh--spinning" : ""}`}
            onClick={onRefresh}
            disabled={isLoading}
            aria-label="Refrescar datos"
            title="Refrescar"
          >
            <i className="bi bi-arrow-clockwise" aria-hidden="true" />
          </button>
        )}
      </div>
    </div>
  );
};

export default FilterSection;