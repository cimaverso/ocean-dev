import React, { useState, forwardRef, useImperativeHandle, useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import SelectField from "./Layouts/SelectField";
import FormSection from "./FormSection";
import Notification from "./Layouts/Notificacion";
import axios from 'axios';


const IngresoForm = forwardRef(({ productos, proveedores, compradores, patios, origenes, pesoBruto, onSubmit, onFinalizar, onActualizar, handleImprimirTiquete }, ref) => {
  const location = useLocation();
  const initialData = location.state ? location.state.record : {};

  const [selectedProveedor, setSelectedProveedor] = useState("");
  const [selectedComprador, setSelectedComprador] = useState("");
  const [selectedProducto, setSelectedProducto] = useState("");
  const [selectedOrigen, setSelectedOrigen] = useState("");
  const [selectedPatio, setSelectedPatio] = useState("");
  const [formType, setFormType] = useState("");
  const [notification, setNotification] = useState({ message: "", type: "" });

  

  useEffect(() => {
    if (initialData && Object.keys(initialData).length > 0 && proveedores.length > 0 && compradores.length > 0 && productos.length > 0 && patios.length > 0 && origenes.length > 0) {
      const proveedor = proveedores.find(pr => pr.codigo_entidad === initialData?.entidad?.codigoEntidad);
      const comprador = compradores.find(c => c.codigo_comprador === initialData?.comprador?.codigoComprador);
      const producto = productos.find(p => p.codigo_producto === initialData?.producto?.codigoProducto);
      const patio = patios.find(pt => pt.codigo_patio === initialData?.patio?.codigoPatio);
      const origen = origenes.find(o => o.codigo_origen === initialData?.origen?.codigoOrigen);
 
      // Solo autocompletar si no se han seleccionado manualmente
      setSelectedProveedor(proveedor ? proveedor.id_entidad : '');
      setSelectedComprador(comprador ? comprador.id_comprador : '');
      setSelectedProducto(producto ? producto.id_producto : '');
      setSelectedPatio(patio ? patio.id_patio : '');
      setSelectedOrigen(origen ? origen.id_origen : '');
    }
  }, [initialData, proveedores, compradores, productos, patios, origenes]);

  const handleProveedorChange = (selectedOption) => {
    const id = selectedOption.value;
    const proveedor = proveedores.find(proveedor => proveedor.id_entidad === parseInt(id));
    setSelectedProveedor(proveedor ? proveedor.id_entidad : '');
  };

  const handleProductoChange = (selectedOption) => {
    const id = selectedOption.value;
    const producto = productos.find(prod => prod.id_producto === parseInt(id));
    setSelectedProducto(producto ? producto.id_producto : '');
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
    if (selectedProducto && selectedProveedor && selectedComprador && selectedOrigen && selectedPatio && pesoBruto) {
      const data = {

        ent_id: selectedProveedor,
        prod_id: selectedProducto,
        comp_id: selectedComprador,

        id_patio: selectedPatio,
        id_origen: selectedOrigen || null,
        estado: "TRANSITO"
      };
      onSubmit(data);
    }
  };

  const handleFinalizar = async () => {
    const finalizarData = {
      //fecha_entrada: fechaEntrada || initialData.fEntrada,
      ///hora_entrada: horaEntrada || initialData.hEntrada,
      fecha_salida: new Date().toISOString().slice(0, 10),
      hora_salida: new Date().toTimeString().slice(0, 8),
      id_origen: selectedOrigen,
      id_patio: selectedPatio,
      comp_id: selectedComprador,
      ent_id: selectedProveedor,
      prod_id: selectedProducto,
      tipo: initialData.tipo
    };

    try {
      const response = await onFinalizar(finalizarData);

      if (response && response.data && response.data.tiquete_id) {
        const tiqueteId = response.data.tiquete_id;

        setSelectedProveedor(finalizarData.ent_id);
        setSelectedComprador(finalizarData.comp_id);
        setSelectedProducto(finalizarData.prod_id);
        setSelectedPatio(finalizarData.id_patio);
        setSelectedOrigen(finalizarData.id_origen);

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
    const actualizarData = {
      tiquete_id: initialData.id,
      ent_id: selectedProveedor,
      prod_id: selectedProducto,
      trasn_id: selectedComprador,
      id_patio: selectedPatio,
      id_origen: selectedOrigen,
    };

    // Llamar a la función de actualización y luego actualizar el estado local
    onActualizar(actualizarData);

    // Actualizar el estado local con los datos actualizados
    setSelectedProveedor(actualizarData.ent_id);
    setSelectedComprador(actualizarData.comp_id);
    setSelectedProducto(actualizarData.prod_id);
    setSelectedPatio(actualizarData.id_patio);
    setSelectedOrigen(actualizarData.id_origen);
  };

  const getFormData = () => ({
    fecha_entrada: initialData.fEntrada,
    hora_entrada: initialData.hEntrada,
    fecha_salida: new Date().toISOString().slice(0, 10),
    hora_salida: new Date().toTimeString().slice(0, 8),
    id_origen: selectedOrigen,
    id_patio: selectedPatio,
    comp_id: selectedComprador,
    ent_id: selectedProveedor,
    prod_id: selectedProducto,
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
          <FormSection title="Proveedor">
            
            <SelectField
              label="Nombre"
              id="nombreProveedor"
              options={[
                { value: '', label: 'Seleccionar' },
                ...proveedores.map((proveedor) => ({
                  value: proveedor.id_entidad,
                  label: proveedor.nombre_entidad,
                })),
              ]}
              apiEndpoint="http://localhost:5000/proveedores" 
              postApiEndpoint="http://localhost:5000/Producto/add"
              value={selectedProveedor}
              onChange={handleProveedorChange}
            />
            <SelectField
              label="Código"
              id="codigoProveedor"
              options={[
                { value: '', label: 'Seleccionar' },
                ...proveedores.map((proveedor) => ({
                  value: proveedor.id_entidad,
                  label: proveedor.codigo_entidad,
                })),
              ]}
              apiEndpoint="http://localhost:5000/proveedores"
              postApiEndpoint="http://localhost:5000/Producto/add"
              value={selectedProveedor}
              onChange={handleProveedorChange}
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
          <div className="grid grid-cols-2 gap-1">          

            <SelectField
              label="Origen"              
              id="nombreOrigen"
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
              postApiEndpoint="http://localhost:5000/crear_producto"
              value={selectedProducto}
              onChange={handleProductoChange}
            />

          </div>
        </FormSection>
      </section>
    </>


  );
});

export default IngresoForm;
