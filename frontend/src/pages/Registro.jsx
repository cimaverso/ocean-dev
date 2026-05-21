/**
 * Registro.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Fuente única de datos para tránsito e historial.
 * Filtro.jsx recibe los datos y devuelve los filtrados — no hace fetch propio.
 * Auto-refresh cada 60 segundos mientras la página está abierta.
 */

import React, { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import Sidebar from "../components/Layouts/Sidebar";
import Header from "../components/Layouts/Header";
import FilterSection from "../components/Registro/Filtro";
import TablaTransito from "../components/Registro/Transito";
import TablaHistorial from "../components/Registro/Historial";
import BotonesVista from "../components/Registro/BotonesVista";
import Notification from "../components/Layouts/Notificacion";
import { useAuth } from "../context/AuthContext";
import { registrosAPI, tiquetesAPI } from "../api/api";
import "./Registro.css";

const Registro = () => {
  const navigate          = useNavigate();
  const { userRole }      = useAuth();

  const [viewType,      setViewType]      = useState("transito");
  const [rawData,       setRawData]       = useState([]);
  const [tableData,     setTableData]     = useState([]);
  const [isLoading,     setIsLoading]     = useState(true);
  const [notif,         setNotif]         = useState({ message: "", type: "" });

  // ── Fetch — una sola fuente de verdad ──────────────────────────────────
  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      if (viewType === "transito") {
        const res = await registrosAPI.getRegistros();
        setRawData(Array.isArray(res.data) ? res.data : []);
      } else {
        const res = await tiquetesAPI.getTiquetesDiarios();
        setRawData(Array.isArray(res.data) ? res.data : []);
      }
    } catch (err) {
      setNotif({
        message: "Error al cargar registros: " + (err.message || ""),
        type:    "error",
      });
      setRawData([]);
    } finally {
      setIsLoading(false);
    }
  }, [viewType]);

  // Fetch al cambiar de vista
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Auto-refresh cada 60 segundos
  useEffect(() => {
    const interval = setInterval(fetchData, 60_000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // ── Handlers de vista ──────────────────────────────────────────────────
  const showTransito  = () => setViewType("transito");
  const showHistorial = () => setViewType("historial");

  // ── Doble clic en fila ─────────────────────────────────────────────────
  const handleDoubleClick = useCallback((record) => {
    // Historial solo para administrador
    if (viewType === "historial" && userRole !== "administrador") {
      setNotif({
        message: "Acceso denegado: solo los administradores pueden editar el historial.",
        type:    "error",
      });
      return;
    }

    const tipo = (record.tipo || "").toUpperCase();
    const formTypes = ["INGRESO", "DESPACHO", "SERVICIOS", "SERVICIO"];

    if (!formTypes.includes(tipo)) return;

    const formType = tipo === "SERVICIO" ? "SERVICIOS" : tipo;

    navigate("/formulario", {
      state: {
        record,
        formType,
        isFinalizing: viewType === "transito",
        isHistorial:  viewType === "historial",
      },
    });
  }, [viewType, userRole, navigate]);

  // ── Contadores para los tabs ───────────────────────────────────────────
  const countTransito  = viewType === "transito"  ? rawData.length : null;
  const countHistorial = viewType === "historial" ? rawData.length : null;

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <Header />

        <div className="registro-content">

          {/* ── Toolbar: tabs + botón crear ── */}
          <div className="registro-toolbar">
            <div className="registro-toolbar__left">
              <BotonesVista
                showTransito={showTransito}
                showHistorial={showHistorial}
                viewType={viewType}
                countTransito={countTransito}
                countHistorial={countHistorial}
              />
            </div>

            <div className="registro-toolbar__right">
              <Link
                to="/formulario"
                className="registro-btn-crear"
                aria-label="Crear nuevo ingreso"
              >
                <i className="bi bi-plus-lg" aria-hidden="true" />
                Nuevo Ingreso
              </Link>
            </div>
          </div>

          {/* ── Filtros ── */}
          <FilterSection
            data={rawData}
            onFilter={setTableData}
            isLoading={isLoading}
            onRefresh={fetchData}
            consultaTipo={viewType}
          />

          {/* ── Tabla ── */}
          <div className="registro-tabla">
            {viewType === "transito" ? (
              <TablaTransito
                data={tableData}
                onDoubleClickRow={handleDoubleClick}
                isLoading={isLoading}
              />
            ) : (
              <TablaHistorial
                data={tableData}
                onDoubleClickRow={handleDoubleClick}
                isLoading={isLoading}
              />
            )}
          </div>

        </div>
      </div>

      <Notification
        message={notif.message}
        type={notif.type}
        onClose={() => setNotif({ message: "", type: "" })}
      />
    </div>
  );
};

export default Registro;