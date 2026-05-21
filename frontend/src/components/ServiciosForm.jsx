/**
 * ServiciosForm.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Subformulario para registros de tipo SERVICIOS.
 * Sin fetch propio — catálogos vienen de TiqueteForm via props.
 */

import React, {
  useState,
  forwardRef,
  useImperativeHandle,
  useEffect,
} from "react";
import { useLocation } from "react-router-dom";
import SelectField  from "./Layouts/SelectField";
import FormSection  from "./FormSection";
import Notification from "./Layouts/Notificacion";
import { catalogosAPI } from "../api/api";
import "./SubForm.css";

const ServiciosForm = forwardRef((
  {
    servicios   = [],
    terceros    = [],
    compradores = [],
    patios      = [],
    origenes    = [],
    pesoBruto,
    onSubmit,
    onFinalizar,
    onActualizar,
    handleImprimirTiquete,
  },
  ref
) => {
  const location    = useLocation();
  const initialData = location.state?.record || {};

  const [selectedTercero,  setSelectedTercero]  = useState("");
  const [selectedComprador,setSelectedComprador] = useState("");
  const [selectedServicio, setSelectedServicio]  = useState("");
  const [selectedOrigen,   setSelectedOrigen]    = useState("");
  const [selectedPatio,    setSelectedPatio]     = useState("");
  const [unidad,           setUnidad]            = useState("");
  const [cantidad,         setCantidad]          = useState("");
  const [observaciones,    setObservaciones]     = useState("");
  const [notif,            setNotif]             = useState({ message: "", type: "" });

  // ── Autocompletar ────────────────────────────────────────────────────────
  useEffect(() => {
    if (!initialData || Object.keys(initialData).length === 0) return;

    const terc = terceros.find((t) => t.codigo_entidad === initialData?.entidad?.codigoEntidad);
    const comp = compradores.find((c) => c.codigo_comprador === initialData?.comprador?.codigoComprador);
    const serv = servicios.find((s) => s.codigo_producto === initialData?.producto?.codigoProducto);
    const orig = origenes.find((o) => o.codigo_origen === initialData?.origen?.codigoOrigen);
    const pati = patios.find((p) => p.codigo_patio === initialData?.patio?.codigoPatio);

    if (terc) setSelectedTercero(terc.id_entidad);
    if (comp) setSelectedComprador(comp.id_comprador);
    if (serv) { setSelectedServicio(serv.id_producto); setUnidad(serv.unidad_medida || ""); }
    if (orig) setSelectedOrigen(orig.id_origen);
    if (pati) setSelectedPatio(pati.id_patio);
    setCantidad(initialData.cantidad    || "");
    setObservaciones(initialData.observaciones || "");
  }, [initialData, terceros, compradores, servicios, origenes, patios]);

  // Actualizar unidad cuando cambia el servicio seleccionado
  useEffect(() => {
    const serv = servicios.find((s) => s.id_producto === selectedServicio);
    setUnidad(serv?.unidad_medida || "");
  }, [selectedServicio, servicios]);

  // ── Opciones ─────────────────────────────────────────────────────────────
  const optsTercero    = terceros.map((t)    => ({ value: t.id_entidad,   label: t.nombre_entidad    }));
  const optsTercCodigo = terceros.map((t)    => ({ value: t.id_entidad,   label: t.codigo_entidad    }));
  const optsComprador  = compradores.map((c) => ({ value: c.id_comprador, label: c.nombre_comprador  }));
  const optsCompCodigo = compradores.map((c) => ({ value: c.id_comprador, label: c.codigo_comprador  }));
  const optsServicio   = servicios.map((s)   => ({ value: s.id_producto,  label: s.nombre_producto   }));
  const optsServCodigo = servicios.map((s)   => ({ value: s.id_producto,  label: s.codigo_producto   }));
  const optsOrigen     = origenes.map((o)    => ({ value: o.id_origen,    label: o.nombre_origen     }));
  const optsPatio      = patios.map((p)      => ({ value: p.id_patio,     label: p.nombre_patio      }));

  // ── onAddNew ─────────────────────────────────────────────────────────────
  const onAddTercero   = async (d) => { const r = await catalogosAPI.crearTercero(d);   return { value: r.data.id_entidad,   label: r.data.nombre_entidad   }; };
  const onAddComprador = async (d) => { const r = await catalogosAPI.crearComprador(d); return { value: r.data.id_comprador, label: r.data.nombre_comprador }; };
  const onAddServicio  = async (d) => { const r = await catalogosAPI.crearServicio(d);  return { value: r.data.id_producto,  label: r.data.nombre_producto  }; };
  const onAddOrigen    = async (d) => { const r = await catalogosAPI.crearOrigen(d);    return { value: r.data.id_origen,    label: r.data.nombre_origen    }; };
  const onAddPatio     = async (d) => { const r = await catalogosAPI.crearPatio(d);     return { value: r.data.id_patio,     label: r.data.nombre_patio     }; };

  // ── Handlers ─────────────────────────────────────────────────────────────
  const handleTerceroChange   = (opt) => setSelectedTercero(opt?.value   ?? "");
  const handleCompradorChange = (opt) => setSelectedComprador(opt?.value ?? "");
  const handleServicioChange  = (opt) => setSelectedServicio(opt?.value  ?? "");
  const handleOrigenChange    = (opt) => setSelectedOrigen(opt?.value    ?? "");
  const handlePatioChange     = (opt) => setSelectedPatio(opt?.value     ?? "");

  // ── getFormData ──────────────────────────────────────────────────────────
  const getFormData = () => ({
    ent_id:    selectedTercero,
    prod_id:   selectedServicio,
    comp_id:   selectedComprador,
    id_patio:  selectedPatio,
    id_origen: selectedOrigen,
    cantidad,
    observaciones,
    tipo:      initialData.tipo,
  });

  // ── handleProcesar ───────────────────────────────────────────────────────
  const handleProcesar = () => {
    if (selectedServicio && selectedTercero && selectedComprador &&
        selectedOrigen && selectedPatio && pesoBruto) {
      onSubmit?.({ ...getFormData(), estado: "TRANSITO" }, 3);
    }
  };

  // ── handleFinalizar ──────────────────────────────────────────────────────
  const handleFinalizar = async () => {
    const data = {
      ...getFormData(),
      fecha_salida: new Date().toISOString().slice(0, 10),
      hora_salida:  new Date().toTimeString().slice(0, 8),
    };
    try {
      const response = await onFinalizar?.(data);
      if (response?.data?.tiquete_id) {
        handleImprimirTiquete?.(response.data.tiquete_id);
      }
    } catch (err) {
      setNotif({
        message: "Error al finalizar: " + (err.response?.data?.error || err.message),
        type: "error",
      });
    }
  };

  // ── handleActualizar ─────────────────────────────────────────────────────
  const handleActualizar = () => {
    if (selectedServicio && selectedTercero && selectedComprador &&
        selectedOrigen && selectedPatio) {
      onActualizar?.({ tiquete_id: initialData.id, ...getFormData() });
    }
  };

  useImperativeHandle(ref, () => ({
    handleProcesar,
    handleFinalizar,
    handleActualizar,
    getFormData,
  }));

  return (
    <div className="subform">
      {/* ── Tercero / Comprador ── */}
      <div className="subform__grid-2">
        <FormSection title="Tercero" icon="bi-person">
          <SelectField
            label="Nombre"
            id="nombreTercero"
            options={optsTercero}
            value={selectedTercero}
            onChange={handleTerceroChange}
            onAddNew={onAddTercero}
            addNewFields={[
              { key: "nombre", label: "Nombre" },
              { key: "codigo", label: "Código" },
            ]}
          />
          <SelectField
            label="Código"
            id="codigoTercero"
            options={optsTercCodigo}
            value={selectedTercero}
            onChange={handleTerceroChange}
          />
        </FormSection>

        <FormSection title="Comprador" icon="bi-person-check">
          <SelectField
            label="Nombre"
            id="nombreComprador"
            options={optsComprador}
            value={selectedComprador}
            onChange={handleCompradorChange}
            onAddNew={onAddComprador}
            addNewFields={[
              { key: "nombre", label: "Nombre" },
              { key: "codigo", label: "Código" },
            ]}
          />
          <SelectField
            label="Código"
            id="codigoComprador"
            options={optsCompCodigo}
            value={selectedComprador}
            onChange={handleCompradorChange}
          />
        </FormSection>
      </div>

      {/* ── Servicio / Material ── */}
      <FormSection title="Servicio" icon="bi-gear">
        <div className="subform__grid-material">
          <SelectField
            label="Origen"
            id="origen"
            options={optsOrigen}
            value={selectedOrigen}
            onChange={handleOrigenChange}
            onAddNew={onAddOrigen}
            addNewFields={[{ key: "nombre", label: "Nombre" }]}
          />
          <SelectField
            label="Patio"
            id="patio"
            options={optsPatio}
            value={selectedPatio}
            onChange={handlePatioChange}
            onAddNew={onAddPatio}
            addNewFields={[{ key: "nombre", label: "Nombre" }]}
          />
          <SelectField
            label="Código"
            id="codigoServicio"
            options={optsServCodigo}
            value={selectedServicio}
            onChange={handleServicioChange}
          />
          <SelectField
            label="Servicio"
            id="nombreServicio"
            options={optsServicio}
            value={selectedServicio}
            onChange={handleServicioChange}
            onAddNew={onAddServicio}
            addNewFields={[
              { key: "nombre", label: "Nombre"  },
              { key: "codigo", label: "Código"  },
              { key: "unidad", label: "Unidad"  },
            ]}
          />

          {/* Unidad (readonly — viene del servicio) */}
          <div className="subform__extra-field">
            <label className="subform__extra-label" htmlFor="unidad">Unidad</label>
            <input
              id="unidad"
              className="subform__extra-input"
              type="text"
              value={unidad}
              readOnly
              placeholder="—"
            />
          </div>

          {/* Cantidad */}
          <div className="subform__extra-field">
            <label className="subform__extra-label" htmlFor="cantidad">Cantidad</label>
            <input
              id="cantidad"
              className="subform__extra-input"
              type="number"
              value={cantidad}
              onChange={(e) => setCantidad(e.target.value)}
              placeholder="0"
              min={0}
            />
          </div>
        </div>
      </FormSection>

      <Notification
        message={notif.message}
        type={notif.type}
        onClose={() => setNotif({ message: "", type: "" })}
      />
    </div>
  );
});

ServiciosForm.displayName = "ServiciosForm";
export default ServiciosForm;