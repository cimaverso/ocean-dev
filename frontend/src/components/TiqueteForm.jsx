import React, { useState, useEffect, useRef } from "react";
import moment from "moment-timezone";
import axios from "axios";
import SelectField from "./Layouts/SelectField";
import FormSection from "./FormSection";
import IngresoForm from "./IngresoForm";
import DespachoForm from "./DespachoForm";
import ServiciosForm from "./ServiciosForm";
import InputField from "./Layouts/InputField";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Notification from "./Layouts/Notificacion";
import { useAuth } from "../context/AuthContext";
import { CursorArrowRaysIcon } from "@heroicons/react/24/solid";

const TiqueteForm = ({ formType: initialFormType, initialData }) => {
  const location = useLocation();
  const [ticketNumber, setTicketNumber] = useState(initialData.registro);
  const [ticketNumberFinal, setTicketNumberFinal] = useState(
    initialData.tiquete
  );
  const [formType, setFormType] = useState(
    location.state?.formType || initialFormType
  );
  const [vehicleInfo, setVehicleInfo] = useState({
    placa: initialData.placa || "",
  });
  const [trailerInfo, setTrailerInfo] = useState({
    trailer: initialData.trailer || "",
    trai_id: initialData.trai_id || null,
  });
  const [facturaInfo, setFacturaInfo] = useState({
    numero_factura: initialData.numero_factura || "",
    fac_id: initialData.fac_id || null,
  });

  const [conductInfo, setConductInfo] = useState({
    conductor: initialData.conductor || "",
    cedulaConductor: initialData.cedulaConductor || "",
    conduct_id: initialData.conduct_id || null,
  });

  const [peso, setPeso] = useState({
    tara: initialData.pesoTara || "",
    bruto: initialData.pesoBruto || "",
    neto: initialData.pesoNeto || "",
  });

  const [facturaOptions, setFacturaOptions] = useState([]);
  const [facturaSeleccionada, setFacturaSeleccionada] = useState("");
  const [fechaSalida, setFechaSalida] = useState(initialData.fSalida || "");
  const [horaSalida, setHoraSalida] = useState(initialData.hSalida || "");
  const [currentDate, setCurrentDate] = useState("");
  const [currentTime, setCurrentTime] = useState("");
  const [productos, setProductos] = useState([]);
  const [servicios, setServicios] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [proveedores, setProveedores] = useState([]);
  const [terceros, setTerceros] = useState([]);
  const [placa, setPlaca] = useState([]);
  const [compradores, setCompradores] = useState([]);
  const [transportadoras, setTransportadoras] = useState([]);
  const [destinos, setDestinos] = useState([]);
  const [origenes, setOrigenes] = useState([]);
  const [unidades, setUnidades] = useState([]);
  const [observaciones, setObservaciones] = useState(
    initialData.observaciones || ""
  );
  const [cantidad, setCantidad] = useState([]);
  const [isFinalizing, setIsFinalizing] = useState(
    location.state?.isFinalizing || false
  );
  const [isHistorial, setIsHistorial] = useState(
    location.state?.isHistorial || false
  );
  const [isTiquete, setIsTiquete] = useState(
    location.state?.isTiquete || false
  );
  const [patios, setPatios] = useState([]);
  const [notification, setNotification] = useState({ message: "", type: "" });
  const [isProcessing, setIsProcessing] = useState(false); // Nuevo estado para controlar el procesamiento
  const [isTiqueteFinalizado, setIsTiqueteFinalizado] = useState(false);
  const navigate = useNavigate();
  const { getToken, userId } = useAuth();
  const [fechaEntrada, setFechaEntrada] = useState(initialData.fEntrada || "");
  const [horaEntrada, setHoraEntrada] = useState(initialData.hEntrada || "");

  //CAMBIOS
  const [vehicleOptions, setVehicleOptions] = useState([]); // Nuevo estado
  const [conductorOptions, setConductorOptions] = useState([]); // Nuevo estado
  const [cedulaOptions, setCedulaOptions] = useState([]);
  const [trailerOptions, setTrailerOptions] = useState([]);

  const ingresoFormRef = useRef();
  const despachoFormRef = useRef();
  const servicioFormRef = useRef();

  const [registroId, setRegistroId] = useState(null);
  // Usamos useRef para rastrear si el registro ya se creó
  const registroCreadoRef = useRef(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const incluirInactivos =
          isFinalizing || isHistorial || isTiquete ? "true" : "false";

        if (
          (formType === "INGRESO" ||
            formType === "DESPACHO" ||
            formType === "SERVICIOS") &&
          !ticketNumber &&
          !isFinalizing &&
          !isHistorial
        ) {
          const { data } = await axios.get(
            "http://127.0.0.1:5000/obtener_proximo_id"
          );

          setTicketNumber(data.proximo_id_registro);
          setTicketNumberFinal(data.proximo_id_tiquete);

          // Paso 2: Crear el registro si aún no se ha creado
          if (!registroCreadoRef.current) {
            try {
              const response = await axios.post(
                "http://127.0.0.1:5000/crear_registro",
                {
                  tipo_id:
                    formType === "INGRESO"
                      ? 1
                      : formType === "DESPACHO"
                      ? 2
                      : 3,
                  fecha_entrada: new Date().toISOString().split("T")[0],
                  hora_entrada: new Date().toLocaleTimeString("en-US", {
                    hour12: false,
                  }),
                }
              );

              setTicketNumber(response.data.id); // Asegurar que el ID guardado es el mismo que se muestra
              registroCreadoRef.current = true; // Marcar como creado
              console.log(`Registro creado con ID: ${response.data.id}`);
            } catch (error) {
              console.error("Error al crear el registro:", error);
            }
          }
        }

        if (formType === "INGRESO") {
          const [
            productosEntradaData,
            productosESData,
            proveedoresData,
            patiosData,
            compradoresData,
            destinosData,
            origenesData,
          ] = await Promise.all([
            axios.get(
              `http://127.0.0.1:5000/productos_entrada?incluir_inactivos=${incluirInactivos}`
            ),
            axios.get(
              `http://127.0.0.1:5000/productos_entrada_salida?incluir_inactivos=${incluirInactivos}`
            ),
            axios.get(
              `http://127.0.0.1:5000/proveedores?incluir_inactivos=${incluirInactivos}`
            ),
            axios.get("http://127.0.0.1:5000/patios"),
            axios.get("http://127.0.0.1:5000/compradores"),
            axios.get("http://127.0.0.1:5000/destinos"),
            axios.get("http://127.0.0.1:5000/origenes"),
          ]);

          const productosCombinados = [
            ...productosEntradaData.data,
            ...productosESData.data,
          ];
          setProductos(productosCombinados);
          setProveedores(proveedoresData.data);
          setCompradores(compradoresData.data);
          setPatios(patiosData.data);
          setDestinos(destinosData.data);
          setOrigenes(origenesData.data);
        } else if (formType === "DESPACHO") {
          const [
            clientesData,
            productosSalidaData,
            productosESData,
            transportadorasData,
            patiosData,
            origenesData,
            destinosData,
          ] = await Promise.all([
            axios.get(
              `http://127.0.0.1:5000/clientes?incluir_inactivos=${incluirInactivos}`
            ),
            axios.get(
              `http://127.0.0.1:5000/productos_salida?incluir_inactivos=${incluirInactivos}`
            ),
            axios.get(
              `http://127.0.0.1:5000/productos_entrada_salida?incluir_inactivos=${incluirInactivos}`
            ),
            axios.get("http://127.0.0.1:5000/transportadoras"),
            axios.get("http://127.0.0.1:5000/patios"),
            axios.get("http://127.0.0.1:5000/origenes"),
            axios.get("http://127.0.0.1:5000/destinos"),
          ]);

          const productosCombinados = [
            ...productosSalidaData.data,
            ...productosESData.data,
          ];
          setClientes(clientesData.data);
          setProductos(productosCombinados);
          setTransportadoras(transportadorasData.data);
          setPatios(patiosData.data);
          setDestinos(destinosData.data);
          setOrigenes(origenesData.data);
        } else if (formType === "SERVICIOS") {
          const [
            tercerosData,
            compradoresData,
            serviciosData,
            patiosData,
            origenesData,
            unidadesData,
          ] = await Promise.all([
            axios.get(
              `http://127.0.0.1:5000/terceros?incluir_inactivos=${incluirInactivos}`
            ),
            axios.get("http://127.0.0.1:5000/compradores"),
            axios.get(
              `http://127.0.0.1:5000/servicios?incluir_inactivos=${incluirInactivos}`
            ),
            axios.get("http://127.0.0.1:5000/patios"),
            axios.get("http://127.0.0.1:5000/origenes"),
            axios.get("http://127.0.0.1:5000/unidades"),
          ]);

          setTerceros(tercerosData.data);
          setCompradores(compradoresData.data);
          setServicios(serviciosData.data);
          setPatios(patiosData.data);
          setOrigenes(origenesData.data);
          setUnidades(unidadesData.data);
        }
      } catch (error) {
        setNotification({
          message: "Error fetching data: " + error.message,
          type: "error",
        });
      }
    };

    fetchData();
  }, [formType, isFinalizing, isHistorial, isTiquete]);

  const cerrarRegistro = async () => {
    try {
      const token = await getToken();
      await axios.post(
        `http://127.0.0.1:5000/cerrar_registro/${ticketNumber}`,
        { user_id: userId },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
    } catch (error) {
      console.error(
        "Error al cerrar el registro:",
        error.response?.data || error.message
      );
      setNotification({
        message: "Error al cerrar el registro",
        type: "error",
      });
    }
  };

  useEffect(() => {
    const abrirRegistro = async () => {
      try {
        const token = await getToken();
        const response = await axios.post(
          `http://127.0.0.1:5000/abrir_registro/${ticketNumber}`,
          { user_id: userId },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (
          response.data.message ===
          "El registro ya está abierto por este usuario"
        ) {
          setNotification({
            message: "El registro ya está abierto por ti.",
            type: "info",
          });
        } else {
          setNotification({
            message: "Registro abierto exitosamente.",
            type: "success",
          });
        }
      } catch (error) {
        if (error.response?.status === 400) {
          setNotification({
            message:
              error.response?.data?.error || "El registro ya está ocupado.",
            type: "error",
          });

          // Esperar 3 segundos (3000ms) antes de redirigir
          setTimeout(() => {
            navigate("/registro");
          }, 3000);
        } else {
          setNotification({
            message: "Error al abrir el registro.",
            type: "error",
          });

          // Esperar 3 segundos antes de redirigir
          setTimeout(() => {
            navigate("/registro");
          }, 2000);
        }
      }
    };

    if (isFinalizing) {
      abrirRegistro();
    }

    return () => {
      if (ticketNumber) {
        cerrarRegistro();
      } else {
        console.log("No se puede cerrar el regstro porque es undefinied");
      }
    };
  }, [isFinalizing, ticketNumber, userId]);

  const cerrarTiquete = async () => {
    try {
      const token = await getToken();

      await axios.post(
        `http://127.0.0.1:5000/cerrar_tiquete/${ticketNumberFinal}`,
        { user_id: userId },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
    } catch (error) {
      console.error(
        "Error al cerrar el registro:",
        error.response?.data || error.message
      );
      setNotification({
        message: "Error al cerrar el registro",
        type: "error",
      });
    }
  };

  useEffect(() => {
    const abrirTiquete = async () => {
      try {
        console.log("usuario", userId);
        console.log("Tiquete ID", ticketNumberFinal);
        const token = await getToken();
        const response = await axios.post(
          `http://127.0.0.1:5000/abrir_tiquete/${ticketNumberFinal}`,
          { user_id: userId },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (
          response.data.message ===
          "El Tiqeute ya está abierto por este usuario"
        ) {
          setNotification({
            message: "El tiquete ya está abierto por ti.",
            type: "info",
          });
        } else {
          setNotification({
            message: "Tiquete abierto exitosamente.",
            type: "success",
          });
        }
      } catch (error) {
        if (error.response?.status === 400) {
          setNotification({
            message:
              error.response?.data?.error || "El tiquete ya está ocupado.",
            type: "error",
          });

          // Esperar 3 segundos (3000ms) antes de redirigir
          setTimeout(() => {
            navigate("/registro");
          }, 3000);
        } else {
          setNotification({
            message: "Error al abrir el tiquete.",
            type: "error",
          });

          // Esperar 3 segundos antes de redirigir
          setTimeout(() => {
            navigate("/registro");
          }, 2000);
        }
      }
    };

    if (isHistorial || isTiquete) {
      abrirTiquete();
    }

    return () => {
      if (ticketNumberFinal) {
        cerrarTiquete();
      } else {
        console.log("No se peude cerrar el tiquete porque es undefined");
      }
    };
  }, [isHistorial, isTiquete, ticketNumberFinal, userId]);

  useEffect(() => {
    const now = moment().tz("America/Bogota");
    setCurrentDate(now.format("YYYY-MM-DD"));
    setCurrentTime(now.format("HH:mm"));
  }, []);

  const fetchVehiculos = async () => {
    try {
      const response = await axios.get("http://localhost:5000/vehiculos");
      return response.data.map((vehiculo) => ({
        value: vehiculo.placa,
        label: vehiculo.placa,
      }));
    } catch (error) {
      console.error("Error fetching vehicle options:", error);
      return [];
    }
  };
  const fetchTrailers = async () => {
    try {
      const response = await axios.get("http://localhost:5000/trailers");
      return response.data.map((trailer) => ({
        value: trailer.trailer,
        label: trailer.trailer,
      }));
    } catch (error) {
      console.error("Error fetching trailer options:", error);
      return [];
    }
  };
  const fetchConductores = async () => {
    try {
      const response = await axios.get("http://localhost:5000/conductores");
      console.log("Conductores recibidos:", response.data);
      return response.data.map((conductor) => ({
        value: conductor.nombre_conductor, // Almacena el ID del conductor
        label: conductor.nombre_conductor, // Almacena el nombre del conductor
      }));
    } catch (error) {
      console.error("Error fetching conductor options:", error);
      return [];
    }
  };
  const fetchConductorCedula = async () => {
    try {
      const response = await axios.get("http://localhost:5000/conductores");
      console.log("Conductores recibidos:", response.data);
      return response.data.map((cedula) => ({
        value: cedula.cedula_conductor, // Almacena el ID del conductor
        label: cedula.cedula_conductor, // Almacena el nombre del conductor
      }));
    } catch (error) {
      console.error("Error fetching conductor options:", error);
      return [];
    }
  };
  const fetchFacturas = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/facturas");
      console.log("Factura recibida", response.data);

      return response.data.map((factura) => ({
        value: factura.id_factura,
        label: factura.numero_factura,
      }));
    } catch (error) {
      console.log("Error al buscar facturas", error);
      setFacturaOptions([]);
    }
  };

  useEffect(() => {
    const fetchOptions = async () => {
      const facturas = await fetchFacturas();
      const vehiculos = await fetchVehiculos();
      const trailers = await fetchTrailers();
      const conductores = await fetchConductores();
      const cedulaConductor = await fetchConductorCedula();

      setFacturaOptions(facturas);
      setVehicleOptions(vehiculos);
      setTrailerOptions(trailers);
      setConductorOptions(conductores);
      setCedulaOptions(cedulaConductor);
      console.log("Opciones de conductores actualizadas:", conductores); // Agrega este log
    };

    fetchOptions();
  }, []);

  const handlePlacaChange = async (selectedOption) => {
    const placa = selectedOption.value;
    try {
      const { data } = await axios.get(
        `http://localhost:5000/vehiculo?vehi_placa=${placa}`
      );
      console.log("placa id", data.id_vehiculo);
      setVehicleInfo((prevState) => ({
        ...prevState,
        placa: placa,

        vehi_id: data.id_vehiculo,
      }));
    } catch (error) {
      if (error.response && error.response.status === 404) {
        setNotification({ message: "Vehículo no encontrado", type: "error" });
      } else {
        setNotification({
          message: "Error fetching vehicle info",
          type: "error",
        });
      }
    }
  };

  const handleTrailerChange = async (selectedOption) => {
    const trailer = selectedOption.value;
    try {
      const { data } = await axios.get(
        `http://localhost:5000/trailer?trai_trailer=${trailer}`
      );

      setTrailerInfo((prevState) => ({
        ...prevState,
        trailer: trailer,
        trai_id: data.id_trailer,
      }));
    } catch (error) {
      if (error.response && error.response.status === 404) {
        setNotification({ message: "Vehículo no encontrado", type: "error" });
      } else {
        setNotification({
          message: "Error fetching vehicle info",
          type: "error",
        });
      }
    }
  };

  const handleConductorChange = async (selectedOption) => {
    const conductor = selectedOption.value;
    try {
      const { data } = await axios.get(
        `http://localhost:5000/conductor?conduct_nombre=${conductor}`
      );
      setConductInfo((prevState) => ({
        ...prevState,
        conductor: conductor,
        cedulaConductor: data.cedula_conductor || "",
        conduct_id: data.id_conductor,
      }));
    } catch (error) {
      if (error.response && error.response.status === 404) {
        setNotification({ message: "Conductor no encontrado", type: "error" });
      } else {
        setNotification({
          message: "Error fetching vehicle info",
          type: "error",
        });
      }
    }
  };

  const handleCedulaChange = async (selectedOption) => {
    const cedula = selectedOption.value;
    try {
      const { data } = await axios.get(
        `http://localhost:5000/conductor?conduct_cedula=${cedula}`
      );
      setConductInfo((prevState) => ({
        ...prevState,
        conductor: data.nombre_conductor || "",
        cedulaConductor: cedula,
        conduct_id: data.id_conductor,
      }));
    } catch (error) {
      if (error.response && error.response.status === 404) {
        setNotification({ message: "Conductor no encontrado", type: "error" });
      } else {
        setNotification({
          message: "Error fetching conductor info",
          type: "error",
        });
      }
    }
  };

  const handleFacturaChange = async (selectedOption) => {
    const factura_id = selectedOption.value; // Asegúrate de enviar el ID
    console.log("Factura seleccionada - ID:", factura_id);

    try {
      const { data } = await axios.get(
        `http://localhost:5000/factura?numero_factura=${factura_id}` // Enviar ID en lugar de fecha
      );
      setFacturaInfo((prevState) => ({
        ...prevState,
        numero_factura: data.numero_factura || "",
        fac_id: data.id_factura,
      }));
    } catch (error) {
      if (error.response && error.response.status === 404) {
        console.log("Factura no encontrada");
        setNotification({ message: "Factura no encontrada", type: "error" });
      } else {
        console.log("Error en la solicitud:", error);
        setNotification({
          message: "Error fetching factura info",
          type: "error",
        });
      }
    }
  };

  useEffect(() => {
    const tara = peso.tara || 0;
    const bruto = peso.bruto || 0;
    const neto = formType === "DESPACHO" ? bruto - tara : bruto - tara;
    setPeso((prevPeso) => ({
      ...prevPeso,
      neto: neto,
    }));
  }, [peso.tara, peso.bruto]);

  const handlePesoBrutoChange = (e) => {
    const value = e.target.value.replace(/\./g, ""); // Elimina puntos de mil si existen
    setPeso((prevPeso) => ({
      ...prevPeso,
      bruto: parseInt(value, 10) || null, // Conviértelo a número entero
    }));
  };

  const handlePesoTaraChange = (e) => {
    const value = e.target.value.replace(/\./g, ""); // Elimina puntos de mil si existen
    setPeso((prevPeso) => ({
      ...prevPeso,
      tara: parseInt(value, 10) || null, // Conviértelo a número entero
    }));
  };

  const handleObservacionesChange = (e) => {
    setObservaciones(e.target.value);
  };

  const handleSubmitRegistro = async (registroData, tipoId) => {
    const currentVehiId = vehicleInfo.vehi_id;
    const currentConductId = conductInfo.conduct_id;
    const currentTraiId = trailerInfo.trai_id;
    const currentFacturaId = facturaInfo.fac_id;

    console.log("IDa mandar:", currentFacturaId);

    try {
      await axios.put(
        `http://127.0.0.1:5000/procesar_registro/${ticketNumber}`,
        {
          ...registroData,
          tipo_id: tipoId, // Este valor ya no es necesario actualizar en el registro existente
          peso_bruto:
            formType === "INGRESO" || formType === "SERVICIOS"
              ? peso.bruto
              : null,
          peso_tara: formType === "DESPACHO" ? peso.tara : null,
          vehi_id: currentVehiId,
          trai_id: currentTraiId,
          conduct_id: currentConductId,
          observaciones: observaciones,
          id_factura: currentFacturaId,
        }
      );

      setNotification({
        message: "Registro procesado exitosamente",
        type: "success",
      });
    } catch (error) {
      setNotification({
        message:
          "Error procesando registro: " +
          (error.response ? error.response.data.error : error.message),
        type: "error",
      });
    }
  };

  const handleFinalizarTiquete = async (finalizarData) => {
    const currentVehiId = vehicleInfo.vehi_id;
    const currentConductId = conductInfo.conduct_id;
    const currentTraiId = trailerInfo.trai_id;
    const currentFacturaId = facturaInfo.fac_id;
    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/guardar_tiquete",
        {
          ...finalizarData,
          fecha_entrada: fechaEntrada || initialData.fEntrada,
          hora_entrada: horaEntrada || initialData.hEntrada,
          fecha_salida: fechaSalida || currentDate,
          hora_salida: horaSalida || currentTime,
          peso_tara: peso.tara,
          peso_bruto: peso.bruto,
          peso_neto: peso.neto,
          observaciones: observaciones,
          id_registro: initialData.id_registro,
          vehi_id: currentVehiId, // Puede ser nulo si no se seleccionó
          conduct_id: currentConductId, // Puede ser nulo si no se seleccionó
          trai_id: currentTraiId,
          tipo: initialData.tipo,
          id_factura: currentFacturaId,
        }
      );

      const tiqueteId = response.data.tiquete_id; // Obtén el ID del tiquete
      setTicketNumberFinal(tiqueteId); // Actualiza ticketNumber con el ID del tiquete
      setIsTiqueteFinalizado(true); // Marca que el tiquete ha sido finalizado
      setNotification({
        message: "Tiquete guardado exitosamente",
        type: "success",
      });
    } catch (error) {
      setNotification({
        message:
          "Error guardando tiquete: " +
          (error.response ? error.response.data.message : error.message),
        type: "error",
      });
    }
  };

  const handleActualizarTiquete = async (actualizarData) => {
    const currentVehiId = vehicleInfo.vehi_id;
    const currentConductId = conductInfo.conduct_id;
    const currentTraiId = trailerInfo.trai_id;
    const currentFacturaId = facturaInfo.fac_id;
    try {
      await axios.put(
        `http://127.0.0.1:5000/actualizar_tiquete/${ticketNumberFinal}`,
        {
          ...actualizarData,
          fecha_entrada: fechaEntrada, // Use the user-provided date
          hora_entrada: horaEntrada, // Use the user-provided time
          fecha_salida: fechaSalida, // Use the user-provided date
          hora_salida: horaSalida, // Use the user-provided time
          pesoTara: peso.tara,
          pesoBruto: peso.bruto,
          pesoNeto: peso.neto,
          placa: vehicleInfo.placa,
          observaciones: observaciones,
          id_registro: initialData.id_registro,
          vehi_id: currentVehiId, // Puede ser nulo si no se seleccionó
          conduct_id: currentConductId, // Puede ser nulo si no se seleccionó
          trai_id: currentTraiId,
          tipo: initialData.tipo,
          id_factura: currentFacturaId,
        }
      );
      setNotification({
        message: "Tiquete actualizado exitosamente",
        type: "success",
      });
    } catch (error) {
      setNotification({
        message:
          "Error actualizando tiquete: " +
          (error.response ? error.response.data.error : error.message),
        type: "error",
      });
    }
  };

  const handleImprimirTiquete = async () => {
    try {
      let token = await getToken();
      if (!token) {
        throw new Error(
          "No se encontró el token. Debe iniciar sesión nuevamente."
        );
      }

      const response = await axios.get(
        `http://127.0.0.1:5000/imprimir_tiquete?tiquete_id=${ticketNumberFinal}`,
        {
          responseType: "blob",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const url = window.URL.createObjectURL(
        new Blob([response.data], { type: "application/pdf" })
      );
      window.open(url, "_blank");
      window.URL.revokeObjectURL(url);

      setNotification({
        message: "Tiquete imprimido exitosamente",
        type: "success",
      });
    } catch (error) {
      setNotification({
        message: "Error al imprimir el tiquete: " + error.message,
        type: "error",
      });
    }
  };

  const handleProcesarIngreso = () => {
    let data = {};
    if (ingresoFormRef.current) {
      ingresoFormRef.current.handleProcesar();
      data = ingresoFormRef.current.getFormData();
    }
    handleSubmitRegistro(data, 1);
  };

  const handleProcesarDespacho = () => {
    let data = {};
    if (despachoFormRef.current) {
      despachoFormRef.current.handleProcesar();
      data = despachoFormRef.current.getFormData();
    }
    handleSubmitRegistro(data, 2);
  };

  const handleProcesarServicios = () => {
    let data = {};
    if (servicioFormRef.current) {
      servicioFormRef.current.handleProcesar();
      data = servicioFormRef.current.getFormData();
    }
    handleSubmitRegistro(data, 3);
  };

  const handleProcesar = async () => {
    if (isProcessing) return; // Evitar procesar si ya se está procesando

    if (!vehicleInfo.placa || !conductInfo.conductor) {
      setNotification({
        message:
          "Por favor complete los campos obligatorios: Placa, Conductor ",
        type: "error",
      });
      return;
    }

    setIsProcessing(true); // Desactivar el botón
    try {
      if (formType === "SERVICIOS") {
        handleProcesarServicios();
      } else if (formType === "INGRESO") {
        handleProcesarIngreso();
      } else if (formType === "DESPACHO") {
        handleProcesarDespacho();
      }
      navigate("/registro");
    } finally {
      setIsProcessing(false); // Reactivar el botón después del procesamiento
    }
  };

  const handleFinalizar = async () => {
    if (isProcessing) return;

    setIsProcessing(true);

    try {
      let data = {};

      if (formType === "SERVICIOS" && servicioFormRef.current) {
        data = servicioFormRef.current.getFormData();
      } else if (formType === "INGRESO" && ingresoFormRef.current) {
        data = ingresoFormRef.current.getFormData();
      } else if (formType === "DESPACHO" && despachoFormRef.current) {
        data = despachoFormRef.current.getFormData();
      }

      await cerrarRegistro();

      await handleFinalizarTiquete(data);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleActualizar = async () => {
    if (isProcessing) return;

    setIsProcessing(true);

    try {
      let data = {};

      if (formType === "SERVICIOS" && servicioFormRef.current) {
        data = servicioFormRef.current.getFormData();
      } else if (formType === "INGRESO" && ingresoFormRef.current) {
        data = ingresoFormRef.current.getFormData();
      } else if (formType === "DESPACHO" && despachoFormRef.current) {
        data = despachoFormRef.current.getFormData();
      }

      await cerrarTiquete();

      await handleActualizarTiquete(data);
    } finally {
      setIsProcessing(false);
    }
  };

  const formTypes = [
    { value: "", label: "Seleccione un formulario" },
    { value: "INGRESO", label: "Ingreso" },
    { value: "DESPACHO", label: "Despacho" },
    { value: "SERVICIOS", label: "Servicios" },
  ];

  const handleFormTypeChange = (selectedOption) => {
    setFormType(selectedOption ? selectedOption.value : "");
    console.log(
      "Form Type selected:",
      selectedOption ? selectedOption.value : ""
    );
  };

  const handleFetchPesoTara = async () => {
    try {
      const response = await axios.get("http://localhost:5000/obtener_peso");
      setPeso((prevPeso) => ({
        ...prevPeso,
        tara: response.data.peso, // Solo actualiza tara
      }));
    } catch (error) {
      console.error("Error fetching Peso Tara:", error);
    }
  };

  const handleFetchPesoBruto = async () => {
    try {
      const response = await axios.get("http://localhost:5000/obtener_peso");
      setPeso((prevPeso) => ({
        ...prevPeso,
        bruto: response.data.peso, // Solo actualiza bruto
      }));
    } catch (error) {
      console.error("Error fetching Peso Bruto:", error);
    }
  };

  return (
    <div className="mx-auto p-1 ">
      <div className="rounded p-1 ">
        <div className="bg-[#6D80A6] text-white font-bold text-lg m-1 h-9 rounded justify-around items-center">
          <div className="grid grid-cols-7 gap-2 items-center justify-around">
            <div className="ml-1 p-1 flex w-11/12 col-span-3 ">
              <label className="text-xs 2xl:text-base text-center w-20 font-bold m-1 block mr-1">
                Registro
              </label>

              {isHistorial || isTiquete || isFinalizing ? (
                <>
                  <input
                    className="bg-white text-red-800 w-28 xl:w-3/4 text-sm 2xl:textlg text-center h-6 p-2 mr-3 focus:outline-none focus:ring-2 focus:[#6D80A6]"
                    value={ticketNumber}
                    readOnly
                  />

                  <label className="text-xs 2xl:text-base text-center w-20 font-bold m-1 block mr-1">
                    Tiquete
                  </label>

                  <input
                    className="bg-white w-28 xl:w-3/4 text-sm 2xl:textlg text-center text-[#182540] h-6 px-1 focus:outline-none focus:ring-2 focus:[#6D80A6]"
                    value={ticketNumberFinal}
                    readOnly
                  />
                </>
              ) : (
                <input
                  className="bg-white w-28 xl:w-3/4 text-base 2xl:textlg text-center text-[#182540] h-6 px-1 focus:outline-none focus:ring-2 focus:[#6D80A6]"
                  value={ticketNumber}
                  readOnly
                />
              )}
            </div>

            <div className="col-span-2">
              {formType === "INGRESO" && (
                <SelectField
                  label="Facturado"
                  id="formType"
                  options={facturaOptions}
                  value={facturaInfo.fac_id}
                  onChange={handleFacturaChange}
                /> 
              )}
            </div>
            <div className="col-span-2">
              <SelectField
                label="Tipo"
                id="formType"
                options={formTypes}
                value={formType}
                onChange={handleFormTypeChange}
                isDisabled={isFinalizing || isHistorial || isTiquete}
              />
            </div>
          </div>
        </div>
        <FormSection title="Datos del Vehículo">
          <div className="grid grid-cols-6 gap-2 justify-center items-center ">
            {/* Placa */}
            <div className="m-1 w-full flex flex-col items-center">
              <label className="text-xs 2xl:text-base font-bold m-1 text-center">
                Placa
              </label>
              <SelectField
                apiEndpoint='http://localhost:5000/vehiculos' 
                postApiEndpoint="http://localhost:5000/crear_vehiculo"
                options={vehicleOptions}
                onChange={handlePlacaChange}
                value={vehicleInfo.placa}
                className="appearance-none text-xs 2xl:text-base w-full h-7 border-2 border-[#6D80A6] rounded p-1 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-[#6D80A6]"
              />
            </div>

            {/* Conductor (ocupa 2 columnas y está centrado) */}
            <div className="m-1 w-full col-span-2 flex flex-col items-center justify-center">
              <label className="text-xs 2xl:text-base font-bold m-1 text-center">
                Conductor
              </label>
              <SelectField
                apiEndpoint='http://localhost:5000/conductores'
                postApiEndpoint="http://localhost:5000/crear_conductor"
                options={conductorOptions}
                onChange={handleConductorChange}
                value={conductInfo.conductor}
                className="appearance-none text-xs 2xl:text-base w-full h-7 border-2 border-[#6D80A6] rounded p-1 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-[#6D80A6]"
              />
            </div>

            {/* Nro. Documento (ocupa 2 columnas) */}
            <div className="m-1 w-full col-span-2 flex flex-col items-center">
              <label className="text-xs 2xl:text-base font-bold m-1 text-center">
                Nro. Documento
              </label>
              <SelectField
                apiEndpoint='http://localhost:5000/conductores'
                postApiEndpoint="http://localhost:5000/crear_conductor"
                options={cedulaOptions}
                onChange={handleCedulaChange}
                value={conductInfo.cedulaConductor}
                className="appearance-none text-xs 2xl:text-base w-full h-7 border-2 border-[#6D80A6] rounded p-1 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-[#6D80A6]"
              />
            </div>

            {/* Tráiler (solo si aplica) */}
            {(formType === "DESPACHO" ||
              formType === "INGRESO" ||
              formType === "SERVICIOS" ||
              formType.startsWith("FINALIZAR")) && (
              <div className="m-1 w-full flex flex-col items-center">
                <label className="text-xs text-red-700 2xl:text-base font-bold m-1 text-center">
                  Tráiler
                </label>
                <SelectField
                  apiEndpoint='http://localhost:5000/trailers'
                  postApiEndpoint="http://localhost:5000/crear_trailer"
                  options={trailerOptions}
                  onChange={handleTrailerChange}
                  value={trailerInfo.trailer}
                  className="appearance-none text-xs 2xl:text-base w-full h-7 border-2 border-[#6D80A6] rounded p-1 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-[#6D80A6]"
                />
              </div>
            )}
          </div>
        </FormSection>

        {formType === "INGRESO" && (
          <IngresoForm
            ref={ingresoFormRef}
            productos={productos}
            proveedores={proveedores}
            compradores={compradores}
            patios={patios}
            origenes={origenes}
            vehicleInfo={vehicleInfo}
            pesoBruto={peso.bruto}
            pesoTara={peso.tara}
            handlePesoBrutoChange={handlePesoBrutoChange}
            handlePesoTaraChange={handlePesoTaraChange}
            onSubmit={handleSubmitRegistro}
            onFinalizar={handleFinalizarTiquete}
            onAcualizar={handleActualizarTiquete}
          />
        )}

        {formType === "DESPACHO" && (
          <DespachoForm
            ref={despachoFormRef}
            clientes={clientes}
            productos={productos}
            transportadoras={transportadoras}
            vehicleInfo={vehicleInfo}
            destinos={destinos}
            origenes={origenes}
            patios={patios}
            pesoTara={peso.tara}
            pesoBruto={peso.bruto}
            handlePesoTaraChange={handlePesoTaraChange}
            handlePesoBrutoChange={handlePesoBrutoChange}
            onSubmit={handleSubmitRegistro}
            onFinalizar={handleFinalizarTiquete}
            onAcualizar={handleActualizarTiquete}
          />
        )}

        {formType === "SERVICIOS" && (
          <ServiciosForm
            ref={servicioFormRef}
            terceros={terceros}
            servicios={servicios}
            compradores={compradores}
            origenes={origenes}
            patios={patios}
            vehicleInfo={vehicleInfo}
            pesoBruto={peso.bruto}
            unidades={unidades}
            cantidad={cantidad}
            setCantidad={setCantidad}
            handlePesoBrutoChange={handlePesoBrutoChange}
            onSubmit={handleSubmitRegistro}
            onFinalizar={handleFinalizarTiquete}
            onAcualizar={handleActualizarTiquete}
          />
        )}

        <section>
          <FormSection title="Báscula">
            <div className="grid grid-cols-3 gap-1">
              <InputField
                label="Fecha Entrada"
                id="fechaEntrada"
                type="date"
                value={
                  fechaEntrada
                    ? fechaEntrada
                    : initialData.fEntrada || currentDate
                }
                onChange={(e) => setFechaEntrada(e.target.value)}
                tabIndex="-1"
              />
              <InputField
                label="Hora Entrada"
                id="horaEntrada"
                type="time"
                value={
                  horaEntrada
                    ? horaEntrada
                    : initialData.hEntrada || currentTime
                }
                onChange={(e) => setHoraEntrada(e.target.value)}
                tabIndex="-1"
              />
              {formType === "DESPACHO" ? (
                <>
                  <div className="m-0 p-1 flex w-full justify-between">
                    <label className="text-xs xl:text-base w-1/4 font-bold block">
                      Peso Tara
                    </label>
                    <input
                      className="shadow w-3/4 text-base appearance-none border-2 border-[#6D80A6] rounded text-[#182540] leading-tight focus:outline-none focus:ring-2 focus:[#6D80A6]"
                      type="text"
                      id="pesoTara"
                      value={peso.tara}
                      onChange={handlePesoTaraChange}
                    />
                    <button
                      className="text-[#182540] rounded"
                      onClick={handleFetchPesoTara}
                    >
                      <CursorArrowRaysIcon className="w-6" />
                    </button>
                  </div>
                  <InputField
                    label="Fecha Salida"
                    id="fechaSalida"
                    type="date"
                    value={
                      fechaSalida
                        ? fechaSalida
                        : initialData.fSalida || currentDate
                    }
                    onChange={(e) => setFechaSalida(e.target.value)}
                    tabIndex="-1"
                  />
                  <InputField
                    label="Hora Salida"
                    id="horaSalida"
                    type="time"
                    value={
                      horaSalida
                        ? horaSalida
                        : initialData.hSalida || currentTime
                    }
                    onChange={(e) => setHoraSalida(e.target.value)}
                    tabIndex="-1"
                  />
                  <div className="m-0 p-1 flex w-full justify-between">
                    <label className="text-xs xl:text-base w-1/4 font-bold block">
                      Peso Bruto
                    </label>
                    <input
                      className="shadow w-3/4 text-base appearance-none border-2 border-[#6D80A6] rounded text-[#182540] leading-tight focus:outline-none focus:ring-2 focus:[#6D80A6]"
                      type="number"
                      id="pesoBruto"
                      value={
                        isFinalizing || isHistorial || isTiquete
                          ? peso.bruto
                          : ""
                      }
                      onChange={handlePesoBrutoChange}
                    />
                    <button
                      className="text-[#182540] rounded"
                      onClick={handleFetchPesoBruto}
                    >
                      <CursorArrowRaysIcon className="w-6" />
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <div className="m-0 p-1 flex w-full justify-between">
                    <label className="text-xs xl:text-base w-1/4 font-bold block">
                      Peso Bruto
                    </label>
                    <input
                      className="shadow w-3/4 text-base appearance-none border-2 border-[#6D80A6] rounded text-[#182540] leading-tight focus:outline-none focus:ring-2 focus:[#6D80A6]"
                      type="text"
                      id="pesoBruto"
                      value={peso.bruto}
                      onChange={handlePesoBrutoChange}
                    />
                    <button
                      className="text-[#182540] rounded"
                      onClick={handleFetchPesoBruto}
                    >
                      <CursorArrowRaysIcon className="w-6" />
                    </button>
                  </div>

                  <InputField
                    label="Fecha Salida"
                    id="fechaSalida"
                    type="date"
                    value={
                      isFinalizing
                        ? fechaSalida || initialData.fSalida || currentDate
                        : fechaSalida || initialData.fSalida || "" // Valor editable cuando no se está finalizando
                    }
                    onChange={(e) => setFechaSalida(e.target.value)}
                    tabIndex={"0"} // Habilitado para editar
                  />
                  <InputField
                    label="Hora Salida"
                    id="horaSalida"
                    type="time"
                    value={
                      isFinalizing
                        ? horaSalida || initialData.hSalida || currentTime
                        : horaSalida || initialData.hSalida || "" // Valor editable cuando no se está finalizando
                    }
                    onChange={(e) => setHoraSalida(e.target.value)}
                    tabIndex={"0"} // Habilitado para editar
                  />

                  <div className="m-0 p-1 flex w-full justify-between">
                    <label className="text-xs xl:text-base w-1/4 font-bold block">
                      Peso Tara
                    </label>
                    <input
                      className="shadow w-3/4 text-base appearance-none border-2 border-[#6D80A6] rounded text-[#182540] leading-tight focus:outline-none focus:ring-2 focus:[#6D80A6]"
                      type="text"
                      id="pesoTara"
                      value={
                        isFinalizing || isHistorial || isTiquete
                          ? peso.tara
                          : ""
                      }
                      onChange={handlePesoTaraChange}
                    />
                    <button
                      className="text-[#182540] rounded"
                      onClick={handleFetchPesoTara}
                    >
                      <CursorArrowRaysIcon className="w-6" />
                    </button>
                  </div>
                </>
              )}
              <div className="p-1 flex  col-end-4">
                <label className="text-xs xl:text-base w-1/4 font-bold block">
                  Peso Neto
                </label>
                <input
                  className="shadow w-[65%] xl:w-[70%] text-base appearance-none border-2 border-[#6D80A6] rounded text-[#182540] leading-tight focus:outline-none focus:ring-2 focus:[#6D80A6]"
                  type="number"
                  id="pesoNeto"
                  value={peso.neto}
                  readOnly
                />
              </div>
            </div>
          </FormSection>
        </section>

        <section>
          <FormSection title="Observaciones">
            <textarea
              id="observaciones"
              className="col-start-1 col-end-7 appearance-none border-2 border-[#6D80A6] rounded w-full py-1 px-1 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:[#6D80A6]"
              value={observaciones}
              onChange={handleObservacionesChange}
            />
          </FormSection>
        </section>
        <section>
          <div className="p-1 flex items-center justify-between text-xs 2xl:text-base">
            <button
              className={`${
                formType
                  ? "bg-[#182540] text-[#f2f2f2]"
                  : "bg-[#f2f2f2] text-[#182540]"
              } font-bold py-2 hover:bg-[#6D80A6] hover:text-[#f2f2f2] px-4 rounded focus:outline-none focus:ring-2 focus:[#6D80A6]`}
              type="button"
              disabled={!formType || isProcessing} // Desactivar el botón si ya se está procesando
              onClick={() => {
                if (isFinalizing) {
                  handleFinalizar();
                } else if (isHistorial || isTiquete) {
                  handleActualizar();
                } else {
                  handleProcesar();
                }
              }}
            >
              {isFinalizing
                ? "Finalizar Tiquete"
                : isHistorial || isTiquete
                ? "Actualizar Tiquete"
                : "Procesar"}
            </button>
            {(isHistorial || isFinalizing || isTiquete) && (
              <button
                className={`${
                  formType
                    ? "bg-[#182540] text-[#f2f2f2]"
                    : "bg-[#f2f2f2] text-[#182540]"
                } font-bold py-2 px-4 rounded hover:bg-[#6D80A6] hover:text-[#f2f2f2] focus:outline-none focus:ring-2 focus:[#6D80A6]`}
                type="button"
                onClick={handleImprimirTiquete} // Asegúrate de llamar a la función correcta
                disabled={isProcessing} // Desactivar el botón si ya se está procesando
              >
                Imprimir
              </button>
            )}
            <div>
              <button
                className="bg-[#182540] hover:bg-[#6D80A6] hover:text-[#f2f2f2] text-white font-bold py-2 px-4 rounded focus:outline-none focus:ring-2 focus:[#6D80A6]"
                onClick={async () => {
                  await cerrarRegistro(ticketNumber, userId);

                  navigate("/registro");
                }}
              >
                Salir
              </button>
            </div>
          </div>
        </section>
      </div>
      <Notification
        message={notification.message}
        type={notification.type}
        onConfirm={() => setNotification({ message: "", type: "" })}
        onCancel={() => setNotification({ message: "", type: "" })}
      />
    </div>
  );
};

export default TiqueteForm;
