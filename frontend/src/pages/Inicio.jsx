import Sidebar from "../components/Layouts/Sidebar";
import Header from "../components/Layouts/Header";
import { Link } from "react-router-dom";
import axios from 'axios';
import React, { useEffect, useState } from 'react';
import Notification from '../components/Layouts/Notificacion';
import TarjetaInicio from "../components/Layouts/TarjetaInicio";

function Inicio() {
  const [errorMessage, setErrorMessage] = useState("");
  const [data, setData] = useState({
    ingresos: [],
    despachos: []
  });

  useEffect(() => {
    // Llamada a la API para "despachos"
    axios.get('http://localhost:5000/despachos')
      .then((response) => {
        const { resultados } = response.data;

        const formattedDespachos = Object.keys(resultados).map((destino) => ({
          label: destino,
          value: `${resultados[destino].peso_neto} Kg`,
          change: `${resultados[destino].porcentaje}%`
        }));

        setData(prevData => ({
          ...prevData,
          despachos: formattedDespachos,
        }));
      })
      .catch((error) => {
        setErrorMessage('Error al obtener los datos de despachos:', error);
      });

    // Llamada a la API para "ingresos"
    axios.get('http://localhost:5000/ingresos')
      .then((response) => {
        const { resultados } = response.data;

        const formattedIngresos = Object.keys(resultados).map((producto) => ({
          label: producto,
          value: `${resultados[producto].peso_neto} Kg`
        }));

        setData(prevData => ({
          ...prevData,
          ingresos: formattedIngresos,
        }));
      })
      .catch((error) => {
        setErrorMessage('Error al obtener los datos de ingresos:', error);
      });
  }, []);

  // Filtrar datos para mostrar solo aquellos con valores mayores a 0
  const filteredIngresos = data.ingresos.filter(
    (item) => parseFloat(item.value) > 0
  );

  const filteredDespachos = data.despachos.filter(
    (item) => parseFloat(item.value) > 0
  );

  return (
    <div className="h-screen w-screen font-montserrat bg-[#F2F2F2]">
      <Notification message={errorMessage} type="error" />
      <div className="flex h-full">
        <Sidebar />
        <div className="flex flex-col flex-1 w-screen h-dvh overflow-auto">
          <Header />
          <div className="m-2 p-4 content-center">
            {/* Sección de Ingresos */}
            <div className="m-2 p-5">
              <h2 className="text-2xl font-bold mb-4">INGRESOS</h2>
              <div className="m-2 p-2 flex flex-nowrap overflow-auto">
                <div className="flex flex-row gap-6">
                  {filteredIngresos.map((item, index) => (
                    <TarjetaInicio key={index} label={item.label} value={item.value} />
                  ))}
                </div>
              </div>
            </div>

            {/* Sección de Despachos */}
            <div className="m-2 p-5">
              <h2 className="text-2xl font-bold mb-4">DESPACHOS</h2>
              <div className="m-2 p-2 flex flex-nowrap overflow-auto">
                <div className="flex flex-row gap-6">
                  {filteredDespachos.map((item, index) => (
                    <TarjetaInicio key={index} label={item.label} value={item.value} />
                  ))}
                </div>
              </div>
            </div>

            {/* Botón de Crear Ingreso */}
            <div className="m-2 p-2 flex justify-end text-ocean1">
              <Link to="/formulario">
                <button className="bg-white font-bold px-2 w-42 h-12 mt-5 hover:drop-shadow-2xl hover:bg-[#6D80A6] hover:text-[#f2f2f2] rounded">
                  CREAR INGRESO
                </button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Inicio;
