import { useEffect, useState } from "react";
import axios from "axios";
import Notification from "../Layouts/Notificacion";
import SelectField from "../Layouts/SelectField";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import moment from "moment-timezone";


const Table = ({
  columns, data, editable, onEdit, isConsultasPage, onDoubleClickRow, showAddButton, formType,
  setClientes, setProveedores, setTerceros, setProductos, setVarios, setConductores, setVehiculos,
  setOrigenes, setDestinos, setCompradores, setTransportadoras, setPatios, setTrailers, setFacturas,
  clientes = [], proveedores = [], terceros = [], productos = [], varios = [], vehiculos = [],
  conductores = [], unidadesMedida = [], procesosProducto = [], patios = [], origenes = [],
  destinos = [], compradores = [], transportadoras = [], productosEntrada = [], productosEntradaSalida = [], productosSalida = [], trailers = [], facturas = []
}) => {
  const [tableData, setTableData] = useState([]);
  const [editingCell, setEditingCell] = useState(null);
  const [editedValue, setEditedValue] = useState("");
  const [newRow, setNewRow] = useState({});
  const [isAddingNewRow, setIsAddingNewRow] = useState(false);
  const [notification, setNotification] = useState({ message: "", type: "", onConfirm: null, onCancel: null });
  const [contextMenu, setContextMenu] = useState({ show: false, x: 0, y: 0, rowIndex: null });

  // Reset relevant states when formType changes
  useEffect(() => {
    setContextMenu({ show: false, x: 0, y: 0, rowIndex: null });
    setEditingCell(null);
    setEditedValue("");
    setNewRow({});
  }, [formType]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (typeof data === "function") {
          const result = await data();
          setTableData(result);
        } else {
          setTableData(data);
        }
      } catch (error) {
        setNotification({ message: "Error fetching data", type: "error" });
      }
    };

    fetchData();
  }, [data]);

  const handleDoubleClick = (rowIndex, columnName, currentValue) => {

    if (editable) {
      setEditingCell({ rowIndex, columnName });
      setEditedValue(currentValue);
    }
  }

  const handleEditCellChange = (e) => {
    setEditedValue(e.target.value);
  };

  const handleEditCellBlur = async () => {
    if (editingCell && !isAddingNewRow) {

      const { rowIndex, columnName } = editingCell;
      const updatedData = [...tableData];
      let editedValueToSend = editedValue;

      // Formatear fechas y horas si corresponde
      if (columnName === 'fEntrada' || columnName === 'fSalida') {
        editedValueToSend = moment(editedValue).tz("America/Bogota").format("YYYY-MM-DD");
      } else if (columnName === 'hEntrada' || columnName === 'hSalida') {
        editedValueToSend = moment(editedValue, "HH:mm").tz("America/Bogota").format("HH:mm");
      }
      updatedData[rowIndex] = { ...updatedData[rowIndex], [columnName]: editedValue };
      setTableData(updatedData);
      setEditingCell(null);

      try {
        const entity = updatedData[rowIndex];
        let endpoint = '';
        let dataToSend = {};
        let selectedPatioId = null;
        let selectedOrigenId = null;
        let selectedFacturaId = null;
        let selectedTransportadoraId = null;


        if (formType === 'Cliente' || formType === 'Proveedor' || formType === 'Tercero') {
          endpoint = 'http://localhost:5000/actualizar_entidad';
          dataToSend = {
            id_entidad: entity.id_entidad,
            codigo_entidad: entity.codigo_entidad,
            nombre_entidad: entity.nombre_entidad,
            telefono_entidad: entity.telefono_entidad,
            nit_entidad: entity.nit_entidad,
            direccion_entidad: entity.direccion_entidad,
          };
        } else if (formType === "Producto" || formType === "Varios") {
          endpoint = 'http://localhost:5000/actualizar_producto';
          dataToSend = {
            id_producto: entity.id_producto,
            codigo_producto: entity.codigo_producto,
            nombre_producto: entity.nombre_producto,
            unidad_medida: columnName === 'unidad_medida' ? editedValue : entity.unidad_medida,
            proceso_producto: columnName === 'proceso_producto' ? editedValue : entity.proceso_producto,
          };
        } else if (formType === "Vehiculo") {
          endpoint = 'http://localhost:5000/actualizar_vehiculo';
          dataToSend = {
            id_vehiculo: entity.id_vehiculo,
            placa: entity.placa,
            estado: entity.estado
          };

        } else if (formType === "Trailer") {
          endpoint = 'http://localhost:5000/actualizar_trailer';
          dataToSend = {
            id_trailer: entity.id_trailer,
            trailer: entity.trailer,

          };
        } else if (formType === "Conductor") {
          endpoint = 'http://localhost:5000/actualizar_conductor';
          dataToSend = {
            id_conductor: entity.id_conductor,
            codigo_conductor: entity.codigo_conductor,
            nombre_conductor: entity.nombre_conductor,
            cedula_conductor: entity.cedula_conductor
          };
        } else if (formType === "Origen") {
          endpoint = 'http://localhost:5000/actualizar_origen';
          dataToSend = {
            id_origen: entity.id_origen,
            codigo_origen: entity.codigo_origen,
            nombre_origen: entity.nombre_origen,

          };
        } else if (formType === "Comprador") {
          endpoint = 'http://localhost:5000/actualizar_comprador';
          dataToSend = {
            id_comprador: entity.id_comprador,
            codigo_comprador: entity.codigo_comprador,
            nombre_comprador: entity.nombre_comprador,

          };

        } else if (formType === "Factura") {
          endpoint = 'http://localhost:5000/actualizar_factura';
          dataToSend = {
            id_factura: entity.id_factura,
            numero_factura: entity.numero_factura,

          };
        } else if (formType === "Transportadora") {
          endpoint = 'http://localhost:5000/actualizar_transportadora';
          dataToSend = {
            id_transportadora: entity.id_transportadora,
            codigo_transportadora: entity.codigo_transportadora,
            nombre_transportadora: entity.nombre_transportadora,
            ciudad_transportadora: entity.ciudad_transportadora,
            telefono_transportadora: entity.telefono_transportadora,

          };

        } else if (formType === "Destino") {
          endpoint = 'http://localhost:5000/actualizar_destino';
          dataToSend = {
            id_destino: entity.id_destino,
            codigo_destino: entity.codigo_destino,
            nombre_destino: entity.nombre_destino,

          };

        } else if (formType === "Patio") {
          endpoint = 'http://localhost:5000/actualizar_patio';
          dataToSend = {
            id_patio: entity.id_patio,
            codigo_patio: entity.codigo_patio,
            nombre_patio: entity.nombre_patio,

          };
        } else if (formType === 'Ingreso' || formType === 'Despacho' || formType === 'Servicios') {

          const entityMapping = { 'Ingreso': proveedores, 'Despacho': clientes, 'Servicios': terceros };
          const productMapping = {
            'Ingreso': [...productosEntrada, ...productosEntradaSalida],
            'Despacho': [...productosSalida, ...productosEntradaSalida],
            'Servicios': varios
          };
          const entityArray = entityMapping[formType];
          const productArray = productMapping[formType];

          if (columnName === 'pesoBruto' || columnName === 'pesoTara') {
            const pesoBruto = columnName === 'pesoBruto' ? editedValue : entity.pesoBruto;
            const pesoTara = columnName === 'pesoTara' ? editedValue : entity.pesoTara;
            const pesoNeto = pesoBruto - pesoTara;

            // Actualizar los valores en dataToSend
            dataToSend.pesoBruto = pesoBruto;
            dataToSend.pesoTara = pesoTara;
            entity.pesoNeto = pesoNeto.toFixed(2);  // Recalcular y redondear el peso neto

          }
          dataToSend = {
            ...entity,
            [columnName]: editedValue,

          };

          if (columnName === 'nombreEntidad' || columnName === 'codigoEntidad') {
            // Find the selected entity either by name or code
            const selectedEntity = entityArray.find(entity => entity.nombre_entidad === editedValue || entity.codigo_entidad === editedValue);
            if (selectedEntity) {
              dataToSend.ent_id = selectedEntity.id_entidad;
              dataToSend.nombre_entidad = selectedEntity.nombre_entidad;
            }
          } else if (columnName === 'nombreComprador' || columnName === 'codigoComprador') {
            const selectedComprador = compradores.find(comp => comp.nombre_comprador === editedValue || comp.codigo_comprador === editedValue);
            if (selectedComprador) {
              dataToSend.comp_id = selectedComprador.id_comprador;
              dataToSend.codigo_comprador = selectedComprador.codigo_comprador;
              dataToSend.nombre_comprador = selectedComprador.nombre_comprador;
            }

          } else if (columnName === 'nombreProducto' || columnName === 'codigoProducto') {
            const selectedProducto = productArray.find(prod => prod.nombre_producto === editedValue || prod.codigo_producto === editedValue);
            if (selectedProducto) {
              dataToSend.prod_id = selectedProducto.id_producto;
              dataToSend.nombre_producto = selectedProducto.nombre_producto;
              dataToSend.codigo_producto = selectedProducto.codigo_producto;
            }

          } else if (columnName === 'nombreDestino' || columnName === 'codigoDestino') {
            const selectedDestino = destinos.find(dest => dest.nombre_destino === editedValue || dest.codigo_destino === editedValue);
            if (selectedDestino) {
              dataToSend.id_destino = selectedDestino.id_destino;
              dataToSend.nombre_destino = selectedDestino.nombre_destino;
              dataToSend.codigo_destino = selectedDestino.codigo_destino;
            }
          } else if (columnName === 'nombrePatio') {
            selectedPatioId = patios.find(pat => pat.nombre_patio === editedValue)?.id_patio;
            dataToSend.id_patio = selectedPatioId;

          } else if (columnName === 'numero_factura') {
            selectedFacturaId = facturas.find(fac => fac.numero_factura === editedValue)?.id_factura;
            dataToSend.id_factura = selectedFacturaId;
          } else if (columnName === 'nombreOrigen') {
            selectedOrigenId = origenes.find(ori => ori.nombre_origen === editedValue)?.id_origen;
            dataToSend.id_origen = selectedOrigenId;
          } else if (columnName === 'nombreTransportadora') {
            selectedTransportadoraId = transportadoras.find(trans => trans.nombre_transportadora === editedValue)?.id_transportadora;
            dataToSend.trasn_id = selectedTransportadoraId;
          } else if (columnName === 'ordenTransportadora') {
            dataToSend.orden = editedValue;
          } else if (columnName === 'precintoTransportadora') {
            dataToSend.precinto = editedValue;
          } else if (columnName === 'cantidad') {
            dataToSend.cantidad = editedValue;

          } else if (columnName === 'fEntrada') {
            dataToSend.fecha_entrada = editedValue;

          } else if (columnName === 'hEntrada') {
            dataToSend.hora_entrada = editedValue;

          } else if (columnName === 'fSalida') {
            dataToSend.fecha_salida = editedValue;

          } else if (columnName === 'hSalida') {
            dataToSend.hora_salida = editedValue;
          } else if (columnName === 'placa') {
            const selectedVehiculo = vehiculos.find(vehiculo => vehiculo.placa === editedValue);
            if (selectedVehiculo) {
              dataToSend.vehi_id = selectedVehiculo.id_vehiculo;
            }
          } else if (columnName === 'trailer') {
            const selectedTrailer = trailers.find(trailer => trailer.trailer === editedValue);
            if (selectedTrailer) {
              dataToSend.trai_id = selectedTrailer.id_trailer;
            }


          } else if (columnName === 'conductor') {
            const selectedConductor = conductores.find(conductor => conductor.nombre_conductor === editedValue);
            if (selectedConductor) {
              dataToSend.conduct_id = selectedConductor.id_conductor;

            }
          } else if (columnName === 'observaciones') {
            dataToSend.observaciones = editedValue
          }


          endpoint = `http://localhost:5000/actualizar_tiquete/${entity.tiquete}`;
        }

        if (endpoint) {
          await axios.put(endpoint, dataToSend);
          setNotification({ message: 'Registro actualizado con éxito', type: 'success' });
        } else {
          throw new Error('Tipo de formulario no soportado');
        }
      } catch (error) {
        console.error('Error guardando los cambios:', error); // Log del error completo
        setNotification({ message: `Error guardando los cambios: ${error.message}`, type: 'error' });
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleEditCellBlur();
    } else if (e.key === 'Tab') {
      e.preventDefault();
      handleEditCellBlur();
      navigateToNextCell();
    }
  };

  const handleNewRowKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSaveNewRow();
    }
  };

  const navigateToNextCell = () => {
    if (editingCell) {
      const { rowIndex, columnName } = editingCell;
      const currentColumnIndex = columns.findIndex(column => column.name === columnName);
      let nextColumnIndex = currentColumnIndex + 1;
      let nextRowIndex = rowIndex;

      if (nextColumnIndex >= columns.length) {
        nextColumnIndex = 0;
        nextRowIndex = rowIndex + 1;
      }

      if (nextRowIndex < tableData.length) {
        const nextColumnName = columns[nextColumnIndex].name;
        const nextValue = tableData[nextRowIndex][nextColumnName];
        setEditingCell({ rowIndex: nextRowIndex, columnName: nextColumnName });
        setEditedValue(nextValue);
      } else if (isAddingNewRow && nextRowIndex === tableData.length) {
        const nextColumnName = columns[nextColumnIndex].name;
        const nextValue = newRow[nextColumnName] || "";
        setEditingCell({ rowIndex: nextRowIndex, columnName: nextColumnName });
        setEditedValue(nextValue);
      }
    }
  };

  const handleAddNewRow = () => {
    setIsAddingNewRow(true);
    setNewRow(columns.reduce((acc, column) => {
      acc[column.name] = "";
      return acc;
    }, {}));
  };

  const handleNewRowChange = (e, columnName) => {
    setNewRow({ ...newRow, [columnName]: e.target.value });
  };


  const handleSaveNewRow = async () => {
    let dataToSend;
    let url;

    if (formType === "Cliente" || formType === "Proveedor" || formType === "Tercero") {
      if (!newRow.codigo_entidad || !newRow.nombre_entidad) {
        setNotification({ message: 'El código y el nombre son requeridos', type: 'error' });
        return;
      }

      const tipoEntidadMap = { "Cliente": 1, "Proveedor": 2, "Tercero": 3 };

      dataToSend = {
        ent_codigo: newRow.codigo_entidad,
        ent_nombre: newRow.nombre_entidad,
        ent_nit: newRow.nit_entidad,
        ent_telefono: newRow.telefono_entidad,
        ent_direccion: newRow.direccion_entidad,
        ent_idtipoentidad: tipoEntidadMap[formType]
      };

      url = 'http://localhost:5000/crear_entidad';

    } else if (formType === "Producto" || formType === "Varios") {
      if (!newRow.codigo_producto || !newRow.nombre_producto) {
        setNotification({ message: 'El código y el nombre son requeridos', type: 'error' });
        return;
      }

      const tipoProductodMap = { "Producto": 1, "Varios": 2 };

      dataToSend = {
        prod_codigo: newRow.codigo_producto,
        prod_nombre: newRow.nombre_producto,
        prod_idtipoproducto: tipoProductodMap[formType],  // Asegúrate de que este mapeo es correcto
        prod_idunidadmedida: newRow.unidad_medida,
        prod_idprocesoprod: newRow.proceso_producto
      };
      url = 'http://localhost:5000/crear_producto';

    } else if (formType === "Conductor") {
      if (!newRow.nombre_conductor || !newRow.cedula_conductor) {
        setNotification({ message: 'El nombre y la cédula son requeridos', type: 'error' });
        return;
      }

      dataToSend = {
        conduct_nombre: newRow.nombre_conductor,
        conduct_cedula: newRow.cedula_conductor
      };
      url = 'http://localhost:5000/crear_conductor';
    } else if (formType === "Vehiculo") {

      dataToSend = {
        placa: newRow.placa,

      };
      url = 'http://localhost:5000/crear_vehiculo';

    } else if (formType === "Trailer") {

      dataToSend = {
        trailer: newRow.trailer,

      };
      url = 'http://localhost:5000/crear_trailer';

    } else if (formType === "Factura") {

      dataToSend = {
        numero_factura: newRow.numero_factura,

      };
      url = 'http://localhost:5000/crear_factura';

    } else if (formType === "Origen") {
      if (!newRow.nombre_origen || !newRow.codigo_origen) {
        setNotification({ message: 'El codigo y el nombre son requeridos', type: 'error' });
        return;
      }

      dataToSend = {
        codigo_origen: newRow.codigo_origen,
        nombre_origen: newRow.nombre_origen,

      };
      url = 'http://localhost:5000/crear_origen';
    } else if (formType === "Destino") {
      if (!newRow.nombre_destino || !newRow.codigo_destino) {
        setNotification({ message: 'El codigo y el nombre son requeridos', type: 'error' });
        return;
      }

      dataToSend = {
        codigo_destino: newRow.codigo_destino,
        nombre_destino: newRow.nombre_destino,

      };
      url = 'http://localhost:5000/crear_destino';

    } else if (formType === "Patio") {
      if (!newRow.nombre_patio || !newRow.codigo_patio) {
        setNotification({ message: 'El codigo y el nombre son requeridos', type: 'error' });
        return;
      }

      dataToSend = {
        codigo_patio: newRow.codigo_patio,
        nombre_patio: newRow.nombre_patio,

      };
      url = 'http://localhost:5000/crear_patio';

    } else if (formType === "Comprador") {
      if (!newRow.nombre_comprador || !newRow.codigo_comprador) {
        setNotification({ message: 'El codigo y el nombre son requeridos', type: 'error' });
        return;
      }

      dataToSend = {
        codigo_comprador: newRow.codigo_comprador,
        nombre_comprador: newRow.nombre_comprador,

      };
      url = 'http://localhost:5000/crear_comprador';
    } else if (formType === "Transportadora") {
      if (!newRow.nombre_transportadora || !newRow.codigo_transportadora) {
        setNotification({ message: 'El codigo y el nombre son requeridos', type: 'error' });
        return;
      }

      dataToSend = {
        codigo_transportadora: newRow.codigo_transportadora,
        nombre_transportadora: newRow.nombre_transportadora,
        ciudad_transportadora: newRow.ciudad_transportadora,
        nit_transportadora: newRow.nit_transportadora,
        telefono_transportadora: newRow.telefono_transportadora,
        direccion_transportadora: newRow.direccion_transportadora

      };
      url = 'http://localhost:5000/crear_transportadora';
    } else {
      setNotification({ message: 'Tipo de formulario no soportado', type: 'error' });
      return;
    }

    try {
      const response = await axios.post(url, dataToSend, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 201) {
        if (formType === "Cliente") {
          setClientes([...clientes, newRow]);
          setNotification({ message: 'Nuevo cliente guardado', type: 'success' });
        } else if (formType === "Proveedor") {
          setProveedores([...proveedores, newRow]);
          setNotification({ message: 'Nuevo proveedor guardado', type: 'success' });
        } else if (formType === "Tercero") {
          setTerceros([...terceros, newRow]);
          setNotification({ message: 'Nuevo tercero guardado', type: 'success' });
        } else if (formType === "Producto") {
          setProductos([...productos, newRow]);
          setNotification({ message: 'Nuevo producto guardado', type: 'success' });
        } else if (formType === "Varios") {
          setVarios([...varios, newRow]);
          setNotification({ message: 'Nuevo servicio guardado', type: 'success' });
        } else if (formType === "Conductor") {
          setConductores([...conductores, newRow]);
          setNotification({ message: 'Nuevo conductor guardado', type: 'success' });
        } else if (formType === "Origen") {
          setOrigenes([...origenes, newRow]);
          setNotification({ message: 'Nuevo origen guardado', type: 'success' });
        } else if (formType === "Patio") {
          setPatios([...patios, newRow]);
          setNotification({ message: 'Nuevo patio guardado', type: 'success' });
        } else if (formType === "Destino") {
          setDestinos([...destinos, newRow]);
          setNotification({ message: 'Nuevo destino guardado', type: 'success' });
        } else if (formType === "Transportadora") {
          setTransportadoras([...transportadoras, newRow]);
          setNotification({ message: 'Nueva transportadora guardada', type: 'success' });
        } else if (formType === "Comprador") {
          setCompradores([...compradores, newRow]);
          setNotification({ message: 'Nuevo comprador guardado', type: 'success' });
        } else if (formType === "Trailer") {
          setTrailers([...trailers, newRow]);
          setNotification({ message: 'Nuevo Trailer guardado', type: 'success' });
        } else if (formType === "Factura") {
          setTrailers([...facturas, newRow]);
          setNotification({ message: 'Nueva factura guardada', type: 'success' });
        } else if (formType === "Vehiculo") {
          const conductor = conductores.find(c => c.id_conductor === newRow.conductor);
          const newVehiculo = {
            ...newRow,
            nombre_conductor: conductor ? conductor.nombre_conductor : ''
          };
          setVehiculos([...vehiculos, newVehiculo]);
          setNotification({ message: 'Nuevo vehículo guardado', type: 'success' });
        }
        setNewRow({});
        setIsAddingNewRow(false);
      }
    } catch (error) {
      console.error('Error saving new row:', error);
      setNotification({ message: 'Error guardando el nuevo registro: ' + error.message, type: 'error' });
    }
  };

  const handleChangeEstado = async (rowIndex) => {
    try {
      const item = tableData[rowIndex];
      let newEstado, url, idField, estadoField, accionField;

      if (formType === "Producto" || formType === "Varios") {
        newEstado = item.estado_producto === 'Activo' ? 0 : 1;
        url = 'http://localhost:5000/cambiar_estado_producto';
        idField = 'id_producto';
        estadoField = 'estado_producto';
        accionField = 'accion';
      } else if (formType === "Cliente" || formType === "Proveedor" || formType === "Tercero") {
        newEstado = item.estado_entidad === 'Activo' ? 0 : 1;
        url = 'http://localhost:5000/cambiar_estado_entidad';
        idField = 'id_entidad';
        estadoField = 'estado_entidad';
        accionField = 'accion';
      } else if (formType === "Vehiculo") {
        url = 'http://localhost:5000/cambiar_estado_vehiculo';
        idField = 'id_vehiculo';
        estadoField = 'estado_vehiculo';
        accionField = 'accion';
      } else if (formType === 'Conductor') {
        url = 'http://localhost:5000/cambiar_estado_conductor';
        idField = 'id_conductor';
        estadoField = 'estado_conductor';
        accionField = 'accion';
      }

      await axios.put(url, { [idField]: item[idField] });

      const updatedData = [...tableData];
      updatedData[rowIndex] = {
        ...item,
        [estadoField]: newEstado === 1 ? 'Activo' : 'Inactivo',
        [accionField]: newEstado === 1 ? 'Inactivar' : 'Activar'
      };

      setTableData(updatedData);
      setNotification({ message: 'Estado cambiado con éxito', type: 'success' });
    } catch (error) {
      setNotification({ message: `Error cambiando el estado: ${error.message}`, type: 'error' });
    }
  };


  const handleContextMenu = (e, rowIndex) => {
    e.preventDefault();
    setContextMenu({ show: true, x: e.clientX, y: e.clientY, rowIndex });

    // Reset the context menu after 10 seconds
    setTimeout(() => {
      setContextMenu({ show: false, x: 0, y: 0, rowIndex: null });
    }, 10000);
  };

  const handleContextMenuAction = async (action) => {
    if (contextMenu.rowIndex !== null) {
      const row = tableData[contextMenu.rowIndex];

      // Safely access the 'accion' property
      const accion = row?.accion;
      if (accion) {
        await handleChangeEstado(contextMenu.rowIndex);
      }

      setContextMenu({ show: false, x: 0, y: 0, rowIndex: null });
    }
  };

  const renderHeader = () => (
    <thead className="sticky top-0">
      <tr>
        {columns.map((column) => (
          <th key={column.name} className="text-left py-2 px-2 border-b border-gray-200 bg-white whitespace-nowrap w-auto">
            {column.title}
          </th>
        ))}
        {isAddingNewRow && <th className="text-left py-2 px-2 border-b border-gray-200 bg-white"></th>}
      </tr>
    </thead>
  );

  const renderBody = () => (
    <tbody>
      {tableData.map((record, rowIndex) => (
        <tr
          key={rowIndex}
          className={rowIndex % 2 === 0 ? "bg-white" : "bg-gray-100"}
          //onDoubleClick={() => onDoubleClickRow && onDoubleClickRow(record)}
          onContextMenu={(e) => handleContextMenu(e, rowIndex)}
        >
          {columns.map((column) => (
            <td
              key={column.name}
              className="py-2 px-2 border-b whitespace-nowrap w-auto"

              onDoubleClick={() => {
                // Si la columna es no editable, abrir el formulario
                if (["tiquete", "registro", "tipo", "pesoNeto", "unidad", "conductor", "cedulaConductor"].includes(column.name)) {
                  onDoubleClickRow && onDoubleClickRow(record);
                } else {
                  // Si la columna es editable, activar la edición
                  handleDoubleClick(rowIndex, column.name, record[column.name]);
                }
              }}

            >
              {editingCell && editingCell.rowIndex === rowIndex && editingCell.columnName === column.name ? (

                // Restrict double-click for certain columns
                ["tiquete", "registro", "tipo", "pesoNeto", "unidad", "conductor", "cedulaConductor"].includes(column.name) ? (
                  record[column.name]
                ) : column.name === "conductor" && formType === "Vehiculo" && !isAddingNewRow ? (
                  record[column.name]
                ) : (
                  // Renderizar los campos editables para otros casos
                  column.name === "unidad_medida" ? (
                    <select
                      value={editedValue}
                      onChange={handleEditCellChange}
                      onBlur={handleEditCellBlur}
                      className="border border-gray-300 rounded p-2"
                      autoFocus
                    >
                      {unidadesMedida.map((unidad) => (
                        <option key={unidad.id_unidad} value={unidad.nombre_unidad}>
                          {unidad.nombre_unidad}
                        </option>
                      ))}
                    </select>
                  ) : column.name === "proceso_producto" ? (
                    <select
                      value={editedValue}
                      onChange={handleEditCellChange}
                      onBlur={handleEditCellBlur}
                      className="border border-gray-300 rounded p-2"
                      autoFocus
                    >
                      {procesosProducto.map((proceso) => (
                        <option key={proceso.id} value={proceso.nombre}>
                          {proceso.nombre}
                        </option>
                      ))}
                    </select>

                  ) : column.name === 'fEntrada' || column.name === 'fSalida' ? (
                    <input
                      type="date"
                      value={moment(editedValue).tz("America/Bogota").format("YYYY-MM-DD")}
                      onChange={(e) => setEditedValue(e.target.value)}
                      onBlur={handleEditCellBlur}
                      className="border border-gray-300 rounded"
                      autoFocus
                    />
                  ) : column.name === 'hEntrada' || column.name === 'hSalida' ? (
                    <input
                      type="time"
                      value={moment(editedValue, "HH:mm").tz("America/Bogota").format("HH:mm")}
                      onChange={(e) => setEditedValue(e.target.value)}
                      onBlur={handleEditCellBlur}
                      className="border border-gray-300 rounded"
                      autoFocus
                    />

                  ) : (column.name === "nombreEntidad" || column.name === "codigoEntidad") && formType === "Ingreso" ? (
                    <select
                      value={editedValue}
                      onChange={handleEditCellChange}
                      onBlur={handleEditCellBlur}
                      className="border border-gray-300 rounded p-2"
                      autoFocus
                    >
                      {proveedores.map((proveedor) => (
                        <option key={proveedor.id_entidad} value={column.name === "nombreEntidad" ? proveedor.nombre_entidad : proveedor.codigo_entidad}>
                          {column.name === "nombreEntidad" ? proveedor.nombre_entidad : proveedor.codigo_entidad}
                        </option>
                      ))}
                    </select>

                  ) : (column.name === "nombreEntidad" || column.name === "codigoEntidad") && formType === "Despacho" ? (
                    <select
                      value={editedValue}
                      onChange={handleEditCellChange}
                      onBlur={handleEditCellBlur}
                      className="border border-gray-300 rounded p-2"
                      autoFocus
                    >
                      {clientes.map((cliente) => (
                        <option key={cliente.id_entidad} value={column.name === "nombreEntidad" ? cliente.nombre_entidad : cliente.codigo_entidad}>
                          {column.name === "nombreEntidad" ? cliente.nombre_entidad : cliente.codigo_entidad}
                        </option>
                      ))}
                    </select>

                  ) : (column.name === "nombreEntidad" || column.name === "codigoEntidad") && formType === "Servicios" ? (
                    <select
                      value={editedValue}
                      onChange={handleEditCellChange}
                      onBlur={handleEditCellBlur}
                      className="border border-gray-300 rounded p-2"
                      autoFocus
                    >
                      {terceros.map((tercero) => (
                        <option key={tercero.id_entidad} value={column.name === "nombreEntidad" ? tercero.nombre_entidad : tercero.codigo_entidad}>
                          {column.name === "nombreEntidad" ? tercero.nombre_entidad : tercero.codigo_entidad}
                        </option>
                      ))}
                    </select>

                  ) : (column.name === "nombreComprador" || column.name === "codigoComprador") ? (
                    <select
                      value={editedValue}
                      onChange={handleEditCellChange}
                      onBlur={handleEditCellBlur}
                      className="border border-gray-300 rounded p-2"
                      autoFocus
                    >
                      {compradores.map((comprador) => (
                        <option key={comprador.id_entidad} value={column.name === "nombreComprador" ? comprador.nombre_comprador : comprador.codigo_comprador}>
                          {column.name === "nombreComprador" ? comprador.nombre_comprador : comprador.codigo_comprador}
                        </option>
                      ))}
                    </select>

                  ) : (column.name === "nombreProducto" || column.name === "codigoProducto") && formType === "Ingreso" ? (
                    <select
                      value={editedValue}
                      onChange={handleEditCellChange}
                      onBlur={handleEditCellBlur}
                      className="border border-gray-300 rounded p-2"
                      autoFocus
                    >
                      {[...productosEntrada, ...productosEntradaSalida].map((productoEntrada) => (
                        <option key={productoEntrada.id_producto} value={column.name === "nombreProducto" ? productoEntrada.nombre_producto : productoEntrada.codigo_producto}>
                          {column.name === "nombreProducto" ? productoEntrada.nombre_producto : productoEntrada.codigo_producto}
                        </option>
                      ))}
                    </select>
                  ) : (column.name === "nombreProducto" || column.name === "codigoProducto") && formType === "Despacho" ? (
                    <select
                      value={editedValue}
                      onChange={handleEditCellChange}
                      onBlur={handleEditCellBlur}
                      className="border border-gray-300 rounded p-2"
                      autoFocus
                    >
                      {[...productosSalida, ...productosEntradaSalida].map((productoSalida) => (
                        <option key={productoSalida.id_producto} value={column.name === "nombreProducto" ? productoSalida.nombre_producto : productoSalida.codigo_producto}>
                          {column.name === "nombreProducto" ? productoSalida.nombre_producto : productoSalida.codigo_producto}
                        </option>
                      ))}
                    </select>
                  ) : (column.name === "nombreProducto" || column.name === "codigoProducto") && formType === "Servicios" ? (
                    <select
                      value={editedValue}
                      onChange={handleEditCellChange}
                      onBlur={handleEditCellBlur}
                      className="border border-gray-300 rounded p-2"
                      autoFocus
                    >
                      {varios.map((vario) => (
                        <option key={vario.id_producto} value={column.name === "nombreProducto" ? vario.nombre_producto : vario.codigo_producto}>
                          {column.name === "nombreProducto" ? vario.nombre_producto : vario.codigo_producto}
                        </option>
                      ))}
                    </select>
                  )
                    : column.name === "nombrePatio" ? (
                      <select
                        value={editedValue}
                        onChange={handleEditCellChange}
                        onBlur={handleEditCellBlur}
                        className="border border-gray-300 rounded p-2"
                        autoFocus
                      >
                        {patios.map((patio) => (
                          <option key={patio.id_patio} value={patio.nombre_patio}>
                            {patio.nombre_patio}
                          </option>
                        ))}
                      </select>

                    ) : column.name === "nombreOrigen" ? (
                      <select
                        value={editedValue}
                        onChange={handleEditCellChange}
                        onBlur={handleEditCellBlur}
                        className="border border-gray-300 rounded p-2"
                        autoFocus
                      >
                        {origenes.map((origen) => (
                          <option key={origen.id_origen} value={origen.nombre_origen}>
                            {origen.nombre_origen}
                          </option>
                        ))}
                      </select>

                    ) : (column.name === "nombreDestino" || column.name === "codigoDestino") ? (
                      <select
                        value={editedValue}
                        onChange={handleEditCellChange}
                        onBlur={handleEditCellBlur}
                        className="border border-gray-300 rounded p-2"
                        autoFocus
                      >
                        {destinos.map((destino) => (
                          <option key={destino.id_destino} value={column.name === "nombreDestino" ? destino.nombre_destino : destino.codigo_destino}>
                            {column.name === "nombreDestino" ? destino.nombre_destino : destino.codigo_destino}
                          </option>
                        ))}
                      </select>


                    ) : column.name === "numero_factura" ? (
                      formType === "Factura" ? (
                        <input
                          type="text"
                          value={editedValue}
                          onChange={handleEditCellChange}
                          onBlur={handleEditCellBlur}
                          className="border border-gray-300 rounded p-2"
                          autoFocus
                        />
                      ) : (
                        <select
                          value={editedValue}
                          onChange={handleEditCellChange}
                          onBlur={handleEditCellBlur}
                          className="border border-gray-300 rounded p-2"
                          autoFocus
                        >
                          {facturas.map((factura) => (
                            <option key={factura.id_factura} value={factura.numero_factura}>
                              {factura.numero_factura}
                            </option>
                          ))}
                        </select>
                      )


                    ) : column.name === "nombreTransportadora" ? (
                      <select
                        value={editedValue}
                        onChange={handleEditCellChange}
                        onBlur={handleEditCellBlur}
                        className="border border-gray-300 rounded p-2"
                        autoFocus
                      >
                        {transportadoras.map((transportadora) => (
                          <option key={transportadora.id_transportadora} value={transportadora.nombre_transportadora}>
                            {transportadora.nombre_transportadora}
                          </option>
                        ))}
                      </select>

                      //Cambios

                    ) : column.name === "conductor" ? (
                      <select
                        value={editedValue}
                        onChange={handleEditCellChange}
                        onBlur={handleEditCellBlur}
                        className="border border-gray-300 rounded p-2"
                        autoFocus
                      >
                        {conductores.map((conductor) => (
                          <option key={conductor.id_conductor} value={conductor.nombre_conductor}>
                            {conductor.nombre_conductor}
                          </option>
                        ))}
                      </select>

                      //trailer 

                    ) : column.name === "trailer" ? (
                      formType === "Trailer" ? (
                        <input
                          type="text"
                          value={editedValue}
                          onChange={handleEditCellChange}
                          onBlur={handleEditCellBlur}
                          className="border border-gray-300 rounded p-2"
                          autoFocus
                        />
                      ) : (
                        <select
                          value={editedValue}
                          onChange={handleEditCellChange}
                          onBlur={handleEditCellBlur}
                          className="border border-gray-300 rounded p-2"
                          autoFocus
                        >
                          {trailers.map((trailer) => (
                            <option key={trailer.id_trailer} value={trailer.trailer}>
                              {trailer.trailer}
                            </option>
                          ))}
                        </select>
                      )

                    ) : column.name === "placa" && (formType === 'Ingreso' || formType === 'Despacho' || formType === 'Servicios') ? (
                      <select
                        value={editedValue}
                        onChange={handleEditCellChange}
                        onBlur={handleEditCellBlur}
                        className="border border-gray-300 rounded p-2"
                        autoFocus
                      >
                        {vehiculos.map((vehiculo) => (
                          <option key={vehiculo.id_vehiculo} value={vehiculo.placa}>
                            {vehiculo.placa}
                          </option>
                        ))}
                      </select>

                    ) : (
                      <input
                        type="text"
                        value={editedValue}
                        onChange={handleEditCellChange}
                        onBlur={handleEditCellBlur}
                        onKeyDown={handleKeyDown}
                        className="border border-gray-300 rounded"
                        autoFocus
                      />
                    )
                )

              ) : (
                typeof record[column.name] === "object" && record[column.name] !== null
                  ? record[column.name].label
                  : record[column.name]
              )}
            </td>
          ))}
          {isAddingNewRow && rowIndex === tableData.length && (
            <td className="py-2 px-2 border-b">
              <button onClick={handleSaveNewRow} className="text-green-500">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
              </button>
            </td>
          )}
        </tr>
      ))}
      {isAddingNewRow && (
        <tr>
          {columns.map((column) => (
            <td key={column.name} className="py-2 px-2 border-b">
              {column.name === "unidad_medida" ? (
                <select
                  value={newRow[column.name] || ""}
                  onChange={(e) => handleNewRowChange(e, column.name)}
                  className="w-full border border-gray-300 rounded p-2 text-xs"
                >
                  <option value="">Seleccione una unidad</option>
                  {unidadesMedida.map((unidad) => (
                    <option key={unidad.id_unidad} value={unidad.id_unidad}>
                      {unidad.nombre_unidad}
                    </option>
                  ))}
                </select>
              ) : column.name === "proceso_producto" ? (
                <select
                  value={newRow[column.name] || ""}
                  onChange={(e) => handleNewRowChange(e, column.name)}
                  className="w-full border border-gray-300 rounded p-2 text-xs"
                >
                  <option value="">Seleccione un proceso</option>
                  {procesosProducto.map((proceso) => (
                    <option key={proceso.id} value={proceso.id}>
                      {proceso.nombre}
                    </option>
                  ))}
                </select>
              ) : column.name === "conductor" ? (
                <SelectField
                  options={conductores.map((conductor) => ({
                    value: conductor.id_conductor,
                    label: conductor.nombre_conductor,
                  }))}
                  value={newRow[column.name] || ""}
                  onChange={(selectedOption) => handleNewRowChange({ target: { value: selectedOption.value } }, column.name)}
                  isSearchable={true}
                  className="w-full border border-gray-300 rounded p-2 text-xs"
                />
              ) : (
                <input
                  type="text"
                  placeholder={column.title}
                  value={newRow[column.name] || ""}
                  onChange={(e) => handleNewRowChange(e, column.name)}
                  className="w-full border border-gray-300 rounded p-2 text-xs"
                />
              )}
            </td>
          ))}
          <td colSpan={columns.length} className="py-2 px-2 border-b text-center">
            <button onClick={handleSaveNewRow} className="text-green-500">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
            </button>
          </td>
        </tr>
      )}
      {showAddButton && !isAddingNewRow && (
        <tr>
          <td colSpan={columns.length + (isAddingNewRow ? 1 : 0)} className="py-2 px-2 border-b text-center">
            <button onClick={handleAddNewRow} className="text-blue-500">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
              </svg>
              Agregar nuevo registro
            </button>
          </td>
        </tr>
      )}
    </tbody>
  );


  return (
    <div>
      {notification.message && (
        <Notification
          message={notification.message}
          type={notification.type}
          onConfirm={notification.onConfirm}
          onCancel={notification.onCancel}
        />
      )}
      {contextMenu.show && (
        <div
          className="absolute bg-white border border-gray-200 rounded shadow-lg"
          style={{ top: contextMenu.y, left: contextMenu.x }}
        >
          <button
            onClick={() => handleContextMenuAction('changeState')}
            className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            {tableData[contextMenu.rowIndex]?.accion || "No Action"}  {/* Safely access 'accion' */}
          </button>
        </div>
      )}
      <table className="min-w-full border-collapse">
        {renderHeader()}
        {renderBody()}
      </table>
    </div>
  );
};

export default Table;

