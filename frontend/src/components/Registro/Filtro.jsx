import { useState, useEffect, useCallback, useMemo } from "react";
import axios from "axios";
 
const FilterSection = ({ setTableData, consultaTipo }) => {
  const [placa, setPlaca] = useState("");
  const [resultadosPorPagina, setResultadosPorPagina] = useState("elegir");
  const [handler, setHandler] = useState([]);
 
  // Función para obtener datos según el tipo de consulta
  const fetchData = useCallback(async () => {
    try {
      let result;
      if (consultaTipo === "transito") {
        const response = await axios.get('http://localhost:5000/obtener_registros');
        result = response.data;
      } else if (consultaTipo === "historial") {
        const response = await axios.get('http://localhost:5000/obtener_tiquetes_diarios');
        result = response.data;
      } else {
        throw new Error("Tipo de consulta no válido");
      }
      if (Array.isArray(result)) {
        setHandler(result);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  }, [consultaTipo]);
 
  useEffect(() => {
    fetchData();
  }, [fetchData]);
 
  // Filtrar todos los registros según la placa
  const allFilteredData = useMemo(() => {
    return handler.filter(item => placa === "" || item.placa.includes(placa));
  }, [handler, placa]);
 
  // Calcular la cantidad de cada tipo basado en los datos filtrados
  const counts = useMemo(() => {
    const ingresos = allFilteredData.filter(item => item.tipo === "ingreso").length;
    const despachos = allFilteredData.filter(item => item.tipo === "despacho").length;
    const servicios = allFilteredData.filter(item => item.tipo === "servicio").length;
    return { ingresos, despachos, servicios };
  }, [allFilteredData]);
 
  // Aplicar paginación a los datos filtrados
  const filteredData = useMemo(() => {
    if (resultadosPorPagina === "elegir") {
      return allFilteredData;
    } else {
      return allFilteredData.slice(0, Number(resultadosPorPagina));
    }
  }, [allFilteredData, resultadosPorPagina]);
 
  useEffect(() => {
    setTableData(filteredData);
  }, [filteredData, setTableData]);
 
  return (
    <div className="flex flex-col w-full p-2 bg-white rounded-lg shadow-md">
      <div className="flex justify-between content-center">
        <div className="flex p-1">
          {/* Sección del filtro por placa y los contadores */}
          <div className="flex flex-col p-1 justify-center">
            <label className="text-gray-600 text-sm xl:text-base mb-2">
              Placa
            </label>
            <input
              type="text"
              value={placa}
              onChange={(e) => setPlaca(e.target.value)}
              placeholder="Ingrese placa"
              className="px-1 py-1 text-xs xl:text-lg rounded-md border border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            
          </div>
          <div className="flex flex-col p-1 w-[30%] justify-end">
            <button
              onClick={() => setTableData(filteredData)}
              className="px-1 py-1 bg-blue-500 text-sm text-white rounded-md hover:bg-blue-600"
            >
              Buscar
            </button>
          </div>
          
        </div>

        {/* Mostrar contadores de cada tipo */}
        <div className="flex gap-2 mt-2 font-medium items-center">
              <span className="text-base text-gray-700 ">Ingresos: {counts.ingresos}</span>
              <span className="text-base text-gray-700">Despachos: {counts.despachos}</span>
              <span className="text-base text-gray-700">Servicios: {counts.servicios}</span>
            </div>
 
        <div className="flex justify-between items-center gap-4">
          <label className="text-gray-600 text-xs xl:text-base mb-2">
            Resultados por página
          </label>
          <select
            value={resultadosPorPagina}
            onChange={(e) => setResultadosPorPagina(e.target.value)}
            className="px-1 py-1 text-sm xl:text-lg rounded-md border border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="elegir">Elegir</option>
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={15}>15</option>
          </select>
        </div>
      </div>
    </div>
  );
};
 
export default FilterSection;
