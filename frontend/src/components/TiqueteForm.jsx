/**
 * TiqueteForm.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Componente central que orquesta:
 *   - Creación / finalización / actualización de registros y tiquetes
 *   - Bloqueo concurrente (abrir/cerrar registro y tiquete)
 *   - Selección de vehículo, conductor, trailer, factura
 *   - Delegación a IngresoForm / DespachoForm / ServiciosForm
 *   - Generación de PDF desde el frontend (via prop onImprimirTiquete)
 *
 * Sin axios directo — todo via api.js
 * Sin Tailwind — todo via TiqueteForm.css
 * Sin heroicons — Bootstrap Icons
 */

import React, { useState, useEffect, useRef, useCallback } from "react";
import moment from "moment-timezone";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

import FormSection   from "./FormSection";
import SelectField   from "./Layouts/SelectField";
import InputField    from "./Layouts/InputField";
import IngresoForm   from "./IngresoForm";
import DespachoForm  from "./DespachoForm";
import ServiciosForm from "./ServiciosForm";
import Notification  from "./Layouts/Notificacion";

import {
  registrosAPI,
  tiquetesAPI,
  catalogosAPI,
  vehiculosAPI,
  facturasAPI,
  basculaAPI,
} from "../api/api";

import "./TiqueteForm.css";

// ── Opciones de tipo de formulario ────────────────────────────────────────────
const FORM_TYPE_OPTIONS = [
  { value: "",         label: "Seleccione un tipo" },
  { value: "INGRESO",  label: "Ingreso"  },
  { value: "DESPACHO", label: "Despacho" },
  { value: "SERVICIOS",label: "Servicios"},
];

// ═════════════════════════════════════════════════════════════════════════════

