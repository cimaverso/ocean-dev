import React from "react";
import Table from "../Layouts/Tabla";

const columnsTransito = [
  { name: "tipo", title: "Tipo" },
  { name: "registro", title: "Registro" },
  

  { name: "placa", title: "Placa" },
  { name: "cedulaConductor", title: "Cedula Conductor" },
  { name: "conductor", title: "Conductor" },
  { name: "trailer", title: "Trailer" },
  { name: "fEntrada", title: "Fecha Entrada" },
  { name: "hEntrada", title: "Hora Entrada" },
  { name: "peso", title: "Peso" },
];

const TablaTransito = ({ data = [], onDoubleClickRow }) => (
  <Table
    columns={columnsTransito}
    data={data}
    editable={false}
    onDoubleClickRow={onDoubleClickRow}
  />
);

export default TablaTransito;
