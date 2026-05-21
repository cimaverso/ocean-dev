/**
 * Inicio.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Dashboard principal con:
 *   - 4 métricas superiores (ingresos, despachos, tránsito, peso total)
 *   - Gráficas de barras: peso por producto (ingresos) y por destino (despachos)
 *   - Actividad reciente: últimos registros del día
 *   - Accesos rápidos: crear ingreso, despacho, servicio
 *
 * API usada:
 *   dashboardAPI.getResumenDiario() — si no existe en el backend,
 *   se construye con registrosAPI.getRegistros() + tiquetesAPI.getTiquetesDiarios()
 */

import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import Sidebar from "../components/Layouts/Sidebar";
import Header from "../components/Layouts/Header";
import TarjetaInicio from "../components/Layouts/TarjetaInicio";
import Notification from "../components/Layouts/Notificacion";
import { useAuth } from "../context/AuthContext";
import { registrosAPI, tiquetesAPI } from "../api/api";
import "./Inicio.css";

// ── Helpers ───────────────────────────────────────────────────────────────────

const formatPeso = (kg) => {
  if (!kg && kg !== 0) return "0";
  return Number(kg).toLocaleString("es-CO");
};

const formatFecha = () => {
  return new Date().toLocaleDateString("es-CO", {
    weekday: "long",
    year:    "numeric",
    month:   "long",
    day:     "numeric",
  });
};

const capitalizar = (str = "") =>
  str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();

// ── Gráfica de barras ─────────────────────────────────────────────────────────
const BarChart = ({ data = [], color, emptyMessage }) => {
  if (data.length === 0) {
    return (
      <div className="dashboard__empty">
        <i className="bi bi-bar-chart" />
        <span>{emptyMessage}</span>
      </div>
    );
  }

  const max = Math.max(...data.map((d) => d.raw), 1);

  return (
    <div className="dashboard__bars">
      {data.map((item, i) => (
        <div key={i} className="dashboard__bar-row">
          <span className="dashboard__bar-label" title={item.label}>
            {item.label}
          </span>
          <div className="dashboard__bar-track">
            <div
              className="dashboard__bar-fill"
              style={{
                width: `${(item.raw / max) * 100}%`,
                "--bar-color": color,
              }}
            />
          </div>
          <span className="dashboard__bar-value">
            {formatPeso(item.raw)} kg
          </span>
        </div>
      ))}
    </div>
  );
};

// ── Actividad reciente ────────────────────────────────────────────────────────
const ActividadItem = ({ registro }) => {
  const tipo  = (registro.tipo || "").toLowerCase();
  const hora  = registro.hEntrada || registro.hora_entrada || "—";
  const peso  = registro.pesoBruto || registro.peso_bruto || registro.peso;
  const placa = registro.placa || "—";

  return (
    <div className="dashboard__activity-item">
      <div className={`dashboard__activity-dot dashboard__activity-dot--${tipo}`} />
      <div className="dashboard__activity-info">
        <div className="dashboard__activity-placa">{placa}</div>
        <div className="dashboard__activity-tipo">{capitalizar(tipo)}</div>
      </div>
      <div className="dashboard__activity-meta">
        {peso ? (
          <span className="dashboard__activity-peso">
            {formatPeso(peso)} kg
          </span>
        ) : null}
        <span className="dashboard__activity-hora">{hora}</span>
      </div>
    </div>
  );
};

// ═════════════════════════════════════════════════════════════════════════════

