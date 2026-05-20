import React from "react";
import Table from "../Layouts/Tabla";

const columnsHistorial = [
  { name: "tipo", title: "Tipo" },
  { name: "tiquete", title: "Tiquete" },
  { name: "registro", title: "Registro" },
  { name: "placa", title: "Placa" },
  { name: "cedulaConductor", title: "Cedula Conductor" },
  { name: "conductor", title: "conductor" },
  { name: "trailer", title: "Trailer" },
  { name: "fEntrada", title: "F Entrada" },
  { name: "hEntrada", title: "Hora Entrada" },
  { name: "peso", title: "Peso" },
  { name: "fSalida", title: "Fecha Salida" },
  { name: "hSalida", title: "Hora Salida" },
  
];

const TablaHistorial = ({ data = [], onDoubleClickRow }) => (
  <Table
    columns={columnsHistorial}
    data={data}
    onDoubleClickRow={onDoubleClickRow}
    editable={false}
  />
);

export default TablaHistorial;
