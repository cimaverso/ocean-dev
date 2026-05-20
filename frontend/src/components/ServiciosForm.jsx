import React, { useState, useEffect, forwardRef, useImperativeHandle } from "react";
import { useLocation } from "react-router-dom";
import SelectField from "./Layouts/SelectField";
import FormSection from "./FormSection";
import Notification from "./Layouts/Notificacion";

const ServiciosForm = forwardRef(({ servicios, terceros, compradores, patios, origenes, pesoBruto, onSubmit, onFinalizar, onActualizar, isFinalizing, handleImprimirTiquete}, ref) => {
  const location = useLocation();
  const initialData = location.state ? location.state.record : {};

  const [selectedTercero, setSelectedTercero] = useState('');
  const [selectedComprador, setSelectedComprador] = useState('');
  const [selectedServicio, setSelectedServicio] = useState('');
  const [unidad, setUnidad] = useState('');
  const [selectedOrigen, setSelectedOrigen] = useState('');
  const [selectedPatio, setSelectedPatio] = useState('');
  const [cantidad, setCantidad] = useState('');
  const [observaciones, setObservaciones] = useState('');
  const [notification, setNotification] = useState({ message: "", type: "" });

  useEffect(() => {
    if (initialData && Object.keys(initialData).length > 0) {
      autocompletarFormulario(initialData);
    }
  }, [initialData, terceros, compradores, servicios, origenes, patios]);

  const autocompletarFormulario = (data) => {
    const tercero = terceros.find(t => t.codigo_entidad === data?.entidad?.codigoEntidad);
    const comprador = compradores.find(c => c.codigo_comprador === data?.comprador?.codigoComprador);
    const servicio = servicios.find(s => s.codigo_producto === data?.producto?.codigoProducto);
    const origen = origenes.find(o => o.codigo_origen === data?.origen?.codigoOrigen);
    const patio = patios.find(pt => pt.codigo_patio === data?.patio?.codigoPatio);

    setSelectedTercero(tercero ? tercero.id_entidad : '');
    setSelectedComprador(comprador ? comprador.id_comprador : '');
    setSelectedServicio(servicio ? servicio.id_producto : '');
    setSelectedOrigen(origen ? origen.id_origen : '');
    setSelectedPatio(patio ? patio.id_patio : '');
    setUnidad(servicio ? servicio.unidad_medida : '');
    setCantidad(data.cantidad || '');
    setObservaciones(data.observaciones || '');
  };

  useEffect(() => {
    if (selectedServicio) {
      const servicioSeleccionado = servicios.find(serv => serv.id_producto === selectedServicio);
      if (servicioSeleccionado) {
        setUnidad(servicioSeleccionado.unidad_medida || '');
      }
    } else {
      setUnidad(''); // Reinicia el campo de unidad si no hay servicio seleccionado
    }
  }, [selectedServicio, servicios]);

  const handleTerceroChange = (selectedOption) => {
    const id = selectedOption.value;
    const tercero = terceros.find(tercero => tercero.id_entidad === parseInt(id));
    setSelectedTercero(tercero ? tercero.id_entidad : '');
  };

  const handleServicioChange = (selectedOption) => {
    const id = selectedOption.value;
    const servicio = servicios.find(serv => serv.id_producto === parseInt(id));
    setSelectedServicio(servicio ? servicio.id_producto : '');
  };

  const handleCompradorChange = (selectedOption) => {
    const id = selectedOption.value;
    const comprador = compradores.find(comp => comp.id_comprador === parseInt(id));
    setSelectedComprador(comprador ? comprador.id_comprador : '');
  };

  const handleOrigenChange = (selectedOption) => {
    const id = selectedOption.value;
    const origen = origenes.find(ori => ori.id_origen === parseInt(id));
    setSelectedOrigen(origen ? origen.id_origen : '');
  };

  const handlePatioChange = (selectedOption) => {
    const id = selectedOption.value;
    const patio = patios.find(pat => pat.id_patio === parseInt(id));
    setSelectedPatio(patio ? patio.id_patio : '');
  };


  const handleProcesar = () => {
    if (selectedServicio && selectedTercero && selectedComprador && selectedOrigen && selectedPatio && pesoBruto) {
      const data = {
        ent_id: selectedTercero,
        prod_id: selectedServicio,
        comp_id: selectedComprador,
        id_patio: selectedPatio,
        idorigen: selectedOrigen,
        cantidad: cantidad,
        estado: "TRANSITO"
      };

      onSubmit(data);

      // Actualizar el estado local después de procesar
      setSelectedTercero(data.ent_id);
      setSelectedServicio(data.prod_id);
      setSelectedComprador(data.comp_id);
      setSelectedPatio(data.id_patio);
      setSelectedOrigen(data.idorigen);
      setCantidad(data.cantidad);
    } 
  };

  const handleActualizar = () => {
    if (selectedServicio && selectedTercero && selectedComprador && selectedOrigen && selectedPatio && pesoBruto) {
      const data = {
        tiquete_id: initialData.id, // Asegúrate de que initialData tiene el ID del tiquete
        ent_id: selectedTercero,
        prod_id: selectedServicio,
        comp_id: selectedComprador,
        id_patio: selectedPatio,
        idorigen: selectedOrigen,
        cantidad: cantidad,
        observaciones: observaciones,
      };

      onActualizar(data);

      // Actualizar el estado local después de la actualización
      setSelectedTercero(data.ent_id);
      setSelectedServicio(data.prod_id);
      setSelectedComprador(data.comp_id);
      setSelectedPatio(data.id_patio);
      setSelectedOrigen(data.idorigen);
      setCantidad(data.cantidad);
      setObservaciones(data.observaciones);
    } else {
      alert("Por favor, completa todos los campos.");
    }
  };

  const handleFinalizar = async () => {
    const finalizarData = {
      fecha_entrada: initialData.fEntrada,
      hora_entrada: initialData.hEntrada,
      fecha_salida: new Date().toISOString().slice(0, 10),
      hora_salida: new Date().toTimeString().slice(0, 8),
      id_origen: selectedOrigen,
      id_patio: selectedPatio,
      comp_id: selectedComprador,
      ent_id: selectedTercero,
      prod_id: selectedServicio,
      cantidad: cantidad,
      
      tipo: initialData.tipo
    };

    try {
      const response = await onFinalizar(finalizarData);

      if (response && response.data && response.data.tiquete_id) {
        const tiqueteId = response.data.tiquete_id;

        setSelectedTercero(finalizarData.ent_id);
        setSelectedComprador(finalizarData.comp_id);
        setSelectedServicio(finalizarData.prod_id);
        setSelectedPatio(finalizarData.id_patio);
        setSelectedOrigen(finalizarData.id_origen);
        setCantidad(finalizarData.orden);
        

        // Llamar a la función para imprimir el tiquete con el ID recién creado
        handleImprimirTiquete(tiqueteId);
      } else {
        throw new Error("No se recibió el ID del tiquete en la respuesta.");
      }
    } catch (error) {
      setNotification({ message: "Error al finalizar y guardar el tiquete: " + (error.response ? error.response.data.error : error.message), type: "error" });
    }
  };


  const getFormData = () => ({
    fecha_entrada: initialData.fEntrada,
    hora_entrada: initialData.hEntrada,
    fecha_salida: new Date().toISOString().slice(0, 10),
    hora_salida: new Date().toTimeString().slice(0, 8),
    id_origen: selectedOrigen,
    id_patio: selectedPatio,
    comp_id: selectedComprador,
    ent_id: selectedTercero,
    prod_id: selectedServicio,
    cantidad: cantidad,
    tipo: initialData.tipo
  });

  useImperativeHandle(ref, () => ({
    handleProcesar,
    handleFinalizar,
    handleActualizar,
    getFormData
  }));

  return (
    <>
      <section className="grid grid-cols-2">
        <div className="mr-1">
          <FormSection title="Tercero">            
            <SelectField
              label="Nombre"
              id="nombreTercero"
              options={[
                { value: '', label: 'Seleccionar' },
                ...terceros.map((tercero) => ({
                  value: tercero.id_entidad,
                  label: tercero.nombre_entidad,
                })),
              ]}
              apiEndpoint="http://localhost:5000/terceros"
              postApiEndpoint="http://localhost:5000/crear_terceros"
              value={selectedTercero}
              onChange={handleTerceroChange}
            />
            <SelectField
              label="Código"
              id="codigoTercero"
              options={[
                { value: '', label: 'Seleccionar' },
                ...terceros.map((tercero) => ({
                  value: tercero.id_entidad,
                  label: tercero.codigo_entidad,
                })),
              ]}
              apiEndpoint="http://localhost:5000/terceros"
              postApiEndpoint="http://localhost:5000/crear_terceros"
              value={selectedTercero}
              onChange={handleTerceroChange}
            />

          </FormSection>
        </div>
        <div className="ml-1">
          <FormSection title="Comprador">            
            <SelectField
              label="Nombre"
              id="nombreComprador"
              options={[
                { value: '', label: 'Seleccionar' },
                ...compradores.map((comprador) => ({
                  value: comprador.id_comprador,
                  label: comprador.nombre_comprador,
                })),
              ]}
              apiEndpoint="http://localhost:5000/compradores"
              postApiEndpoint="http://localhost:5000/crear_comprador"
              value={selectedComprador}
              onChange={handleCompradorChange}
            />
            <SelectField
              label="Código"
              id="codigoComprador"
              options={[
                { value: '', label: 'Seleccionar' },
                ...compradores.map((comprador) => ({
                  value: comprador.id_comprador,
                  label: comprador.codigo_comprador,
                })),
              ]}
              apiEndpoint="http://localhost:5000/compradores"
              postApiEndpoint="http://localhost:5000/crear_comprador"
              value={selectedComprador}
              onChange={handleCompradorChange}
            />
          </FormSection>
        </div>
      </section>
      <section>
        <FormSection title="Material">
          <div className="grid grid-cols-2">
            <div>
              <SelectField
                label="Origen"
                id="destinoProducto"
                labelClassName="text-red-700 font-bold"
                options={[
                  { value: '', label: 'Seleccionar' },
                  ...origenes.map((origen) => ({
                    value: origen.id_origen,
                    label: origen.nombre_origen,
                  })),
                ]}
                apiEndpoint="http://localhost:5000/origenes"
                postApiEndpoint="http://localhost:5000/crear_origen"
                value={selectedOrigen}
                onChange={handleOrigenChange}
              />

              <SelectField
                label="Código"
                id="codigoServicio"
                options={[
                  { value: '', label: 'Seleccionar' },
                  ...servicios.map((servicio) => ({
                    value: servicio.id_producto,
                    label: servicio.codigo_producto,
                  })),
                ]}
                apiEndpoint="http://localhost:5000/servicios"
                postApiEndpoint="http://localhost:5000/crear_servicio"
                value={selectedServicio}
                onChange={handleServicioChange}
              />
              <div className="m-0 p-1 flex w-full">
                <label className="text-xs 2xl:text-base w-1/4 font-bold m-1 block mr-1">
                  Unidad
                </label>
                <input
                  id="unidad"
                  className="shadow w-11/12 text-xs 2xl:text-base appearance-none border-2 border-[#6D80A6] rounded px-1 text-[#182540] leading-tight focus:outline-none focus:ring-2 focus:[#6D80A6]"
                  type="text"
                  value={unidad}
                  readOnly
                />
              </div>
              
              
            </div>
            <div>
              <SelectField
                label="Patio"
                id="nombrePatio"
                options={[
                  { value: '', label: 'Seleccionar' },
                  ...patios.map((patio) => ({
                    value: patio.id_patio,
                    label: patio.nombre_patio,
                  })),
                ]}
                apiEndpoint="http://localhost:5000/patios"
                postApiEndpoint="http://localhost:5000/crear_patio"
                value={selectedPatio}
                onChange={handlePatioChange}
              />
              <SelectField
                label="Nombre"
                id="nombreServicio"
                options={[
                  { value: '', label: 'Seleccionar' },
                  ...servicios.map((servicio) => ({
                    value: servicio.id_producto,
                    label: servicio.nombre_producto,
                  })),
                ]}
                apiEndpoint="http://localhost:5000/servicios"
                postApiEndpoint="http://localhost:5000/crear_servicio"
                value={selectedServicio}
                onChange={handleServicioChange}
              />
              <div className="m-0 p-1 flex w-full">
                <label className="text-xs 2xl:text-base w-1/4 font-bold m-1 block mr-1">
                  Cantidad
                </label>
                <input
                  id="cantidad"
                  className="shadow w-11/12 text-xs 2xl:text-base appearance-none border-2 border-[#6D80A6] rounded px-1 text-[#182540] leading-tight focus:outline-none focus:ring-2 focus:[#6D80A6]"
                  type="text"
                  value={cantidad}
                  onChange={(e) => setCantidad(e.target.value)}
                />
              </div> 
            </div>
          </div>
        </FormSection>
      </section>
    </>
  );
});

export default ServiciosForm;