const TiqueteForm = ({ formType: initialFormType = "", initialData = {} }) => {
  const location  = useLocation();
  const navigate  = useNavigate();
  const { getToken, userId } = useAuth();

  // ── Estado del tipo de formulario ────────────────────────────────────────
  const [formType, setFormType] = useState(
    location.state?.formType || initialFormType || ""
  );

  // ── Flags de modo ────────────────────────────────────────────────────────
  const isFinalizing = location.state?.isFinalizing || false;
  const isHistorial  = location.state?.isHistorial  || false;
  const isTiquete    = location.state?.isTiquete    || false;

  // ── IDs ──────────────────────────────────────────────────────────────────
  const [ticketNumber,      setTicketNumber]      = useState(initialData.registro  || "");
  const [ticketNumberFinal, setTicketNumberFinal] = useState(initialData.tiquete   || "");

  // ── Vehículo / Conductor / Trailer / Factura ─────────────────────────────
  const [vehicleInfo,  setVehicleInfo]  = useState({ placa: initialData.placa || "", vehi_id: null });
  const [conductInfo,  setConductInfo]  = useState({
    conductor:       initialData.conductor       || "",
    cedulaConductor: initialData.cedulaConductor || "",
    conduct_id:      initialData.conduct_id      || null,
  });
  const [trailerInfo,  setTrailerInfo]  = useState({ trailer: initialData.trailer || "", trai_id: null });
  const [facturaInfo,  setFacturaInfo]  = useState({ numero_factura: initialData.numero_factura || "", fac_id: null });

  // ── Opciones de selects de vehículo ─────────────────────────────────────
  const [vehicleOptions,   setVehicleOptions]   = useState([]);
  const [conductorOptions, setConductorOptions] = useState([]);
  const [conductores,      setConductores]      = useState([]);
  const [cedulaOptions,    setCedulaOptions]    = useState([]);
  const [trailerOptions,   setTrailerOptions]   = useState([]);
  const [facturaOptions,   setFacturaOptions]   = useState([]);

  // ── Catálogos por formType ───────────────────────────────────────────────
  const [productos,       setProductos]       = useState([]);
  const [servicios,       setServicios]       = useState([]);
  const [clientes,        setClientes]        = useState([]);
  const [proveedores,     setProveedores]     = useState([]);
  const [terceros,        setTerceros]        = useState([]);
  const [compradores,     setCompradores]     = useState([]);
  const [transportadoras, setTransportadoras] = useState([]);
  const [destinos,        setDestinos]        = useState([]);
  const [origenes,        setOrigenes]        = useState([]);
  const [patios,          setPatios]          = useState([]);
  const [unidades,        setUnidades]        = useState([]);

  // ── Pesos ────────────────────────────────────────────────────────────────
  const [peso, setPeso] = useState({
    tara:  initialData.pesoTara  || "",
    bruto: initialData.pesoBruto || "",
    neto:  initialData.pesoNeto  || "",
  });

  // ── Fechas y horas ───────────────────────────────────────────────────────
  const [currentDate,  setCurrentDate]  = useState("");
  const [currentTime,  setCurrentTime]  = useState("");
  const [fechaEntrada, setFechaEntrada] = useState(initialData.fEntrada || "");
  const [horaEntrada,  setHoraEntrada]  = useState(initialData.hEntrada || "");
  const [fechaSalida,  setFechaSalida]  = useState(initialData.fSalida  || "");
  const [horaSalida,   setHoraSalida]   = useState(initialData.hSalida  || "");

  // ── Otros ────────────────────────────────────────────────────────────────
  const [observaciones,      setObservaciones]      = useState(initialData.observaciones || "");
  const [isProcessing,       setIsProcessing]       = useState(false);
  const [isTiqueteFinalizado,setIsTiqueteFinalizado]= useState(false);
  const [notif,              setNotif]              = useState({ message: "", type: "" });

  // ── Refs de subformularios ───────────────────────────────────────────────
  const ingresoFormRef  = useRef();
  const despachoFormRef = useRef();
  const servicioFormRef = useRef();

  // Evitar crear el registro dos veces
  const registroCreadoRef = useRef(false);

  // ── Hora actual (Bogotá) ─────────────────────────────────────────────────
  useEffect(() => {
    const now = moment().tz("America/Bogota");
    setCurrentDate(now.format("YYYY-MM-DD"));
    setCurrentTime(now.format("HH:mm"));
  }, []);

  // ── Calcular peso neto ───────────────────────────────────────────────────
  useEffect(() => {
    const tara  = Number(peso.tara)  || 0;
    const bruto = Number(peso.bruto) || 0;
    setPeso((prev) => ({ ...prev, neto: bruto - tara }));
  }, [peso.tara, peso.bruto]);

  // ── Fetch catálogos por tipo ─────────────────────────────────────────────
  useEffect(() => {
    if (!formType) return;

    const incluirInactivos = isFinalizing || isHistorial || isTiquete;

    const fetchCatalogos = async () => {
      try {
        if (formType === "INGRESO") {
          const [prodE, prodES, prov, patioR, comp, dest, orig] = await Promise.all([
            catalogosAPI.getProductosEntrada(incluirInactivos),
            catalogosAPI.getProductosEntradaSalida(incluirInactivos),
            catalogosAPI.getProveedores(incluirInactivos),
            catalogosAPI.getPatios(),
            catalogosAPI.getCompradores(),
            catalogosAPI.getDestinos(),
            catalogosAPI.getOrigenes(),
          ]);
          setProductos([...prodE.data, ...prodES.data]);
          setProveedores(prov.data);
          setCompradores(comp.data);
          setPatios(patioR.data);
          setDestinos(dest.data);
          setOrigenes(orig.data);

        } else if (formType === "DESPACHO") {
          const [cli, prodS, prodES, trans, patioR, orig, dest] = await Promise.all([
            catalogosAPI.getClientes(incluirInactivos),
            catalogosAPI.getProductosSalida(incluirInactivos),
            catalogosAPI.getProductosEntradaSalida(incluirInactivos),
            catalogosAPI.getTransportadoras(),
            catalogosAPI.getPatios(),
            catalogosAPI.getOrigenes(),
            catalogosAPI.getDestinos(),
          ]);
          setClientes(cli.data);
          setProductos([...prodS.data, ...prodES.data]);
          setTransportadoras(trans.data);
          setPatios(patioR.data);
          setOrigenes(orig.data);
          setDestinos(dest.data);

        } else if (formType === "SERVICIOS") {
          const [terc, comp, serv, patioR, orig, uni] = await Promise.all([
            catalogosAPI.getTerceros(incluirInactivos),
            catalogosAPI.getCompradores(),
            catalogosAPI.getServicios(incluirInactivos),
            catalogosAPI.getPatios(),
            catalogosAPI.getOrigenes(),
            catalogosAPI.getUnidades(),
          ]);
          setTerceros(terc.data);
          setCompradores(comp.data);
          setServicios(serv.data);
          setPatios(patioR.data);
          setOrigenes(orig.data);
          setUnidades(uni.data);
        }
      } catch (err) {
        setNotif({ message: "Error cargando catálogos: " + err.message, type: "error" });
      }
    };

    fetchCatalogos();
  }, [formType, isFinalizing, isHistorial, isTiquete]);

  // ── Fetch opciones de vehículo/conductor/trailer/factura ─────────────────
  useEffect(() => {
    const fetchOpciones = async () => {
      try {
        const [veh, trail, cond, fact] = await Promise.all([
          vehiculosAPI.getVehiculos(),
          vehiculosAPI.getTrailers(),
          vehiculosAPI.getConductores(),
          facturasAPI.getFacturas(),
        ]);
        setVehicleOptions(veh.data.map((v) => ({ value: v.id, label: v.placa })));
        setTrailerOptions(trail.data.map((t) => ({ value: t.id, label: t.placa })));
        setConductores(cond.data);
        setConductorOptions(cond.data.map((c) => ({ value: c.id, label: c.nombre })));
        setCedulaOptions(cond.data.map((c) => ({ value: c.id, label: c.cedula || "" })));
        setFacturaOptions(fact.data.map((f) => ({ value: f.id, label: f.fecha })));
      } catch (err) {
        console.error("Error cargando opciones de vehículo:", err);
      }
    };
    fetchOpciones();
  }, []);

  // ── Crear registro automáticamente al abrir formulario nuevo ─────────────
  useEffect(() => {
    if (!formType || ticketNumber || isFinalizing || isHistorial || isTiquete) return;
    if (registroCreadoRef.current) return;

    const crearRegistro = async () => {
      try {
        const proximoRes = await registrosAPI.getProximoId();
        setTicketNumber(proximoRes.data.proximo_id_registro);
        setTicketNumberFinal(proximoRes.data.proximo_id_tiquete);

        const createRes = await registrosAPI.crearRegistro({
          tipo_id:      formType === "INGRESO" ? 1 : formType === "DESPACHO" ? 2 : 3,
          fecha_entrada: new Date().toISOString().split("T")[0],
          hora_entrada:  new Date().toLocaleTimeString("en-US", { hour12: false }),
        });
        setTicketNumber(createRes.data.id);
        registroCreadoRef.current = true;
      } catch (err) {
        setNotif({ message: "Error al crear registro: " + err.message, type: "error" });
      }
    };

    crearRegistro();
  }, [formType, ticketNumber, isFinalizing, isHistorial, isTiquete]);

  // ── Abrir/cerrar registro (bloqueo concurrente) ──────────────────────────
  useEffect(() => {
    if (!isFinalizing || !ticketNumber) return;

    const abrir = async () => {
      try {
        const res = await registrosAPI.abrirRegistro(ticketNumber, userId);
        setNotif({
          message: res.data.message === "El registro ya está abierto por este usuario"
            ? "El registro ya está abierto por ti."
            : "Registro abierto.",
          type: "info",
        });
      } catch (err) {
        setNotif({
          message: err.response?.data?.error || "El registro ya está ocupado.",
          type: "error",
        });
        setTimeout(() => navigate("/registro"), 3000);
      }
    };

    abrir();

    return () => {
      if (ticketNumber) {
        registrosAPI.cerrarRegistro(ticketNumber, userId).catch(console.error);
      }
    };
  }, [isFinalizing, ticketNumber, userId, navigate]);

  // ── Abrir/cerrar tiquete (bloqueo concurrente) ───────────────────────────
  useEffect(() => {
    if ((!isHistorial && !isTiquete) || !ticketNumberFinal) return;

    const abrir = async () => {
      try {
        await tiquetesAPI.abrirTiquete(ticketNumberFinal, userId);
        setNotif({ message: "Tiquete abierto.", type: "info" });
      } catch (err) {
        setNotif({
          message: err.response?.data?.error || "El tiquete ya está ocupado.",
          type: "error",
        });
        setTimeout(() => navigate("/registro"), 3000);
      }
    };

    abrir();

    return () => {
      if (ticketNumberFinal) {
        tiquetesAPI.cerrarTiquete(ticketNumberFinal, userId).catch(console.error);
      }
    };
  }, [isHistorial, isTiquete, ticketNumberFinal, userId, navigate]);

  // ── Handlers de vehículo / conductor / trailer / factura ─────────────────
  const handlePlacaChange = (opt) => {
    setVehicleInfo({ placa: opt?.label || "", vehi_id: opt?.value || null });
  };

  const handleTrailerChange = (opt) => {
    setTrailerInfo({ trailer: opt?.label || "", trai_id: opt?.value || null });
  };

  const handleConductorChange = (opt) => {
    const conductor = conductores.find((c) => c.id === opt?.value);
    setConductInfo({
      conductor:       conductor?.nombre || opt?.label || "",
      cedulaConductor: conductor?.cedula || "",
      conduct_id:      opt?.value || null,
    });
  };

  const handleCedulaChange = (opt) => {
    const conductor = conductores.find((c) => c.id === opt?.value);
    setConductInfo({
      conductor:       conductor?.nombre || "",
      cedulaConductor: opt?.label || "",
      conduct_id:      opt?.value || null,
    });
  };

  const handleFacturaChange = (opt) => {
    setFacturaInfo({ numero_factura: opt?.label || "", fac_id: opt?.value || null });
  };

  // ── Handlers de peso ─────────────────────────────────────────────────────
  const handlePesoBrutoChange = (e) => {
    const val = parseInt(e.target.value.replace(/\./g, ""), 10) || "";
    setPeso((p) => ({ ...p, bruto: val }));
  };

  const handlePesoTaraChange = (e) => {
    const val = parseInt(e.target.value.replace(/\./g, ""), 10) || "";
    setPeso((p) => ({ ...p, tara: val }));
  };

  const handleFetchPesoBruto = async () => {
    try {
      const { data } = await basculaAPI.getPeso();
      setPeso((p) => ({ ...p, bruto: data.peso }));
    } catch {
      setNotif({ message: "Error leyendo báscula", type: "error" });
    }
  };

  const handleFetchPesoTara = async () => {
    try {
      const { data } = await basculaAPI.getPeso();
      setPeso((p) => ({ ...p, tara: data.peso }));
    } catch {
      setNotif({ message: "Error leyendo báscula", type: "error" });
    }
  };

  // ── Payload común ────────────────────────────────────────────────────────
  const buildBasePayload = () => ({
    vehi_id:      vehicleInfo.vehi_id,
    conduct_id:   conductInfo.conduct_id,
    trai_id:      trailerInfo.trai_id,
    id_factura:   facturaInfo.fac_id,
    observaciones,
    fecha_entrada: fechaEntrada || initialData.fEntrada || currentDate,
    hora_entrada:  horaEntrada  || initialData.hEntrada || currentTime,
    fecha_salida:  fechaSalida  || currentDate,
    hora_salida:   horaSalida   || currentTime,
    peso_bruto:    peso.bruto,
    peso_tara:     peso.tara,
    peso_neto:     peso.neto,
  });

  // ── Procesar (nuevo registro) ─────────────────────────────────────────────
  const handleSubmitRegistro = useCallback(async (registroData, tipoId) => {
    try {
      await registrosAPI.procesarRegistro(ticketNumber, {
        ...registroData,
        ...buildBasePayload(),
        tipo_id:    tipoId,
        peso_bruto: formType === "DESPACHO" ? null : peso.bruto,
        peso_tara:  formType === "DESPACHO" ? peso.tara : null,
      });
      setNotif({ message: "Registro procesado exitosamente", type: "success" });
    } catch (err) {
      setNotif({
        message: "Error procesando: " + (err.response?.data?.error || err.message),
        type: "error",
      });
    }
  }, [ticketNumber, peso, formType, observaciones, vehicleInfo, conductInfo, trailerInfo, facturaInfo]);

  // ── Finalizar tiquete ─────────────────────────────────────────────────────
  const handleFinalizarTiquete = useCallback(async (finalizarData) => {
    try {
      const res = await tiquetesAPI.guardarTiquete({
        ...finalizarData,
        ...buildBasePayload(),
        id_registro: initialData.id_registro,
        tipo:        initialData.tipo,
      });
      setTicketNumberFinal(res.data.tiquete_id);
      setIsTiqueteFinalizado(true);
      setNotif({ message: "Tiquete guardado exitosamente", type: "success" });
      return res;
    } catch (err) {
      setNotif({
        message: "Error guardando tiquete: " + (err.response?.data?.message || err.message),
        type: "error",
      });
      throw err;
    }
  }, [buildBasePayload, initialData]);

  // ── Actualizar tiquete ────────────────────────────────────────────────────
  const handleActualizarTiquete = useCallback(async (actualizarData) => {
    try {
      await tiquetesAPI.actualizarTiquete(ticketNumberFinal, {
        ...actualizarData,
        ...buildBasePayload(),
        id_registro: initialData.id_registro,
        tipo:        initialData.tipo,
      });
      setNotif({ message: "Tiquete actualizado exitosamente", type: "success" });
    } catch (err) {
      setNotif({
        message: "Error actualizando: " + (err.response?.data?.error || err.message),
        type: "error",
      });
    }
  }, [ticketNumberFinal, buildBasePayload, initialData]);

  // ── Imprimir tiquete (PDF desde frontend) ─────────────────────────────────
  const handleImprimirTiquete = useCallback(async (tiqueteId) => {
    const id = tiqueteId || ticketNumberFinal;
    if (!id) return;
    try {
      const { data } = await tiquetesAPI.getDatosTiquete(id);
      // El PDF se genera en el frontend — navega a la vista de impresión
      navigate("/tiquete/imprimir", { state: { tiquete: data } });
    } catch (err) {
      setNotif({ message: "Error obteniendo datos del tiquete: " + err.message, type: "error" });
    }
  }, [ticketNumberFinal, navigate]);

  // ── Procesar / Finalizar / Actualizar ─────────────────────────────────────
  const handleProcesar = async () => {
    if (isProcessing) return;
    if (!vehicleInfo.vehi_id || !conductInfo.conduct_id) {
      setNotif({ message: "Complete los campos obligatorios: Placa y Conductor", type: "error" });
      return;
    }
    setIsProcessing(true);
    try {
      const ref  = formType === "INGRESO"   ? ingresoFormRef
                 : formType === "DESPACHO"  ? despachoFormRef
                 : servicioFormRef;
      const tipoId = formType === "INGRESO" ? 1 : formType === "DESPACHO" ? 2 : 3;
      ref.current?.handleProcesar();
      const data = ref.current?.getFormData() || {};
      await handleSubmitRegistro(data, tipoId);
      navigate("/registro");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFinalizar = async () => {
    if (isProcessing) return;
    setIsProcessing(true);
    try {
      const ref = formType === "INGRESO"   ? ingresoFormRef
                : formType === "DESPACHO"  ? despachoFormRef
                : servicioFormRef;
      const data = ref.current?.getFormData() || {};
      await registrosAPI.cerrarRegistro(ticketNumber, userId);
      await handleFinalizarTiquete(data);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleActualizar = async () => {
    if (isProcessing) return;
    setIsProcessing(true);
    try {
      const ref = formType === "INGRESO"   ? ingresoFormRef
                : formType === "DESPACHO"  ? despachoFormRef
                : servicioFormRef;
      const data = ref.current?.getFormData() || {};
      await tiquetesAPI.cerrarTiquete(ticketNumberFinal, userId);
      await handleActualizarTiquete(data);
    } finally {
      setIsProcessing(false);
    }
  };

  // ── Cerrar / salir ────────────────────────────────────────────────────────
  const handleSalir = async () => {
    if (ticketNumber) {
      await registrosAPI.cerrarRegistro(ticketNumber, userId).catch(console.error);
    }
    navigate("/registro");
  };

  // ── Label del botón principal ─────────────────────────────────────────────
  const btnLabel = isFinalizing  ? "Finalizar Tiquete"
                 : isHistorial || isTiquete ? "Actualizar Tiquete"
                 : "Procesar";

  const btnAction = isFinalizing          ? handleFinalizar
                  : isHistorial || isTiquete ? handleActualizar
                  : handleProcesar;

  // ─────────────────────────────────────────────────────────────────────────
  return (
    <div className="tiquete">

      {/* ── Barra superior: IDs + Tipo + Factura ── */}
      <div className="tiquete__topbar">
        {/* Registro */}
        <div className="tiquete__id-group">
          <span className="tiquete__id-label">Registro</span>
          <span className="tiquete__id-value">{ticketNumber || "—"}</span>
          {(isHistorial || isTiquete || isFinalizing) && (
            <>
              <span className="tiquete__id-separator" />
              <span className="tiquete__id-label">Tiquete</span>
              <span className="tiquete__id-value">{ticketNumberFinal || "—"}</span>
            </>
          )}
        </div>

        {/* Factura (solo INGRESO) */}
        {formType === "INGRESO" && (
          <SelectField
            label="Facturado"
            id="factura"
            options={facturaOptions}
            value={facturaInfo.fac_id}
            onChange={handleFacturaChange}
          />
        )}

        {/* Tipo */}
        <SelectField
          label="Tipo"
          id="formType"
          options={FORM_TYPE_OPTIONS}
          value={formType}
          onChange={(opt) => setFormType(opt?.value || "")}
          isDisabled={isFinalizing || isHistorial || isTiquete}
        />
      </div>

      {/* ── Datos del vehículo ── */}
      <FormSection title="Datos del Vehículo" icon="bi-truck">
        <div className="tiquete__vehicle-grid">
          <SelectField
            label="Placa"
            id="placa"
            options={vehicleOptions}
            value={vehicleInfo.vehi_id}
            onChange={handlePlacaChange}
          />
          <SelectField
            label="Conductor"
            id="conductor"
            options={conductorOptions}
            value={conductInfo.conduct_id}
            onChange={handleConductorChange}
          />
          <SelectField
            label="Nro. Documento"
            id="cedula"
            options={cedulaOptions}
            value={conductInfo.conduct_id}
            onChange={handleCedulaChange}
          />
          <SelectField
            label="Trailer"
            id="trailer"
            options={trailerOptions}
            value={trailerInfo.trai_id}
            onChange={handleTrailerChange}
          />
        </div>
      </FormSection>

      {/* ── Subformulario según tipo ── */}
      {formType === "INGRESO" && (
        <IngresoForm
          ref={ingresoFormRef}
          productos={productos}
          proveedores={proveedores}
          compradores={compradores}
          patios={patios}
          origenes={origenes}
          pesoBruto={peso.bruto}
          onSubmit={handleSubmitRegistro}
          onFinalizar={handleFinalizarTiquete}
          onActualizar={handleActualizarTiquete}
          handleImprimirTiquete={handleImprimirTiquete}
        />
      )}

      {formType === "DESPACHO" && (
        <DespachoForm
          ref={despachoFormRef}
          clientes={clientes}
          productos={productos}
          transportadoras={transportadoras}
          patios={patios}
          destinos={destinos}
          origenes={origenes}
          pesoBruto={peso.bruto}
          onSubmit={handleSubmitRegistro}
          onFinalizar={handleFinalizarTiquete}
          onActualizar={handleActualizarTiquete}
          handleImprimirTiquete={handleImprimirTiquete}
        />
      )}

      {formType === "SERVICIOS" && (
        <ServiciosForm
          ref={servicioFormRef}
          terceros={terceros}
          servicios={servicios}
          compradores={compradores}
          patios={patios}
          origenes={origenes}
          pesoBruto={peso.bruto}
          onSubmit={handleSubmitRegistro}
          onFinalizar={handleFinalizarTiquete}
          onActualizar={handleActualizarTiquete}
          handleImprimirTiquete={handleImprimirTiquete}
        />
      )}

      {/* ── Báscula ── */}
      <FormSection title="Báscula" icon="bi-speedometer2">
        <div className="tiquete__bascula-grid">
          <InputField
            label="Fecha Entrada"
            id="fechaEntrada"
            type="date"
            value={fechaEntrada || initialData.fEntrada || currentDate}
            onChange={(e) => setFechaEntrada(e.target.value)}
            tabIndex={-1}
          />
          <InputField
            label="Hora Entrada"
            id="horaEntrada"
            type="time"
            value={horaEntrada || initialData.hEntrada || currentTime}
            onChange={(e) => setHoraEntrada(e.target.value)}
            tabIndex={-1}
          />

          {/* Peso Bruto */}
          <InputField
            label="Peso Bruto"
            id="pesoBruto"
            type="number"
            variant="number"
            value={peso.bruto}
            onChange={handlePesoBrutoChange}
            onAction={handleFetchPesoBruto}
            actionIcon="bi-cursor"
            actionTitle="Leer de báscula"
          />

          {/* Despacho: tara + salida */}
          {formType === "DESPACHO" && (
            <>
              <InputField
                label="Peso Tara"
                id="pesoTara"
                type="number"
                variant="number"
                value={peso.tara}
                onChange={handlePesoTaraChange}
                onAction={handleFetchPesoTara}
                actionIcon="bi-cursor"
                actionTitle="Leer de báscula"
              />
              <InputField
                label="Fecha Salida"
                id="fechaSalida"
                type="date"
                value={fechaSalida || initialData.fSalida || currentDate}
                onChange={(e) => setFechaSalida(e.target.value)}
              />
              <InputField
                label="Hora Salida"
                id="horaSalida"
                type="time"
                value={horaSalida || initialData.hSalida || currentTime}
                onChange={(e) => setHoraSalida(e.target.value)}
              />
            </>
          )}

          {/* Historial/tiquete: mostrar salida */}
          {(isHistorial || isTiquete) && formType !== "DESPACHO" && (
            <>
              <InputField
                label="Fecha Salida"
                id="fechaSalida"
                type="date"
                value={fechaSalida || initialData.fSalida || ""}
                onChange={(e) => setFechaSalida(e.target.value)}
              />
              <InputField
                label="Hora Salida"
                id="horaSalida"
                type="time"
                value={horaSalida || initialData.hSalida || ""}
                onChange={(e) => setHoraSalida(e.target.value)}
              />
              <InputField
                label="Peso Tara"
                id="pesoTara"
                type="number"
                variant="number"
                value={peso.tara}
                onChange={handlePesoTaraChange}
                onAction={handleFetchPesoTara}
                actionIcon="bi-cursor"
                actionTitle="Leer de báscula"
              />
            </>
          )}
        </div>

        {/* Peso neto destacado */}
        <div className="tiquete__peso-neto">
          <span className="tiquete__peso-neto-label">Peso Neto</span>
          <span className="tiquete__peso-neto-value">
            {peso.neto ? Number(peso.neto).toLocaleString("es-CO") : "0"}
          </span>
          <span className="tiquete__peso-neto-unit">kg</span>
        </div>
      </FormSection>

      {/* ── Observaciones ── */}
      <FormSection title="Observaciones" icon="bi-chat-left-text">
        <InputField
          id="observaciones"
          isTextarea
          rows={2}
          value={observaciones}
          onChange={(e) => setObservaciones(e.target.value)}
          placeholder="Observaciones adicionales..."
        />
      </FormSection>

      {/* ── Acciones ── */}
      <div className="tiquete__actions">
        <div className="tiquete__actions-left">
          {/* Botón principal */}
          <button
            className={`tiquete__btn ${
              isFinalizing ? "tiquete__btn--success" : "tiquete__btn--primary"
            }`}
            onClick={btnAction}
            disabled={!formType || isProcessing}
          >
            {isProcessing ? (
              <span className="tiquete__btn-spinner" />
            ) : (
              <i className={`bi ${
                isFinalizing ? "bi-check-circle" : "bi-play-circle"
              }`} aria-hidden="true" />
            )}
            {isProcessing ? "Procesando..." : btnLabel}
          </button>

          {/* Imprimir (solo cuando hay tiquete) */}
          {(isHistorial || isFinalizing || isTiquete || isTiqueteFinalizado) && (
            <button
              className="tiquete__btn tiquete__btn--secondary"
              onClick={() => handleImprimirTiquete()}
              disabled={isProcessing}
            >
              <i className="bi bi-printer" aria-hidden="true" />
              Imprimir
            </button>
          )}
        </div>

        <div className="tiquete__actions-right">
          <button
            className="tiquete__btn tiquete__btn--danger"
            onClick={handleSalir}
            disabled={isProcessing}
          >
            <i className="bi bi-box-arrow-left" aria-hidden="true" />
            Salir
          </button>
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

export default TiqueteForm;