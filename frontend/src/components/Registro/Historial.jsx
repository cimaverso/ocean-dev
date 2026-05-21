/**
 * Historial.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Define columnas para la vista de historial de tiquetes.
 * Delega todo el render a Tabla.jsx.
 *
 * Props:
 *   data             {Array}    — Tiquetes del historial
 *   onDoubleClickRow {Function} — (row) => void
 *   isLoading        {boolean}  — Skeleton de carga
 */

import React from "react";
import Tabla from "../Layouts/Tabla";

const columnsHistorial = [
  {
    name:     "tipo",
    title:    "Tipo",
    sortable: true,
    // Badge automático manejado por Tabla.jsx cuando name === "tipo"
  },
  {
    name:     "tiquete",
    title:    "Tiquete",
    sortable: true,
    mono:     true,
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
    title:    "Peso Neto",
    sortable: true,
    mono:     true,
    render:   (val) => val
      ? (
        <span style={{ fontWeight: "var(--fw-semi)", color: "var(--text-primary)" }}>
          {Number(val).toLocaleString("es-CO")} kg
        </span>
      )
      : <span style={{ color: "var(--text-disabled)" }}>—</span>,
  },
  {
    name:     "fSalida",
    title:    "F. Salida",
    sortable: true,
    mono:     true,
  },
  {
    name:     "hSalida",
    title:    "H. Salida",
    sortable: false,
    mono:     true,
  },
];

const TablaHistorial = ({ data = [], onDoubleClickRow, isLoading = false }) => (
  <Tabla
    columns={columnsHistorial}
    data={data}
    onDoubleClickRow={onDoubleClickRow}
    isLoading={isLoading}
    emptyMessage="No hay tiquetes en el historial de hoy"
    showFooter
  />
);

export default TablaHistorial;