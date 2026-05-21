/**
 * api.js — Capa de acceso a datos centralizada
 * Proyecto Ocean — Sistema de pesaje
 *
 * Reglas:
 * - TODA llamada HTTP del frontend pasa por aquí
 * - Ningún componente importa axios directamente
 * - El backend nunca es tocado desde otro archivo
 * - baseURL apunta a FastAPI en puerto 8000
 */

import axios from "axios";

// ─── Instancia base ───────────────────────────────────────────────────────────

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// ─── Interceptor de request: inyecta token automáticamente ───────────────────

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Interceptor de response: maneja token expirado (401) ────────────────────

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes("/refresh")
    ) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) throw new Error("Sin refresh token");

        const { data } = await axios.post(
          "http://127.0.0.1:8000/refresh",
          {},
          { headers: { Authorization: `Bearer ${refreshToken}` } }
        );

        localStorage.setItem("token", data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch {
        // Refresh falló: limpiar sesión y redirigir a login
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

// ═════════════════════════════════════════════════════════════════════════════
// AUTH
// ═════════════════════════════════════════════════════════════════════════════

export const authAPI = {

  login: (credentials) =>
    api.post(
      "/autenticacion/ingresar",
      new URLSearchParams({
        username: credentials.username,
        password: credentials.password,
      }),
      { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
    ),

  logout: () => Promise.resolve(),  // no existe en backend, no-op

  refresh: () => {
    const refreshToken = localStorage.getItem("refresh_token");
    return axios.post(
      "http://127.0.0.1:8000/autenticacion/refrescar",
      { refresh_token: refreshToken }   // body JSON, no header
    );
  },
};

// ═════════════════════════════════════════════════════════════════════════════
// REGISTROS
// ═════════════════════════════════════════════════════════════════════════════

export const registrosAPI = {
  /** Lista de registros en tránsito */
  getRegistros: () => api.get("/obtener_registros"),

  /** Próximo ID disponible para registro y tiquete */
  getProximoId: () => api.get("/obtener_proximo_id"),

  /**
   * Crear registro vacío al abrir el formulario
   * @param {{ tipo_id: number, fecha_entrada: string, hora_entrada: string }} data
   */
  crearRegistro: (data) => api.post("/crear_registro", data),

  /**
   * Guardar datos completos del registro (PUT)
   * @param {number} id
   * @param {object} data
   */
  procesarRegistro: (id, data) => api.put(`/procesar_registro/${id}`, data),

  /**
   * Bloquear registro para edición exclusiva
   * @param {number} id
   * @param {string} userId
   */
  abrirRegistro: (id, userId) =>
    api.post(`/abrir_registro/${id}`, { user_id: userId }),

  /**
   * Liberar bloqueo de registro
   * @param {number} id
   * @param {string} userId
   */
  cerrarRegistro: (id, userId) =>
    api.post(`/cerrar_registro/${id}`, { user_id: userId }),
};

// ═════════════════════════════════════════════════════════════════════════════
// TIQUETES
// ═════════════════════════════════════════════════════════════════════════════

export const tiquetesAPI = {
  /** Historial de tiquetes diarios */
  getTiquetesDiarios: () => api.get("/obtener_tiquetes_diarios"),

  /**
   * Finalizar registro y crear tiquete
   * @param {object} data
   */
  guardarTiquete: (data) => api.post("/guardar_tiquete", data),

  /**
   * Actualizar tiquete existente
   * @param {number} id
   * @param {object} data
   */
  actualizarTiquete: (id, data) => api.put(`/actualizar_tiquete/${id}`, data),

  /**
   * Obtener datos completos de un tiquete para generar PDF en frontend
   * @param {number} tiqueteId
   */
  getDatosTiquete: (tiqueteId) =>
    api.get(`/imprimir_tiquete?tiquete_id=${tiqueteId}`),

  /**
   * Bloquear tiquete para edición exclusiva
   * @param {number} id
   * @param {string} userId
   */
  abrirTiquete: (id, userId) =>
    api.post(`/abrir_tiquete/${id}`, { user_id: userId }),

  /**
   * Liberar bloqueo de tiquete
   * @param {number} id
   * @param {string} userId
   */
  cerrarTiquete: (id, userId) =>
    api.post(`/cerrar_tiquete/${id}`, { user_id: userId }),
};

// ═════════════════════════════════════════════════════════════════════════════
// CATÁLOGOS — Listas para selects
// ═════════════════════════════════════════════════════════════════════════════

/**
 * @param {boolean} incluirInactivos
 * @returns {string} query param
 */
const inactivosParam = (incluirInactivos) =>
  `?incluir_inactivos=${incluirInactivos ? "true" : "false"}`;

export const catalogosAPI = {
  // Productos
  getProductosEntrada: (incluirInactivos = false) =>
    api.get(`/productos_entrada${inactivosParam(incluirInactivos)}`),

  getProductosSalida: (incluirInactivos = false) =>
    api.get(`/productos_salida${inactivosParam(incluirInactivos)}`),

  getProductosEntradaSalida: (incluirInactivos = false) =>
    api.get(`/productos_entrada_salida${inactivosParam(incluirInactivos)}`),

  getServicios: (incluirInactivos = false) =>
    api.get(`/servicios${inactivosParam(incluirInactivos)}`),

  crearProducto: (data) => api.post("/crear_producto", data),
  crearServicio: (data) => api.post("/crear_servicio", data),

  // Entidades
  getProveedores: (incluirInactivos = false) =>
    api.get(`/proveedores${inactivosParam(incluirInactivos)}`),

  getClientes: (incluirInactivos = false) =>
    api.get(`/clientes${inactivosParam(incluirInactivos)}`),

  getTerceros: (incluirInactivos = false) =>
    api.get(`/terceros${inactivosParam(incluirInactivos)}`),

  getCompradores: () => api.get("/compradores"),
  getTransportadoras: () => api.get("/transportadoras"),

  crearProveedor: (data) => api.post("/crear_proveedor", data),
  crearCliente: (data) => api.post("/crear_cliente", data),
  crearTercero: (data) => api.post("/crear_terceros", data),
  crearComprador: (data) => api.post("/crear_comprador", data),
  crearTransportadora: (data) => api.post("/crear_transportadora", data),

  // Lugares
  getPatios: () => api.get("/patios"),
  getOrigenes: () => api.get("/origenes"),
  getDestinos: () => api.get("/destinos"),
  getUnidades: () => api.get("/unidades"),

  crearPatio: (data) => api.post("/crear_patio", data),
  crearOrigen: (data) => api.post("/crear_origen", data),
  crearDestino: (data) => api.post("/crear_destino", data),
};

// ═════════════════════════════════════════════════════════════════════════════
// VEHÍCULOS, CONDUCTORES, TRAILERS
// ═════════════════════════════════════════════════════════════════════════════

export const vehiculosAPI = {
  getVehiculos: () => api.get("/vehiculos"),
  getVehiculoPorPlaca: (placa) =>
    api.get(`/vehiculo?vehi_placa=${placa}`),

  getTrailers: () => api.get("/trailers"),
  getTrailerPorTrailer: (trailer) =>
    api.get(`/trailer?trai_trailer=${trailer}`),

  getConductores: () => api.get("/conductores"),
  getConductorPorNombre: (nombre) =>
    api.get(`/conductor?conduct_nombre=${nombre}`),
  getConductorPorCedula: (cedula) =>
    api.get(`/conductor?conduct_cedula=${cedula}`),
};

// ═════════════════════════════════════════════════════════════════════════════
// FACTURAS
// ═════════════════════════════════════════════════════════════════════════════

export const facturasAPI = {
  getFacturas: () => api.get("/facturas"),
  getFacturaPorNumero: (numeroFactura) =>
    api.get(`/factura?numero_factura=${numeroFactura}`),
};

// ═════════════════════════════════════════════════════════════════════════════
// BÁSCULA
// ═════════════════════════════════════════════════════════════════════════════

export const basculaAPI = {
  /** Obtener lectura actual de peso desde el hardware */
  getPeso: () => api.get("/obtener_peso"),
};

// ═════════════════════════════════════════════════════════════════════════════
// DASHBOARD / MÉTRICAS  (para Inicio.jsx)
// ═════════════════════════════════════════════════════════════════════════════

export const dashboardAPI = {
  /**
   * Estos endpoints deben existir en FastAPI.
   * Si no existen aún, se construyen a partir de los datos disponibles
   * en el frontend combinando getTiquetesDiarios + getRegistros.
   * Se deja la estructura lista para cuando el backend los implemente.
   */
  getResumenDiario: () => api.get("/dashboard/resumen_diario"),
  getResumenSemanal: () => api.get("/dashboard/resumen_semanal"),
  getResumenMensual: () => api.get("/dashboard/resumen_mensual"),
};

export default api;