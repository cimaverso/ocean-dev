/**
 * IngresoForm.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Subformulario para registros de tipo INGRESO.
 * Recibe catálogos como props desde TiqueteForm (que es dueño del fetch).
 * No hace ninguna llamada HTTP directa.
 *
 * Props:
 *   productos    {Array}    — Lista de productos
 *   proveedores  {Array}    — Lista de proveedores
 *   compradores  {Array}    — Lista de compradores
 *   patios       {Array}    — Lista de patios
 *   origenes     {Array}    — Lista de orígenes
 *   pesoBruto    {number}   — Peso bruto actual
 *   onSubmit     {Function} — (data, tipoId) => void — procesar registro
 *   onFinalizar  {Function} — (data) => Promise       — finalizar tiquete
 *   onActualizar {Function} — (data) => void          — actualizar tiquete
 *   handleImprimirTiquete {Function} — (tiqueteId) => void
 */

import React, {
  useState,
  forwardRef,
  useImperativeHandle,
  useEffect,
} from "react";
import { useLocation } from "react-router-dom";
import SelectField from "./Layouts/SelectField";
import FormSection from "./FormSection";
import Notification from "./Layouts/Notificacion";
import { catalogosAPI } from "../api/api";
import "./SubForm.css";

const IngresoForm = forwardRef((
  {
    productos   = [],
    proveedores = [],
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

  const [selectedProveedor, setSelectedProveedor] = useState("");
  const [selectedComprador, setSelectedComprador] = useState("");
  const [selectedProducto,  setSelectedProducto]  = useState("");
  const [selectedOrigen,    setSelectedOrigen]    = useState("");
  const [selectedPatio,     setSelectedPatio]     = useState("");
  const [notif,             setNotif]             = useState({ message: "", type: "" });

  // ── Autocompletar desde initialData ────────────────────────────────────
  useEffect(() => {
    if (!initialData || Object.keys(initialData).length === 0) return;
    if (!proveedores.length || !compradores.length || !productos.length) return;

    const prov = proveedores.find((p) => p.codigo === initialData?.entidad?.codigo);
    const comp = compradores.find((c) => c.codigo === initialData?.comprador?.codigo);
    const prod = productos.find((p) => p.codigo === initialData?.producto?.codigo);
    const pati = patios.find((p) => p.codigo === initialData?.patio?.codigo);
    const orig = origenes.find((o) => o.codigo === initialData?.origen?.codigo);

    if (prov) setSelectedProveedor(prov.id);
    if (comp) setSelectedComprador(comp.id);
    if (prod) setSelectedProducto(prod.id);
    if (pati) setSelectedPatio(pati.id);
    if (orig) setSelectedOrigen(orig.id);
  }, [initialData, proveedores, compradores, productos, patios, origenes]);

  // ── Builders de opciones ────────────────────────────────────────────────
  const optsProveedor = proveedores.map((p) => ({ value: p.id,   label: p.nombre  }));
  const optsProvCodigo= proveedores.map((p) => ({ value: p.id,   label: p.codigo  }));
  const optsComprador = compradores.map((c) => ({ value: c.id, label: c.nombre}));
  const optsCompCodigo= compradores.map((c) => ({ value: c.id, label: c.codigo}));
  const optsProducto  = productos.map((p)   => ({ value: p.id,  label: p.nombre }));
  const optsProdCodigo= productos.map((p)   => ({ value: p.id,  label: p.codigo }));
  const optsPatio     = patios.map((p)       => ({ value: p.id,    label: p.nombre    }));
  const optsOrigen    = origenes.map((o)     => ({ value: o.id,   label: o.nombre   }));

  // ── onAddNew callbacks ──────────────────────────────────────────────────
  const onAddProveedor = async (formData) => {
    const res = await catalogosAPI.crearProveedor(formData);
    return { value: res.data.id, label: res.data.nombre };
  };
  const onAddComprador = async (formData) => {
    const res = await catalogosAPI.crearComprador(formData);
    return { value: res.data.id, label: res.data.nombre };
  };
  const onAddProducto = async (formData) => {
    const res = await catalogosAPI.crearProducto(formData);
    return { value: res.data.id, label: res.data.nombre };
  };
  const onAddOrigen = async (formData) => {
    const res = await catalogosAPI.crearOrigen(formData);
    return { value: res.data.id, label: res.data.nombre };
  };
  const onAddPatio = async (formData) => {
    const res = await catalogosAPI.crearPatio(formData);
    return { value: res.data.id, label: res.data.nombre };
  };

  // ── Handlers de selección ────────────────────────────────────────────────
  const handleProveedorChange = (opt) => setSelectedProveedor(opt?.value ?? "");
  const handleCompradorChange = (opt) => setSelectedComprador(opt?.value ?? "");
  const handleProductoChange  = (opt) => setSelectedProducto(opt?.value  ?? "");
  const handleOrigenChange    = (opt) => setSelectedOrigen(opt?.value    ?? "");
  const handlePatioChange     = (opt) => setSelectedPatio(opt?.value     ?? "");

  // ── getFormData ──────────────────────────────────────────────────────────
  const getFormData = () => ({
    ent_id:    selectedProveedor,
    prod_id:   selectedProducto,
    comp_id:   selectedComprador,
    id_patio:  selectedPatio,
    id_origen: selectedOrigen || null,
    tipo:      initialData.tipo,
  });

  // ── handleProcesar ───────────────────────────────────────────────────────
  const handleProcesar = () => {
    if (selectedProducto && selectedProveedor && selectedComprador &&
        selectedOrigen && selectedPatio && pesoBruto) {
      onSubmit?.({ ...getFormData(), estado: "TRANSITO" }, 1);
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
    onActualizar?.({ tiquete_id: initialData.id, ...getFormData() });
  };

  // ── Exponer métodos al padre via ref ─────────────────────────────────────
  useImperativeHandle(ref, () => ({
    handleProcesar,
    handleFinalizar,
    handleActualizar,
    getFormData,
  }));

  return (
    <div className="subform">
      {/* ── Proveedor / Comprador ── */}
      <div className="subform__grid-2">
        <FormSection title="Proveedor" icon="bi-building">
          <SelectField
            label="Nombre"
            id="nombreProveedor"
            options={optsProveedor}
            value={selectedProveedor}
            onChange={handleProveedorChange}
            onAddNew={onAddProveedor}
            addNewFields={[
              { key: "nombre",  label: "Nombre"  },
              { key: "codigo",  label: "Código"  },
            ]}
          />
          <SelectField
            label="Código"
            id="codigoProveedor"
            options={optsProvCodigo}
            value={selectedProveedor}
            onChange={handleProveedorChange}
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
              { key: "nombre",  label: "Nombre"  },
              { key: "codigo",  label: "Código"  },
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

      {/* ── Material ── */}
      <FormSection title="Material" icon="bi-box-seam">
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
            id="codigoProducto"
            options={optsProdCodigo}
            value={selectedProducto}
            onChange={handleProductoChange}
          />
          <SelectField
            label="Producto"
            id="nombreProducto"
            options={optsProducto}
            value={selectedProducto}
            onChange={handleProductoChange}
            onAddNew={onAddProducto}
            addNewFields={[
              { key: "nombre", label: "Nombre" },
              { key: "codigo", label: "Código" },
            ]}
          />
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

IngresoForm.displayName = "IngresoForm";
export default IngresoForm;