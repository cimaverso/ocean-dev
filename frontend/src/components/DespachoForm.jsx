/**
 * DespachoForm.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Subformulario para registros de tipo DESPACHO.
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

const DespachoForm = forwardRef((
  {
    clientes        = [],
    productos       = [],
    transportadoras = [],
    patios          = [],
    destinos        = [],
    origenes        = [],
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

  const [selectedCliente,        setSelectedCliente]        = useState("");
  const [selectedTransportadora, setSelectedTransportadora] = useState("");
  const [selectedProducto,       setSelectedProducto]       = useState("");
  const [selectedOrigen,         setSelectedOrigen]         = useState("");
  const [selectedDestino,        setSelectedDestino]        = useState("");
  const [selectedPatio,          setSelectedPatio]          = useState("");
  const [orden,                  setOrden]                  = useState("");
  const [precinto,               setPrecinto]               = useState("");
  const [notif,                  setNotif]                  = useState({ message: "", type: "" });

  // ── Autocompletar ────────────────────────────────────────────────────────
  useEffect(() => {
    if (!initialData || Object.keys(initialData).length === 0) return;

    const cli   = clientes.find((c) => c.codigo === initialData?.entidad?.codigo);
    const trans = transportadoras.find((t) => t.nombre === initialData?.transportadora?.nombre);
    const prod  = productos.find((p) => p.codigo === initialData?.producto?.codigo);
    const dest  = destinos.find((d) => d.nombre === initialData?.destino?.nombre);
    const orig  = origenes.find((o) => o.codigo === initialData?.origen?.codigo);
    const pati  = patios.find((p) => p.codigo === initialData?.patio?.codigo);

    if (cli)   setSelectedCliente(cli.id);
    if (trans) setSelectedTransportadora(trans.id);
    if (prod)  setSelectedProducto(prod.id);
    if (dest)  setSelectedDestino(dest.id);
    if (orig)  setSelectedOrigen(orig.id);
    if (pati)  setSelectedPatio(pati.id);
    setOrden(initialData?.transportadora?.orden || "");
    setPrecinto(initialData?.transportadora?.precinto || "");
  }, [initialData, clientes, transportadoras, productos, destinos, origenes, patios]);

  // ── Opciones ─────────────────────────────────────────────────────────────
  const optsCliente    = clientes.map((c) => ({ value: c.id,         label: c.nombre          }));
  const optsCliCodigo  = clientes.map((c) => ({ value: c.id,         label: c.codigo          }));
  const optsTrans      = transportadoras.map((t) => ({ value: t.id,         label: t.nombre         }));
  const optsProducto   = productos.map((p) => ({ value: p.id,         label: p.nombre         }));
  const optsProdCodigo = productos.map((p) => ({ value: p.id,         label: p.codigo         }));
  const optsDestino    = destinos.map((d) => ({ value: d.id,         label: d.nombre         }));
  const optsDestCodigo = destinos.map((d) => ({ value: d.id,         label: d.codigo         }));
  const optsOrigen     = origenes.map((o) => ({ value: o.id,         label: o.nombre         }));
  const optsPatio      = patios.map((p) => ({ value: p.id,         label: p.nombre         }));

  // ── onAddNew ─────────────────────────────────────────────────────────────
  const onAddCliente        = async (d) => { const r = await catalogosAPI.crearCliente(d);        return { value: r.data.id,         label: r.data.nombre         }; };
  const onAddTransportadora = async (d) => { const r = await catalogosAPI.crearTransportadora(d); return { value: r.data.id,   label: r.data.nombre  }; };
  const onAddProducto       = async (d) => { const r = await catalogosAPI.crearProducto(d);       return { value: r.data.id,          label: r.data.nombre        }; };
  const onAddDestino        = async (d) => { const r = await catalogosAPI.crearDestino(d);        return { value: r.data.id,           label: r.data.nombre         }; };
  const onAddOrigen         = async (d) => { const r = await catalogosAPI.crearOrigen(d);         return { value: r.data.id,            label: r.data.nombre          }; };
  const onAddPatio          = async (d) => { const r = await catalogosAPI.crearPatio(d);          return { value: r.data.id,             label: r.data.nombre           }; };

  // ── Handlers ─────────────────────────────────────────────────────────────
  const handleClienteChange        = (opt) => setSelectedCliente(opt?.value        ?? "");
  const handleTransportadoraChange = (opt) => setSelectedTransportadora(opt?.value ?? "");
  const handleProductoChange       = (opt) => setSelectedProducto(opt?.value       ?? "");
  const handleOrigenChange         = (opt) => setSelectedOrigen(opt?.value         ?? "");
  const handleDestinoChange        = (opt) => setSelectedDestino(opt?.value        ?? "");
  const handlePatioChange          = (opt) => setSelectedPatio(opt?.value          ?? "");

  // ── getFormData ──────────────────────────────────────────────────────────
  const getFormData = () => ({
    ent_id:     selectedCliente,
    prod_id:    selectedProducto,
    trasn_id:   selectedTransportadora,
    id_patio:   selectedPatio,
    id_origen:  selectedOrigen,
    id_destino: selectedDestino,
    orden,
    precinto,
    tipo:       initialData.tipo,
  });

  // ── handleProcesar ───────────────────────────────────────────────────────
  const handleProcesar = () => {
    if (selectedProducto && selectedCliente && selectedTransportadora &&
        selectedOrigen && selectedDestino && selectedPatio && pesoBruto) {
      onSubmit?.({ ...getFormData(), estado: "TRANSITO" }, 2);
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
    if (selectedProducto && selectedCliente && selectedTransportadora &&
        selectedOrigen && selectedDestino && selectedPatio) {
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
      {/* ── Cliente / Transportadora ── */}
      <div className="subform__grid-2">
        <FormSection title="Cliente" icon="bi-person-check">
          <SelectField
            label="Nombre"
            id="nombreCliente"
            options={optsCliente}
            value={selectedCliente}
            onChange={handleClienteChange}
            onAddNew={onAddCliente}
            addNewFields={[
              { key: "nombre", label: "Nombre" },
              { key: "codigo", label: "Código" },
            ]}
          />
          <SelectField
            label="Código"
            id="codigoCliente"
            options={optsCliCodigo}
            value={selectedCliente}
            onChange={handleClienteChange}
          />
        </FormSection>

        <FormSection title="Transportadora" icon="bi-truck-front">
          <div className="subform__transp-row">
            <div className="subform__transp-select">
              <SelectField
                label="Nombre"
                id="nombreTransp"
                options={optsTrans}
                value={selectedTransportadora}
                onChange={handleTransportadoraChange}
                onAddNew={onAddTransportadora}
                addNewFields={[{ key: "nombre", label: "Nombre" }]}
              />
            </div>
            <div className="subform__transp-orden">
              <div className="subform__extra-field">
                <label className="subform__extra-label" htmlFor="orden">Orden</label>
                <input
                  id="orden"
                  className="subform__extra-input"
                  type="text"
                  value={orden}
                  onChange={(e) => setOrden(e.target.value)}
                  placeholder="Nro. orden"
                />
              </div>
            </div>
          </div>

          {/* Precintos */}
          <div className="subform__extra-field">
            <label className="subform__extra-label" htmlFor="precinto">Precintos</label>
            <textarea
              id="precinto"
              className="subform__extra-textarea"
              value={precinto}
              onChange={(e) => setPrecinto(e.target.value)}
              placeholder="Números de precinto..."
            />
          </div>
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
            label="Código Prod."
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
          <SelectField
            label="Código Dest."
            id="codigoDestino"
            options={optsDestCodigo}
            value={selectedDestino}
            onChange={handleDestinoChange}
          />
          <SelectField
            label="Destino"
            id="nombreDestino"
            options={optsDestino}
            value={selectedDestino}
            onChange={handleDestinoChange}
            onAddNew={onAddDestino}
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

DespachoForm.displayName = "DespachoForm";
export default DespachoForm;