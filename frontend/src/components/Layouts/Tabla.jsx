/**
 * Tabla.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Props:
 *   columns         {Array}    — [{ name, title, sortable?, mono?, render? }]
 *                                  name:     key del objeto de datos
 *                                  title:    cabecera visible
 *                                  sortable: permite ordenar por esta columna
 *                                  mono:     fuente monoespaciada (pesos, IDs)
 *                                  render:   (value, row) => ReactNode — renderizado custom
 *   data            {Array}    — Filas de datos
 *   onDoubleClickRow {Function} — (row) => void — acción al doble clic
 *   isLoading       {boolean}  — Muestra skeleton de carga
 *   emptyMessage    {string}   — Texto cuando no hay datos
 *   showFooter      {boolean}  — Muestra contador inferior (default: true)
 */

import React, { useState, useMemo } from "react";
import "./Tabla.css";

// ── Ícono de ordenamiento ─────────────────────────────────────────────────────
const SortIcon = ({ direction }) => {
  if (direction === "asc")  return <i className="bi bi-caret-up-fill tabla__sort-icon" />;
  if (direction === "desc") return <i className="bi bi-caret-down-fill tabla__sort-icon" />;
  return <i className="bi bi-chevron-expand tabla__sort-icon" />;
};

// ── Badge de tipo de registro ─────────────────────────────────────────────────
const TypeBadge = ({ value }) => {
  const lower = (value ?? "").toLowerCase();
  const icons = {
    ingreso:   "bi-arrow-down-circle",
    despacho:  "bi-arrow-up-circle",
    servicio:  "bi-gear",
    servicios: "bi-gear",
  };
  return (
    <span className={`tabla__type-badge tabla__type-badge--${lower}`}>
      <i className={`bi ${icons[lower] ?? "bi-circle"}`} aria-hidden="true" />
      {value}
    </span>
  );
};

// ── Filas skeleton ────────────────────────────────────────────────────────────
const SkeletonRows = ({ columns, count = 6 }) => (
  <>
    {Array.from({ length: count }).map((_, i) => (
      <tr key={i} className="tabla__skeleton-row">
        {columns.map((col) => (
          <td key={col.name} className="tabla__skeleton-cell">
            <div
              className="tabla__skeleton-bar"
              style={{ width: `${55 + Math.random() * 35}%` }}
            />
          </td>
        ))}
      </tr>
    ))}
  </>
);

// ═════════════════════════════════════════════════════════════════════════════

const Tabla = ({
  columns          = [],
  data             = [],
  onDoubleClickRow = null,
  isLoading        = false,
  emptyMessage     = "No hay registros para mostrar",
  showFooter       = true,
}) => {
  const [sortKey,       setSortKey]       = useState(null);
  const [sortDirection, setSortDirection] = useState("asc");
  const [activeRow,     setActiveRow]     = useState(null);

  // ── Ordenamiento ────────────────────────────────────────────────────────
  const handleSort = (col) => {
    if (!col.sortable) return;
    if (sortKey === col.name) {
      setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(col.name);
      setSortDirection("asc");
    }
  };

  const sortedData = useMemo(() => {
    if (!sortKey) return data;
    return [...data].sort((a, b) => {
      const aVal = a[sortKey] ?? "";
      const bVal = b[sortKey] ?? "";
      const cmp  = String(aVal).localeCompare(String(bVal), "es", { numeric: true });
      return sortDirection === "asc" ? cmp : -cmp;
    });
  }, [data, sortKey, sortDirection]);

  // ── Render celda ────────────────────────────────────────────────────────
  const renderCell = (col, row) => {
    const value = row[col.name];

    // Render custom
    if (col.render) return col.render(value, row);

    // Badge automático para columna "tipo"
    if (col.name === "tipo" && value) return <TypeBadge value={value} />;

    // Vacío
    if (value === null || value === undefined || value === "") {
      return <span style={{ color: "var(--text-disabled)" }}>—</span>;
    }

    return value;
  };

  // ── Estados vacío / carga ────────────────────────────────────────────────
  const isEmpty = !isLoading && sortedData.length === 0;

  return (
    <div className="tabla-wrapper">
      <div className="tabla-scroll">
        {isEmpty ? (
          <div className="tabla__empty" role="status">
            <i className="bi bi-inbox tabla__empty-icon" aria-hidden="true" />
            <span className="tabla__empty-text">{emptyMessage}</span>
          </div>
        ) : (
          <table className="tabla" role="table">
            {/* ── Cabecera ── */}
            <thead className="tabla__head">
              <tr>
                {columns.map((col) => (
                  <th
                    key={col.name}
                    className={[
                      "tabla__th",
                      col.sortable            ? "tabla__th--sortable" : "",
                      sortKey === col.name    ? "tabla__th--sorted"   : "",
                    ].filter(Boolean).join(" ")}
                    onClick={() => handleSort(col)}
                    aria-sort={
                      sortKey === col.name
                        ? sortDirection === "asc" ? "ascending" : "descending"
                        : undefined
                    }
                    scope="col"
                  >
                    {col.title}
                    {col.sortable && (
                      <SortIcon
                        direction={sortKey === col.name ? sortDirection : null}
                      />
                    )}
                  </th>
                ))}
              </tr>
            </thead>

            {/* ── Cuerpo ── */}
            <tbody className="tabla__body">
              {isLoading ? (
                <SkeletonRows columns={columns} />
              ) : (
                sortedData.map((row, idx) => (
                  <tr
                    key={row.id ?? row.registro ?? idx}
                    className={[
                      "tabla__row",
                      onDoubleClickRow    ? "tabla__row--clickable" : "",
                      activeRow === idx   ? "tabla__row--active"    : "",
                    ].filter(Boolean).join(" ")}
                    onDoubleClick={() => {
                      setActiveRow(idx);
                      onDoubleClickRow?.(row);
                    }}
                    onClick={() => setActiveRow(idx)}
                    tabIndex={onDoubleClickRow ? 0 : undefined}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && onDoubleClickRow) {
                        setActiveRow(idx);
                        onDoubleClickRow(row);
                      }
                    }}
                    aria-selected={activeRow === idx}
                  >
                    {columns.map((col) => (
                      <td
                        key={col.name}
                        className={[
                          "tabla__td",
                          col.mono ? "tabla__td--mono" : "",
                        ].filter(Boolean).join(" ")}
                        title={
                          typeof row[col.name] === "string" &&
                          row[col.name].length > 25
                            ? row[col.name]
                            : undefined
                        }
                      >
                        {renderCell(col, row)}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* ── Footer con contador ── */}
      {showFooter && !isLoading && (
        <div className="tabla__footer">
          <span className="tabla__footer-count">
            {isEmpty
              ? "Sin registros"
              : `${sortedData.length} registro${sortedData.length !== 1 ? "s" : ""}`}
          </span>
          {sortKey && (
            <span className="tabla__footer-count">
              Ordenado por: <strong>{columns.find(c => c.name === sortKey)?.title}</strong>
              {" "}{sortDirection === "asc" ? "↑" : "↓"}
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default Tabla;