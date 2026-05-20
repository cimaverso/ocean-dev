import React, { useState, forwardRef, useImperativeHandle, useEffect } from "react";
import { useLocation } from "react-router-dom";
import SelectField from "./Layouts/SelectField";
import FormSection from "./FormSection";
import Notification from "./Layouts/Notificacion";

const DespachoForm = forwardRef(({ clientes, productos, transportadoras, patios, destinos, origenes, pesoBruto, onSubmit, onFinalizar, onActualizar, handleImprimirTiquete }, ref) => {
  const location = useLocation();
  const initialData = location.state ? location.state.record : {};

  const [selectedCliente, setSelectedCliente] = useState('');
  const [selectedTransportadora, setSelectedTransportadora] = useState('');
  const [selectedProducto, setSelectedProducto] = useState('');
  const [selectedOrigen, setSelectedOrigen] = useState('');
  const [selectedDestino, setSelectedDestino] = useState('');
  const [orden, setOrden] = useState('');
  const [precinto, setPrecinto] = useState('');
  const [selectedPatio, setSelectedPatio] = useState('');
  const [observaciones, setObservaciones] = useState('');
  const [notification, setNotification] = useState({ message: "", type: "" });

 
  useEffect(() => {
    if (initialData && Object.keys(initialData).length > 0) {
      autocompletarFormulario(initialData);
    }
  }, [initialData, clientes, transportadoras, productos, destinos, origenes, patios]);

  const autocompletarFormulario = (data) => {
    const cliente = clientes.find(c => c.codigo_entidad === data.entidad.codigoEntidad);
    const transportadora = transportadoras.find(t => t.nombre_transportadora === data.transportadora.nombreTransportadora);
    const producto = productos.find(p => p.codigo_producto === data.producto.codigoProducto);
    const destino = destinos.find(d => d.nombre_destino === data.destino.nombreDestino);
    const origen = origenes.find(o => o.codigo_origen === data.origen.codigoOrigen);
    const patio = patios.find(pt => pt.codigo_patio === data.patio.codigoPatio);

    setSelectedCliente(cliente ? cliente.id_entidad : '');
    setSelectedTransportadora(transportadora ? transportadora.id_transportadora : '');
    setSelectedProducto(producto ? producto.id_producto : '');
    setSelectedDestino(destino ? destino.id_destino : '');
    setSelectedOrigen(origen ? origen.id_origen : '');
    setSelectedPatio(patio ? patio.id_patio : '');
    setOrden(data.transportadora.ordenTransportadora || '');
    setPrecinto(data.transportadora.precintoTransportadora || '');
    setObservaciones(data.observaciones || '');
  };


  const handleClienteChange = (selectedOption) => {
    const id = selectedOption.value;
    const cliente = clientes.find(cliente => cliente.id_entidad === parseInt(id));
    setSelectedCliente(cliente ? cliente.id_entidad : '');
  };

  const handleProductoChange = (selectedOption) => {
    const id = selectedOption.value;
    const producto = productos.find(prod => prod.id_producto === parseInt(id));
    setSelectedProducto(producto ? producto.id_producto : '');
  };

  const handleTransportadoraChange = (selectedOption) => {
    const id = selectedOption.value;
    const transportadora = transportadoras.find(trans => trans.id_transportadora === parseInt(id));
    setSelectedTransportadora(transportadora ? transportadora.id_transportadora : '');
  };

  const handleOrigenChange = (selectedOption) => {
    const id = selectedOption.value;
    const origen = origenes.find(ori => ori.id_origen === parseInt(id));
    setSelectedOrigen(origen ? origen.id_origen : '');
  };
  const handleDestinoChange = (selectedOption) => {
    const id = selectedOption.value;
    const destino = destinos.find(dest => dest.id_destino === parseInt(id));
    setSelectedDestino(destino ? destino.id_destino : '');
  };

  const handlePatioChange = (selectedOption) => {
    const id = selectedOption.value;
    const patio = patios.find(pat => pat.id_patio === parseInt(id));
    setSelectedPatio(patio ? patio.id_patio : '');
  };

  const handleOrdenChange = (e) => {
    setOrden(e.target.value);
  };

  const handlePrecintoChange = (e) => {
    setPrecinto(e.target.value);
  };


  const handleProcesar = () => {
    if (selectedProducto && selectedCliente && selectedTransportadora && selectedOrigen && selectedDestino && selectedPatio && pesoBruto) {
      const data = {
        ent_id: selectedCliente,
        prod_id: selectedProducto,
        trasn_id: selectedTransportadora,
        id_patio: selectedPatio,
        id_origen: selectedOrigen,
        id_destino: selectedDestino,
        orden: orden,
        precinto: precinto,
        estado: "TRANSITO"
      };

      onSubmit(data);
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
      trasn_id: selectedTransportadora,
      ent_id: selectedCliente,
      prod_id: selectedProducto,
      orden: orden,
      precinto: precinto,
      tipo: initialData.tipo
    };

    try {
      const response = await onFinalizar(finalizarData);

      if (response && response.data && response.data.tiquete_id) {
        const tiqueteId = response.data.tiquete_id;

        setSelectedCliente(finalizarData.ent_id);
        setSelectedTransportadora(finalizarData.trasn_id);
        setSelectedProducto(finalizarData.prod_id);
        setSelectedPatio(finalizarData.id_patio);
        setSelectedOrigen(finalizarData.id_origen);
        setSelectedDestino(finalizarData.id_destino);
        setOrden(finalizarData.orden);
        setPrecinto(finalizarData.precinto);

        // Llamar a la función para imprimir el tiquete con el ID recién creado
        handleImprimirTiquete(tiqueteId);
      } else {
        throw new Error("No se recibió el ID del tiquete en la respuesta.");
      }
    } catch (error) {
      setNotification({ message: "Error al finalizar y guardar el tiquete: " + (error.response ? error.response.data.error : error.message), type: "error" });
    }
  };

  const handleActualizar = () => {
    if (selectedProducto && selectedCliente && selectedTransportadora && selectedOrigen && selectedDestino && selectedPatio && pesoBruto) {
      const data = {
        tiquete_id: initialData.id, // Asegúrate de que initialData tiene el ID del tiquete
        ent_id: selectedCliente,
        prod_id: selectedProducto,
        trasn_id: selectedTransportadora,
        id_patio: selectedPatio,
        id_origen: selectedOrigen,
        id_destino: selectedDestino,
        orden: orden,
        precinto: precinto,
      };

      onActualizar(data);

      // Actualizar el estado local después de la actualización
      setSelectedCliente(data.ent_id);
      setSelectedProducto(data.prod_id);
      setSelectedTransportadora(data.trasn_id);
      setSelectedPatio(data.id_patio);
      setSelectedOrigen(data.id_origen);
      setSelectedDestino(data.id_destino);
      setOrden(data.orden);
      setPrecinto(data.precinto);
    } else {
      alert("Por favor, completa todos los campos.");
    }
  };

  

  const getFormData = () => ({
    fecha_entrada: initialData.fEntrada,
    hora_entrada: initialData.hEntrada,
    fecha_salida: new Date().toISOString().slice(0, 10),
    hora_salida: new Date().toTimeString().slice(0, 8),
    id_origen: selectedOrigen,
    id_destino: selectedDestino,
    id_patio: selectedPatio,
    trasn_id: selectedTransportadora,
    ent_id: selectedCliente,
    prod_id: selectedProducto,
    precinto: precinto,
    orden: orden,
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
      <section className="grid grid-cols-8 gap-0">
        <div className="mr-1 col-span-3">
          <FormSection title="Cliente">
            <div>
              
              <SelectField
                label="Nombre"
                id="nombrCliente"
                options={[
                  { value: '', label: 'Seleccionar' },
                  ...clientes.map((cliente) => ({
                    value: cliente.id_entidad,
                    label: cliente.nombre_entidad,
                  })),
                ]}
                apiEndpoint="http://localhost:5000/clientes"
                postApiEndpoint="http://localhost:5000/crear_cliente" 
                value={selectedCliente}
                onChange={handleClienteChange}
              />
              <SelectField
                label="Código"
                id="codigoCliente"
                options={[
                  { value: '', label: 'Seleccionar' },
                  ...clientes.map((cliente) => ({
                    value: cliente.id_entidad,
                    label: cliente.codigo_entidad,
                  })),
                ]}
                apiEndpoint="http://localhost:5000/clientes"
                postApiEndpoint="http://localhost:5000/crear_cliente"
                value={selectedCliente}
                onChange={handleClienteChange}
              />
            </div>
          </FormSection>
        </div>
        <div className="ml-1 col-span-5">
          <FormSection title="Transportadora">
            <div className="flex">
              <SelectField
                label="Nombre"
                id="nombreTransp"
                options={[
                  { value: '', label: 'Seleccionar' },
                  ...transportadoras.map((transportadora) => ({
                    value: transportadora.id_transportadora,
                    label: transportadora.nombre_transportadora,
                  })),
                ]}
                apiEndpoint="http://localhost:5000/transportadoras"
                postApiEndpoint="http://localhost:5000/crear_transportadora"
                value={selectedTransportadora}
                onChange={handleTransportadoraChange}
              />
              <div className="p-1 flex w-11/12">
                <label className="text-xs 2xl:text-base text-center w-1/3 font-bold m-1 block">
                  Orden
                </label>
                <input
                  id="orden"
                  className="border-2 border-[#6D80A6] rounded w-3/4 text-xs 2xl:text-base h-6 px-1 focus:outline-none focus:ring-2 focus:[#6D80A6]"
                  type="text"
                  value={orden}
                  onChange={handleOrdenChange}
                />
              </div>
            </div>
            <div className="ml-1 p-1 flex w-11/12">
              <label className="text-xs 2xl:text-base w-1/5 font-bold m-1 block">
                Precintos
              </label>
              <textarea
                id="precinto"
                className="border-2 text-xs 2xl:text-base  border-[#6D80A6] rounded w-11/12 h-7 px-1 focus:outline-none focus:ring-2 focus:[#6D80A6]"
                type="text"
                value={precinto}
                onChange={handlePrecintoChange}
              />
            </div>
          </FormSection>
        </div>
      </section>

      <section>
        <FormSection title="Material">
          <div className="grid grid-cols-2 gap-0">
            <div>              
               <SelectField
                label="Origen"
                id="origenProducto"
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
                id="codigoProducto"
                options={[
                  { value: '', label: 'Seleccionar' },
                  ...productos.map((producto) => ({
                    value: producto.id_producto,
                    label: producto.codigo_producto,
                  })),
                ]}
                apiEndpoint="http://localhost:5000/productos"
                postApiEndpoint="http://localhost:5000/crear_producto"
                value={selectedProducto}
                onChange={handleProductoChange}
              />
              
              <SelectField
                label="Código"
                id="destinoProducto"
                options={[
                  { value: '', label: 'Seleccionar' },
                  ...destinos.map((destino) => ({
                    value: destino.id_destino,
                    label: destino.codigo_destino,
                  })),
                ]}
                apiEndpoint="http://localhost:5000/destinos"
                postApiEndpoint="http://localhost:5000/crear_destino"
                value={selectedDestino}
                onChange={handleDestinoChange}
              />
              
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
                label="Producto"
                id="nombreProducto"
                options={[
                  { value: '', label: 'Seleccionar' },
                  ...productos.map((producto) => ({
                    value: producto.id_producto,
                    label: producto.nombre_producto,
                  })),
                ]}
                apiEndpoint="http://localhost:5000/productos"
                postApiEndpoint="http://localhost:5000//crear_producto"
                value={selectedProducto}
                onChange={handleProductoChange}
              />

              <SelectField
                label="Destino"
                id="destinoProducto"
                options={[
                  { value: '', label: 'Seleccionar' },
                  ...destinos.map((destino) => ({
                    value: destino.id_destino,
                    label: destino.nombre_destino,
                  })),
                ]}
                apiEndpoint="http://localhost:5000/destinos"
                postApiEndpoint="http://localhost:5000/crear_destino"
                value={selectedDestino}
                onChange={handleDestinoChange}
              />
             
            </div>
          </div>
        </FormSection>
      </section>
    </>
  );


  
});

export default DespachoForm;