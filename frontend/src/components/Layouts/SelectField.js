import { useState, useEffect } from "react";
import Select from "react-select";
import axios from "axios";

const SelectField = ({ 
  label, 
  id, 
  options = [], 
  value, 
  onChange, 
  isDisabled = false, 
  apiEndpoint, 
  postApiEndpoint 
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({});
  const [selectOptions, setSelectOptions] = useState(options);
  const [fields, setFields] = useState([]);

  useEffect(() => {
    axios.get(apiEndpoint)
      .then(response => {
        const apiOptions = response.data.map(item => ({
          value: item.id,
          label: item.nombre || item.placa || item.descripcion || item.cedula,
        }));
        setSelectOptions(apiOptions);
      })
      .catch(error => console.error("Error cargando opciones:", error));
  }, [apiEndpoint]);

  const formattedOptions = selectOptions.map((option) => ({
    value: option.value,
    label: option.label,
  }));

  const handleChange = (selectedOption) => {
    onChange(selectedOption);
  };

  const handleOpenModal = async () => {
    try {
      const response = await axios.get(`${apiEndpoint}/fields`);
      setFields(response.data);
      setFormData({});
      setIsModalOpen(true);
    } catch (error) {
      console.error("Error obteniendo los campos:", error);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleAddNew = async () => {
    try {
      const response = await axios.post(postApiEndpoint, formData); // 🔹 Aquí usamos la API para guardar
      const newOption = { value: response.data.id, label: response.data.nombre || response.data.placa };

      setSelectOptions([...selectOptions, newOption]); // Agregar nuevo dato al select
      setIsModalOpen(false); // Cerrar modal
      onChange(newOption); // Seleccionar el nuevo valor en el select
    } catch (error) {
      console.error("Error al guardar el nuevo dato:", error);
    }
  };

  return (
    <div className="mb-1 p-0 flex items-center w-full">
      {label && (
        <label className="text-xs 2xl:text-base w-1/4 font-bold m-1 block" htmlFor={id}>
          {label}
        </label>
      )}
      
      <div className="relative w-11/12">
        <Select
          id={id}
          value={formattedOptions.find(option => option.value === value)}
          onChange={handleChange}
          options={formattedOptions}
          className="text-xs 2xl:text-base text-[#182540] focus:outline-none focus:ring-2 focus:ring-blue-300"
          isDisabled={isDisabled}
          noOptionsMessage={() => (
            <div className="flex items-center justify-between px-2">
              <span>No hay opciones</span>
              <button 
                className="text-blue-500 hover:text-blue-700 text-sm font-semibold ml-2"
                onClick={handleOpenModal}
              >
                + Añadir
              </button>
            </div>
          )}
        />
      </div>

      {/* MODAL PARA AÑADIR NUEVO DATO */}
      {isModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white p-5 rounded-lg shadow-md max-w-sm w-full">
            <h2 className="text-lg font-bold mb-3">Añadir Nuevo {label}</h2>
            
            {fields.map((field) => (
              <div key={field} className="mb-3">
                <label className="block text-sm font-semibold">{field}</label>
                <input
                  type="text"
                  className="border rounded p-2 w-full"
                  placeholder={`Ingrese ${field}`}
                  value={formData[field] || ""}
                  onChange={(e) => handleInputChange(field, e.target.value)}
                />
              </div>
            ))}

            <div className="flex justify-end space-x-2">
              <button className="bg-gray-300 px-3 py-1 rounded" onClick={() => setIsModalOpen(false)}>Cancelar</button>
              <button className="bg-blue-500 text-white px-3 py-1 rounded" onClick={handleAddNew}>Guardar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SelectField;





