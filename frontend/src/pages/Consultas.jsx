import { useState, useEffect, useRef, useMemo } from "react";
import moment from 'moment';
import api, { catalogosAPI, vehiculosAPI, facturasAPI } from "../api/api";
import Sidebar from "../components/Layouts/Sidebar";
import Header from "../components/Layouts/Header";
import Table from "../components/Layouts/Tabla";
import { MagnifyingGlassIcon } from "@heroicons/react/24/solid";
import InputField from "../components/Layouts/InputField";
import SelectField from "../components/Layouts/SelectField";
import Notification from "../components/Layouts/Notificacion";
import iconTxt from "../assets/txt.svg";
import iconPdf from "../assets/pdf.svg";
import iconExcel from "../assets/excel.svg";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Consultas() {
  const [formType, setFormType] = useState("Ingreso");
  const [ingresos, setIngresos] = useState([]);
  const [despachos, setDespachos] = useState([]);
  const [servicios, setServicios] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [proveedores, setProveedores] = useState([]);
  const [terceros, setTerceros] = useState([]);
  const [productos, setProductos] = useState([]);
  const [productosEntrada, setProductosEntrada] = useState([]);
  const [productosSalida, setProductosSalida] = useState([]);
  const [productosEntradaSalida, setProductosEntradaSalida] = useState([]);
  const [varios, setVarios] = useState([]);
  const [vehiculos, setVehiculos] = useState([]);
  const [trailers, setTrailers] = useState([]);
  const [conductores, setConductores] = useState([]);
  const [origenes, setOrigenes] = useState([]);
  const [destinos, setDestinos] = useState([]);
  const [patios, setPatios] = useState([]);
  const [compradores, setCompradores] = useState([]);
  const [transportadoras, setTransportadoras] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [notification, setNotification] = useState({ message: "", type: "" });
  const [procesosProducto, setProcesosProducto] = useState([]);
  const [unidadesMedida, setUnidadesMedida] = useState([]);
  const cancelTokenSource = useRef(null);
  const navigate = useNavigate();
  const userRole = localStorage.getItem("userRole");
  const [facturas, setFacturas] = useState([])

  useEffect(() => {
    const currentDate = moment().format('YYYY-MM-DD');

    if (["Ingreso", "Despacho", "Servicios"].includes(formType)) {
      setStartDate(currentDate);
      setEndDate(currentDate);
    } else {
      setStartDate('');
      setEndDate('');
    }

    fetchData();
  }, [formType]);

  const fetchCommonData = async () => {
    try {
      const [clientesResponse, proveedoresResponse, tercerosResponse, productosEntradaResponse, productosSalidaResponse, productosEntradaSalidaResponse, variosResponse, destinosResponse, origenesResponse, patiosResponse, compradoresResponse, transportadorasResponse, conductoresResponse, vehiculosResponse, trailersResponse, facturaResponse] = await Promise.all([
        catalogosAPI.getClientes(),
        catalogosAPI.getProveedores(),
        catalogosAPI.getTerceros(),
        catalogosAPI.getProductosEntrada(),
        catalogosAPI.getProductosSalida(),
        catalogosAPI.getProductosEntradaSalida(),
        catalogosAPI.getServicios(),
        catalogosAPI.getDestinos(),
        catalogosAPI.getOrigenes(),
        catalogosAPI.getPatios(),
        catalogosAPI.getCompradores(),
        catalogosAPI.getTransportadoras(),
        vehiculosAPI.getConductores(),
        vehiculosAPI.getVehiculos(),
        vehiculosAPI.getTrailers(),
        facturasAPI.getFacturas()
      ]);

      setClientes(clientesResponse.data);
      setProveedores(proveedoresResponse.data);
      setTerceros(tercerosResponse.data);
      setProductosEntrada(productosEntradaResponse.data);
      setProductosSalida(productosSalidaResponse.data);
      setProductosEntradaSalida(productosEntradaSalidaResponse.data);
      setVarios(variosResponse.data);
      setDestinos(destinosResponse.data);
      setOrigenes(origenesResponse.data);
      setPatios(patiosResponse.data);
      setCompradores(compradoresResponse.data);
      setTransportadoras(transportadorasResponse.data);
      setConductores(conductoresResponse.data);
      setVehiculos(vehiculosResponse.data);
      setTrailers(trailersResponse.data);
      setFacturas(facturaResponse.data);

    } catch (error) {
      console.error('Error fetching common data:', error);
      setErrorMessage('Error fetching common data: ' + error.message);
    }
  };

  const tipoMap = {
    Ingreso: 1,
    Despacho: 2,
    Servicios: 3,
  };

  const fetchData = async () => {
    setLoading(true);
    if (cancelTokenSource.current) {
      cancelTokenSource.current.cancel('Operation canceled due to new request.');
    }
    cancelTokenSource.current = api.CancelToken.source();

    try {
      let response;
      const includeInactive = true;

      if (["Ingreso", "Despacho", "Servicios"].includes(formType)) {
        const tipo = tipoMap[formType];
        response = await api.get(`/registro/finalizado/${tipo}`, {
          params: {
            fecha_inicio: startDate,
            fecha_fin: endDate,
          },
          cancelToken: cancelTokenSource.current.token,
        });

        if (formType === "Ingreso") setIngresos(response.data);
        if (formType === "Despacho") setDespachos(response.data);
        if (formType === "Servicios") setServicios(response.data);
        fetchCommonData();
        return;
      }

      switch (formType) {
        case "Cliente":
          response = await api.get("/entidad/1", {
            params: { incluir_inactivos: includeInactive },
            cancelToken: cancelTokenSource.current.token,
          });
          setClientes(response.data);
          break;
        case "Proveedor":
          response = await api.get("/entidad/2", {
            params: { incluir_inactivos: includeInactive },
            cancelToken: cancelTokenSource.current.token,
          });
          setProveedores(response.data);
          break;
        case "Tercero":
          response = await api.get("/entidad/3", {
            params: { incluir_inactivos: includeInactive },
            cancelToken: cancelTokenSource.current.token,
          });
          setTerceros(response.data);
          break;
        case "Producto":
          try {
            response = await api.get("/producto/1", {
              params: { incluir_inactivos: includeInactive },
              cancelToken: cancelTokenSource.current.token,
            });
            const allProductos = response.data;
            fetchProcesosProducto();
            fetchUnidadesMedida();
            setProductos(allProductos);
          } catch (error) {
            console.error('Error fetching products data:', error);
          }
          break;
        case "Varios":
          response = await api.get("/producto/2", {
            params: { incluir_inactivos: includeInactive },
            cancelToken: cancelTokenSource.current.token,
          });
          setVarios(response.data);
          fetchUnidadesMedida();
          break;
        case "Vehiculo":
          response = await api.get("/vehiculo/", {
            cancelToken: cancelTokenSource.current.token,
          });
          setVehiculos(response.data);
          fetchConductores();
          break;
        case "Conductor":
          response = await api.get("/conductor/", {
            cancelToken: cancelTokenSource.current.token,
          });
          setConductores(response.data);
          break;
        case "Origen":
          response = await api.get("/origen/", {
            cancelToken: cancelTokenSource.current.token,
          });
          setOrigenes(response.data);
          break;
        case "Destino":
          response = await api.get("/destino/", {
            cancelToken: cancelTokenSource.current.token,
          });
          setDestinos(response.data);
          break;
        case "Patio":
          response = await api.get("/patio/", {
            cancelToken: cancelTokenSource.current.token,
          });
          setPatios(response.data);
          break;
        case "Comprador":
          response = await api.get("/comprador/", {
            cancelToken: cancelTokenSource.current.token,
          });
          setCompradores(response.data);
          break;
        case "Trailer":
          response = await api.get("/trailer/", {
            cancelToken: cancelTokenSource.current.token,
          });
          setTrailers(response.data);
          break;
        case "Transportadora":
          response = await api.get("/transportadora/", {
            cancelToken: cancelTokenSource.current.token,
          });
          setTransportadoras(response.data);
          break;
        case "Factura":
          response = await api.get("/factura/", {
            cancelToken: cancelTokenSource.current.token,
          });
          setFacturas(response.data);
          break;
        default:
          break;
      }
    } catch (error) {
      if (api.isCancel(error)) {
        console.log('Request canceled', error.message);
      } else {
        setErrorMessage("Error fetching data: " + error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchProcesosProducto = async () => {
    try {
      const response = await api.get('/proceso/', { cancelToken: cancelTokenSource.current.token });
      setProcesosProducto(response.data);
    } catch (error) {
      console.error('Error fetching procesos producto:', error);
    }
  };

  const fetchUnidadesMedida = async () => {
    try {
      const response = await api.get('/medida/', { cancelToken: cancelTokenSource.current.token });
      setUnidadesMedida(response.data);
    } catch (error) {
      console.error('Error fetching unidades de medida:', error);
    }
  };

  const fetchConductores = async () => {
    try {
      const response = await api.get('/conductor/', { cancelToken: cancelTokenSource.current.token });
      setConductores(response.data);
    } catch (error) {
      console.error('Error fetching conductores:', error);
    }
  };

  useEffect(() => {
    fetchData();
  }, [formType]);

  const handleExport = () => {
    const exportPaths = {
      Ingreso: '/registro/exportar/ingresos',
      Despacho: '/registro/exportar/despachos',
      Servicios: '/registro/exportar/servicios',
      Cliente: '/entidad/exportar/1',
      Proveedor: '/entidad/exportar/2',
      Tercero: '/entidad/exportar/3',
      Producto: '/producto/exportar/1',
      Varios: '/producto/exportar/2',
      Vehiculo: '/vehiculo/exportar',
      Trailer: '/trailer/exportar',
      Conductor: '/conductor/exportar',
      Origen: '/origen/exportar',
      Destino: '/destino/exportar',
      Patio: '/patio/exportar',
      Comprador: '/comprador/exportar',
      Transportadora: '/transportadora/exportar',
      Factura: '/factura/exportar'
    };

    const exportPath = exportPaths[formType];
    if (!exportPath) return;

    const params = new URLSearchParams({ consulta: searchQuery });
    if (["Ingreso", "Despacho", "Servicios"].includes(formType)) {
      params.set('fecha_inicio', startDate);
      params.set('fecha_fin', endDate);
    }

    window.location.href = `${api.defaults.baseURL}${exportPath}?${params.toString()}`;
  };

  const handleDoubleClick = (record) => {
    if (["Ingreso", "Despacho", "Servicios"].includes(formType)) {
      let formTypeToNavigate;
      if (record.tipo) {
        switch (record.tipo.toUpperCase()) {
          case "INGRESO":
            formTypeToNavigate = "INGRESO";
            break;
          case "DESPACHO":
            formTypeToNavigate = "DESPACHO";
            break;
          case "SERVICIOS":
            formTypeToNavigate = "SERVICIOS";
            break;
          default:
            formTypeToNavigate = null;
            break;
        }
        if (formTypeToNavigate) {
          navigate("/formulario", {
            state: {
              record,
              formType: formTypeToNavigate,
              isTiquete: true
            }
          });
        }
      } else {
        console.warn("El tipo de registro es undefined:", record);
      }
    }
  };

  const columnConfig = {
    Ingreso: [
      { name: "tiquete", title: "Tiquete" },
      { name: "registro", title: "Registro" },
      { name: "tipo", title: "Tipo" },
      { name: "numero_factura", title: "Facturado" },
      { name: "nombreOrigen", title: "Origen" },
      { name: "fEntrada", title: "Fecha Entrada" },
      { name: "hEntrada", title: "Hora Entrada" },
      { name: "fSalida", title: "Fecha Salida" },
      { name: "hSalida", title: "Hora Salida" },
      { name: "placa", title: "Placa" },
      { name: "trailer", title: "Trailer" },
      { name: "conductor", title: "Conductor" },
      { name: "cedulaConductor", title: "Cedula Conductor" },
      { name: "codigoEntidad", title: "Código Proveedor" },
      { name: "nombreEntidad", title: "Proveedor" },
      { name: "codigoComprador", title: "Código Comprador" },
      { name: "nombreComprador", title: "Comprador" },
      { name: "codigoProducto", title: "Código Producto" },
      { name: "nombreProducto", title: "Producto" },
      { name: "pesoBruto", title: "Peso Entrada" },
      { name: "pesoTara", title: "Peso Salida" },
      { name: "pesoNeto", title: "Peso Neto" },      
      { name: "nombrePatio", title: "Patio" },
      { name: "observaciones", title: "Observaciones" },
    ],
    Despacho: [
      { name: "tiquete", title: "Tiquete" },
      { name: "registro", title: "Registro" },
      { name: "tipo", title: "Tipo" },
      { name: "fEntrada", title: "Fecha Entrada" },
      { name: "hEntrada", title: "Hora Entrada" },
      { name: "fSalida", title: "Fecha Salida" },
      { name: "hSalida", title: "Hora Salida" },
      { name: "placa", title: "Placa" },
      { name: "trailer", title: "Trailer" },
      { name: "conductor", title: "Conductor" },
      { name: "cedulaConductor", title: "Cedula Conductor" },
      { name: "codigoEntidad", title: "Código Cliente" },
      { name: "nombreEntidad", title: "Cliente" },
      { name: "codigoDestino", title: "Código Destino" },
      { name: "nombreDestino", title: "Destino" },
      { name: "codigoProducto", title: "Código Producto" },
      { name: "nombreProducto", title: "Producto" },
      { name: "pesoTara", title: "Peso Entrada" },
      { name: "pesoBruto", title: "Peso Salida" },
      { name: "pesoNeto", title: "Peso Neto" },
      { name: "nombreOrigen", title: "Origen" },
      { name: "nombrePatio", title: "Patio" },
      { name: "nombreTransportadora", title: "Transportadora" },
      { name: "ordenTransportadora", title: "Orden" },
      { name: "precintoTransportadora", title: "Precintos" },
      { name: "observaciones", title: "Observaciones" }
    ],
    Servicios: [
      { name: "tiquete", title: "Tiquete" },
      { name: "registro", title: "Registro" },
      { name: "tipo", title: "Tipo" },
      { name: "fEntrada", title: "Fecha Entrada" },
      { name: "hEntrada", title: "Hora Entrada" },
      { name: "fSalida", title: "Fecha Salida" },
      { name: "hSalida", title: "Hora Salida" },
      { name: "placa", title: "Placa" },
      { name: "trailer", title: "Trailer" },
      { name: "conductor", title: "Conductor" },
      { name: "cedulaConductor", title: "Cedula Conductor" },
      { name: "codigoEntidad", title: "Código Tercero" },
      { name: "nombreEntidad", title: "Tercero" },
      { name: "codigoComprador", title: "Código Comprador" },
      { name: "nombreComprador", title: "Comprador" },
      { name: "codigoProducto", title: "Código Servicio" },
      { name: "nombreProducto", title: "Servicio" },
      { name: "pesoBruto", title: "Peso Entrada" },
      { name: "pesoTara", title: "Peso Salida" },
      { name: "pesoNeto", title: "Peso Neto" },
      { name: "nombreOrigen", title: "Origen" },
      { name: "nombrePatio", title: "Patio" },
      { name: "unidad", title: "Unidad" },
      { name: "cantidad", title: "Cantidad" },
      { name: "observaciones", title: "Observaciones" }
    ],
    Cliente: [
      { name: "id_entidad", title: "ID", hidden: true },
      { name: "codigo_entidad", title: "Código" },
      { name: "nombre_entidad", title: "Cliente" },
      { name: "nit_entidad", title: "NIT" },
      { name: "telefono_entidad", title: "Teléfono" },
      { name: "direccion_entidad", title: "Dirección" },
      { name: "estado_entidad", title: "Estado", hidden: true },
    ],
    Proveedor: [
      { name: "id_entidad", title: "ID", hidden: true },
      { name: "codigo_entidad", title: "Código" },
      { name: "nombre_entidad", title: "Proveedor" },
      { name: "nit_entidad", title: "NIT" },
      { name: "telefono_entidad", title: "Teléfono" },
      { name: "direccion_entidad", title: "Dirección" },
      { name: "estado_entidad", title: "Estado", hidden: true },
    ],
    Tercero: [
      { name: "id_entidad", title: "ID", hidden: true },
      { name: "codigo_entidad", title: "Código" },
      { name: "nombre_entidad", title: "Tercero" },
      { name: "nit_entidad", title: "NIT" },
      { name: "telefono_entidad", title: "Teléfono" },
      { name: "direccion_entidad", title: "Dirección" },
      { name: "estado_entidad", title: "Estado", hidden: true },
    ],
    Producto: [
      { name: "id_producto", title: "ID", hidden: true },
      { name: "codigo_producto", title: "Código" },
      { name: "nombre_producto", title: "Producto" },
      { name: "unidad_medida", title: "Unidad de Medida" },
      { name: "proceso_producto", title: "Proceso Producto" },
      { name: "estado_producto", title: "Estado", hidden: true },
    ],
    Varios: [
      { name: "id_producto", title: "ID", hidden: true },
      { name: "codigo_producto", title: "Código" },
      { name: "nombre_producto", title: "Servicio" },
      { name: "unidad_medida", title: "Unidad Medida" },
      { name: "estado_producto", title: "Estado", hidden: true },
    ],
    Vehiculo: [
      { name: "id_vehiculo", title: "ID", hidden: true },
      { name: "placa", title: "Placa" },
      { name: "estado_vehiculo", title: "Estado", hidden: true },
    ],
    Trailer: [
      { name: "id_trailer", title: "ID", hidden: true },
      { name: "trailer", title: "Trailer" },
    ],
    Conductor: [
      { name: "id_conductor", title: "ID", hidden: true },
      { name: "nombre_conductor", title: "Conductor" },
      { name: "cedula_conductor", title: "Cedula" },
      { name: "estado_conductor", title: "Estado", hidden: true },
    ],
    Origen: [
      { name: "id_origen", title: "ID", hidden: true },
      { name: "codigo_origen", title: "Codigo" },
      { name: "nombre_origen", title: "Origen" }
    ],
    Destino: [
      { name: "id_destino", title: "ID", hidden: true },
      { name: "codigo_destino", title: "Codigo" },
      { name: "nombre_destino", title: "Destino" }
    ],
    Patio: [
      { name: "id_patio", title: "ID", hidden: true },
      { name: "codigo_patio", title: "Codigo" },
      { name: "nombre_patio", title: "Patio" }
    ],
    Comprador: [
      { name: "id_comprador", title: "ID", hidden: true },
      { name: "codigo_comprador", title: "Codigo" },
      { name: "nombre_comprador", title: "Comprador" }
    ],
    Transportadora: [
      { name: "id_transportadora", title: "ID", hidden: true },
      { name: "codigo_transportadora", title: "codigo" },
      { name: "nombre_transportadora", title: "Transportadora" },
      { name: "ciudad_transportadora", title: "Ciudad" },
      { name: "nit_transportadora", title: "NIT" },
      { name: "telefono_transportadora", title: "Telefono" }
    ],
    Factura:[
      { name: "id_factura", title: "ID", hidden: true },
      { name: "numero_factura", title: "Factura" },
    ]
  };

  const formTypes = [
    { value: "", label: "Seleccione" },
    { value: "Ingreso", label: "Ingresos" },
    { value: "Despacho", label: "Despachos" },
    { value: "Servicios", label: "Servicios" },
    { value: "Cliente", label: "Cliente" },
    { value: "Proveedor", label: "Proveedor" },
    { value: "Producto", label: "Producto" },
    { value: "Varios", label: "Varios" },
    { value: "Tercero", label: "Tercero" },
    { value: "Vehiculo", label: "Vehiculo" },
    { value: "Trailer", label: "Trailer" },
    { value: "Conductor", label: "Conductor" },
    { value: "Origen", label: "Origen" },
    { value: "Destino", label: "Destino" },
    { value: "Patio", label: "Patio" },
    { value: "Comprador", label: "Comprador" },
    { value: "Transportadora", label: "Transportadora" },
    { value: "Factura", label: "Factura" }
  ];

  const columns = columnConfig[formType] || [];
  const visibleColumns = columns.filter(column => !column.hidden);

  const filteredData = (formType === "Cliente" ? clientes :
    formType === "Proveedor" ? proveedores :
      formType === "Tercero" ? terceros :
        formType === "Producto" ? productos :
          formType === "Vehiculo" ? vehiculos.map(vehiculo => ({
            ...vehiculo,
            nombre_conductor: conductores.find(conductor => conductor.id_conductor === vehiculo.vehi_idconductor)?.nombre_conductor || ''
          })) :
            formType === "Conductor" ? conductores :
              formType === "Ingreso" ? ingresos :
                formType === "Despacho" ? despachos :
                  formType === "Servicios" ? servicios :
                    formType === "Trailer" ? trailers :
                      formType === "Origen" ? origenes :
                        formType === "Destino" ? destinos :
                          formType === "Patio" ? patios :
                            formType === "Comprador" ? compradores :
                              formType === "Transportadora" ? transportadoras :
                                formType === "Varios" ? varios :
                                  formType === "Factura" ? facturas : [])
    .filter(item => {
      if (formType === "Ingreso" || formType === "Despacho" || formType === "Servicios") {
        return item.tipo.toUpperCase() === formType.toUpperCase();
      }
      return true;
    })
    .filter(item => {
      if (searchQuery === "") return true;
      return Object.values(item).some(val => val && val.toString().toLowerCase().includes(searchQuery.toLowerCase()));
    })
    .filter(item => {
      const fSalida = item.fSalida ? moment(item.fSalida, "YYYY-MM-DD") : null;
      const startDateValid = startDate === "" || (fSalida && fSalida.isSameOrAfter(moment(startDate, "YYYY-MM-DD")));
      const endDateValid = endDate === "" || (fSalida && fSalida.isSameOrBefore(moment(endDate, "YYYY-MM-DD")));
      return startDateValid && endDateValid;
    });

  // Usamos useMemo para calcular el total de "peso neto" a partir de los datos filtrados.
  // Se suma la propiedad "pesoNeto" de cada registro, convirtiéndola a número.
  const totalPesoNeto = useMemo(() => {
    return filteredData.reduce((total, item) => {
      const peso = parseFloat(item.pesoNeto);
      return total + (isNaN(peso) ? 0 : peso);
    }, 0);
  }, [filteredData]);

  const tablesWithAddButton = ["Cliente", "Proveedor", "Producto", "Varios", "Tercero", "Vehiculo", "Conductor", "Origen", "Destino", "Patio", "Comprador", "Transportadora", "Trailer", "Factura"];

  const handleFormTypeChange = (selectedOption) => {
    if (cancelTokenSource.current) {
      cancelTokenSource.current.cancel('Operation canceled due to new request.');
    }
    setFormType(selectedOption ? selectedOption.value : "");
    console.log("Form Type selected:", selectedOption ? selectedOption.value : "");
    setSearchQuery(''); // Reset search query on form type change
    setStartDate(''); // Reset start date
    setEndDate(''); // Reset end date
    setClientes([]);
    setProveedores([]);
    setTerceros([]);
    setProductos([]);
    setVarios([]);
    setVehiculos([]);
    setConductores([]);
    setOrigenes([]);
    setTrailers([]);
    setPatios([]);
    setCompradores([]);
    setTransportadoras([]);
    setFacturas([]);
  };

  return (
    <div className="h-screen font-montserrat bg-[#F2F2F2]">
      <Notification message={errorMessage} type="error" />
      <div className="flex h-full">
        <Sidebar />
        <div className="flex flex-col flex-1 w-screen h-dvh overflow-hidden">
          <Header />
          <div className="m-2 p-1 h-screen overflow-auto">
            <div className="m-1 p-1 text-sm xl:text-base">
              <div className="bg-white p-1 rounded-lg space-y-1">
                <div className="flex items-center space-x-1">
                  <SelectField
                    label="Tablas"
                    id="formType"
                    options={formTypes}
                    value={formType}
                    onChange={handleFormTypeChange}
                    className="mr-2"
                  />
                  <div className="flex-grow w-3/5">
                    <div className="relative">
                      <input
                        className="w-full h-6 p-2 rounded-lg border border-gray-300"
                        placeholder="Buscar..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                      <MagnifyingGlassIcon className="w-5 h-5 absolute right-4 top-1/2 transform -translate-y-1/2" />
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  <InputField
                    label="Desde"
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    readOnly={!["Ingreso", "Despacho", "Servicios"].includes(formType)}
                  />
                  <InputField
                    label="Hasta"
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    readOnly={!["Ingreso", "Despacho", "Servicios"].includes(formType)}
                  />
                </div>
              </div>
            </div>
            <div className="m-3 h-[73%] overflow-scroll text-[9px]">
              <Table
                columns={visibleColumns}
                data={filteredData}
                editable={true}
                formType={formType}
                isConsultasPage={true}
                showAddButton={tablesWithAddButton.includes(formType)}
                setClientes={setClientes}
                setProveedores={setProveedores}
                setTerceros={setTerceros}
                setProductos={setProductos}
                setVarios={setVarios}
                setConductores={setConductores}
                setVehiculos={setVehiculos}
                setDestinos={setDestinos}
                setOrigenes={setOrigenes}
                setCompradores={setCompradores}
                setPatios={setPatios}
                setTransportadoras={setTransportadoras}
                setTrailers={setTrailers}
                setFacturas={setFacturas}
                clientes={clientes}
                proveedores={proveedores}
                terceros={terceros}
                productos={productos}
                productosEntrada={productosEntrada}
                productosSalida={productosSalida}
                productosEntradaSalida={productosEntradaSalida}
                origenes={origenes}
                destinos={destinos}
                patios={patios}
                varios={varios}
                transportadoras={transportadoras}
                vehiculos={vehiculos}
                trailers={trailers}
                facturas={facturas}
                compradores={compradores}
                conductores={conductores}
                unidadesMedida={unidadesMedida}
                procesosProducto={procesosProducto}
                onDoubleClickRow={handleDoubleClick}   
              />
            </div>
            <div className="flex justify-between mt-4">
              <div>
                {/* Se muestran el total de registros y la suma del peso neto */}
                <h3 className="font-semibold max-xl:text-sm text-lg">
                  Resultados: {filteredData.length}
                </h3>
                <h3 className="font-semibold max-xl:text-sm text-lg">
                  Tonelaje: {totalPesoNeto.toFixed(2)}
                </h3>
              </div>
              <div className="flex items-center bg-[#182540] m-2 p-2 xl:w-1/3 text-white font-bold rounded hover:bg-[#6D80A6] hover:text-[#f2f2f2] justify-between">
                <span>Exportar</span>
                <div className="flex">
                  <button className="m-2 p-1" onClick={handleExport}>
                    <img src={iconExcel} alt="Icon" className="w-6 h-6" />
                  </button>
                  <button className="m-2 p-1">
                    <img src={iconTxt} alt="Icon" className="w-6 h-6" />
                  </button>
                  <button className="m-2 p-1">
                    <img src={iconPdf} alt="Icon" className="w-6 h-6" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Consultas;