const Inicio = () => {
  const { userName } = useAuth();

  const [isLoading, setIsLoading] = useState(true);
  const [notif,     setNotif]     = useState({ message: "", type: "" });

  // Datos
  const [registros,  setRegistros]  = useState([]);
  const [tiquetes,   setTiquetes]   = useState([]);

  // ── Fetch ──────────────────────────────────────────────────────────────
  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [regRes, tiqRes] = await Promise.all([
        registrosAPI.getRegistros(),
        tiquetesAPI.getTiquetesDiarios(),
      ]);
      setRegistros(Array.isArray(regRes.data)  ? regRes.data  : []);
      setTiquetes(Array.isArray(tiqRes.data)   ? tiqRes.data  : []);
    } catch (err) {
      setNotif({ message: "Error al cargar datos del dashboard", type: "error" });
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    // Refrescar cada 2 minutos
    const interval = setInterval(fetchData, 120_000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // ── Métricas calculadas ─────────────────────────────────────────────────
  const hoy = new Date().toISOString().slice(0, 10);

  const tiquetesHoy = tiquetes.filter(
    (t) => (t.fEntrada || t.fecha_entrada || "").slice(0, 10) === hoy
  );

  const ingresosHoy  = tiquetesHoy.filter((t) => (t.tipo || "").toUpperCase() === "INGRESO");
  const despachosHoy = tiquetesHoy.filter((t) => (t.tipo || "").toUpperCase() === "DESPACHO");
  const serviciosHoy = tiquetesHoy.filter((t) => (t.tipo || "").toUpperCase() === "SERVICIOS");

  const transitoActual = registros.filter(
    (r) => (r.estado || "").toUpperCase() === "TRANSITO"
  );

  const pesoTotalNeto = tiquetesHoy.reduce(
    (sum, t) => sum + (Number(t.pesoNeto || t.peso_neto) || 0), 0
  );

  // ── Datos para gráficas ─────────────────────────────────────────────────
  // Ingresos por producto
  const ingPorProducto = Object.entries(
    ingresosHoy.reduce((acc, t) => {
      const key = t.producto?.nombreProducto || t.nombre_producto || "Sin nombre";
      acc[key]  = (acc[key] || 0) + (Number(t.pesoNeto || t.peso_neto) || 0);
      return acc;
    }, {})
  )
    .map(([label, raw]) => ({ label, raw }))
    .sort((a, b) => b.raw - a.raw)
    .slice(0, 6);

  // Despachos por destino
  const despPorDestino = Object.entries(
    despachosHoy.reduce((acc, t) => {
      const key = t.destino?.nombreDestino || t.nombre_destino || "Sin destino";
      acc[key]  = (acc[key] || 0) + (Number(t.pesoNeto || t.peso_neto) || 0);
      return acc;
    }, {})
  )
    .map(([label, raw]) => ({ label, raw }))
    .sort((a, b) => b.raw - a.raw)
    .slice(0, 6);

  // Actividad reciente: mezcla registros + tiquetes, últimos 8
  const actividadReciente = [...tiquetesHoy, ...transitoActual]
    .sort((a, b) => {
      const ta = a.hEntrada || a.hora_entrada || "";
      const tb = b.hEntrada || b.hora_entrada || "";
      return tb.localeCompare(ta);
    })
    .slice(0, 8);

  // ── Nombre para saludo ───────────────────────────────────────────────────
  const primerNombre = (userName || "").split(" ")[0] || "Usuario";

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <Header />

        <main className="dashboard" aria-label="Dashboard principal">
          {/* ── Encabezado ── */}
          <div className="dashboard__header">
            <div className="dashboard__greeting">
              <span className="dashboard__greeting-label">Panel de control</span>
              <h1 className="dashboard__greeting-title">
                Hola, {primerNombre}
              </h1>
            </div>
            <div className="dashboard__date">
              <i className="bi bi-calendar3" aria-hidden="true" />
              {capitalizar(formatFecha())}
            </div>
          </div>

          {/* ── Métricas superiores ── */}
          <div className="dashboard__metrics">
            <TarjetaInicio
              label="Ingresos hoy"
              value={isLoading ? "—" : ingresosHoy.length}
              unit="registros"
              icon="bi-arrow-down-circle"
              variant="ingreso"
              trendLabel="del día"
              isLoading={isLoading}
            />
            <TarjetaInicio
              label="Despachos hoy"
              value={isLoading ? "—" : despachosHoy.length}
              unit="registros"
              icon="bi-arrow-up-circle"
              variant="despacho"
              trendLabel="del día"
              isLoading={isLoading}
            />
            <TarjetaInicio
              label="En tránsito"
              value={isLoading ? "—" : transitoActual.length}
              unit="vehículos"
              icon="bi-truck"
              variant="transito"
              trendLabel="en este momento"
              isLoading={isLoading}
            />
            <TarjetaInicio
              label="Peso neto total"
              value={isLoading ? "—" : formatPeso(pesoTotalNeto)}
              unit="kg"
              icon="bi-speedometer2"
              variant="peso"
              trendLabel="acumulado hoy"
              isLoading={isLoading}
            />
          </div>

          {/* ── Gráficas + Actividad reciente ── */}
          <div className="dashboard__grid-2">

            {/* Gráficas */}
            <div className="dashboard__section">
              {/* Ingresos por producto */}
              <div className="dashboard__chart">
                <div className="dashboard__chart-title">
                  <i className="bi bi-arrow-down-circle" aria-hidden="true" />
                  Ingresos por producto — hoy
                </div>
                <BarChart
                  data={ingPorProducto}
                  color="var(--info)"
                  emptyMessage="Sin ingresos registrados hoy"
                />
              </div>

              {/* Despachos por destino */}
              <div className="dashboard__chart">
                <div className="dashboard__chart-title">
                  <i className="bi bi-arrow-up-circle" aria-hidden="true" />
                  Despachos por destino — hoy
                </div>
                <BarChart
                  data={despPorDestino}
                  color="var(--warning)"
                  emptyMessage="Sin despachos registrados hoy"
                />
              </div>
            </div>

            {/* Actividad reciente */}
            <div className="dashboard__section">
              <div className="dashboard__section-header">
                <h2 className="dashboard__section-title">
                  <i className="bi bi-clock-history" aria-hidden="true" />
                  Actividad reciente
                </h2>
                {!isLoading && (
                  <span className="dashboard__section-badge">
                    {actividadReciente.length} registros
                  </span>
                )}
              </div>

              <div className="dashboard__activity">
                <div className="dashboard__activity-header">
                  <i className="bi bi-list-ul" aria-hidden="true" />
                  Últimos movimientos del día
                </div>

                <div className="dashboard__activity-list">
                  {isLoading ? (
                    Array.from({ length: 5 }).map((_, i) => (
                      <div key={i} className="dashboard__activity-item">
                        <div className="skeleton" style={{ width: 8, height: 8, borderRadius: "50%" }} />
                        <div className="dashboard__activity-info">
                          <div className="skeleton" style={{ width: "60%", height: 12, marginBottom: 4 }} />
                          <div className="skeleton" style={{ width: "35%", height: 10 }} />
                        </div>
                      </div>
                    ))
                  ) : actividadReciente.length === 0 ? (
                    <div className="dashboard__empty">
                      <i className="bi bi-inbox" />
                      <span>Sin actividad registrada hoy</span>
                    </div>
                  ) : (
                    actividadReciente.map((reg, i) => (
                      <ActividadItem key={reg.id ?? reg.registro ?? i} registro={reg} />
                    ))
                  )}
                </div>
              </div>

              {/* Accesos rápidos */}
              <div className="dashboard__section-header">
                <h2 className="dashboard__section-title">
                  <i className="bi bi-lightning" aria-hidden="true" />
                  Acceso rápido
                </h2>
              </div>

              <div className="dashboard__quick-actions">
                <Link
                  to="/formulario"
                  state={{ formType: "INGRESO" }}
                  className="dashboard__quick-btn dashboard__quick-btn--primary"
                >
                  <i className="bi bi-arrow-down-circle" aria-hidden="true" />
                  Nuevo Ingreso
                </Link>
                <Link
                  to="/formulario"
                  state={{ formType: "DESPACHO" }}
                  className="dashboard__quick-btn dashboard__quick-btn--secondary"
                >
                  <i className="bi bi-arrow-up-circle" aria-hidden="true" />
                  Nuevo Despacho
                </Link>
                <Link
                  to="/formulario"
                  state={{ formType: "SERVICIOS" }}
                  className="dashboard__quick-btn dashboard__quick-btn--secondary"
                >
                  <i className="bi bi-gear" aria-hidden="true" />
                  Nuevo Servicio
                </Link>
              </div>
            </div>
          </div>
        </main>
      </div>

      <Notification
        message={notif.message}
        type={notif.type}
        onClose={() => setNotif({ message: "", type: "" })}
      />
    </div>
  );
};

export default Inicio;