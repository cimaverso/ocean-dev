/**
 * Transito.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Define columnas para la vista de registros en tránsito.
 * Delega todo el render a Tabla.jsx.
 *
 * Props:
 *   data             {Array}    — Registros en tránsito
 *   onDoubleClickRow {Function} — (row) => void
 *   isLoading        {boolean}  — Skeleton de carga
 */

import React from "react";
import Tabla from "../Layouts/Tabla";

const columnsTransito = [
  {
    name:     "tipo",
    title:    "Tipo",
    sortable: true,
    // Badge automático manejado por Tabla.jsx cuando name === "tipo"
  },
  {
    name:     "registro",
    title:    "Registro",
    sortable: true,
    mono:     true,
  },
  {
    name:     "placa",
    title:    "Placa",
    sortable: true,
    mono:     true,
    render:   (val) => val
      ? <strong style={{ letterSpacing: "0.06em" }}>{val}</strong>
      : <span style={{ color: "var(--text-disabled)" }}>—</span>,
  },
  {
    name:     "cedulaConductor",
    title:    "Cédula",
    sortable: false,
    mono:     true,
  },
  {
    name:     "conductor",
    title:    "Conductor",
    sortable: true,
  },
  {
    name:     "trailer",
    title:    "Trailer",
    sortable: false,
    mono:     true,
  },
  {
    name:     "fEntrada",
    title:    "F. Entrada",
    sortable: true,
    mono:     true,
  },
  {
    name:     "hEntrada",
    title:    "H. Entrada",
    sortable: false,
    mono:     true,
  },
  {
    name:     "peso",
    title:    "Peso Bruto",
    sortable: true,
    mono:     true,
    render:   (val) => val
      ? `${Number(val).toLocaleString("es-CO")} kg`
      : <span style={{ color: "var(--text-disabled)" }}>—</span>,
  },
];

const TablaTransito = ({ data = [], onDoubleClickRow, isLoading = false }) => (
  <Tabla
    columns={columnsTransito}
    data={data}
    onDoubleClickRow={onDoubleClickRow}
    isLoading={isLoading}
    emptyMessage="No hay vehículos en tránsito"
    showFooter
  />
);

export default TablaTransito;