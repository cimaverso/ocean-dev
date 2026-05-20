import { useEffect, useState } from "react";
import axios from "axios";

const Table = ({ columns, data, editable, onEdit, isConsultasPage }) => {
  const [tableData, setTableData] = useState([]);
  const [editingCell, setEditingCell] = useState(null); // { rowIndex, columnName }
  const [editedValue, setEditedValue] = useState("");
  const [newRow, setNewRow] = useState({});
  const [isAddingNewRow, setIsAddingNewRow] = useState(false);

  useEffect(() => {
    if (typeof data === "function") {
      try {
        const result = data();
        setTableData(result);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    } else {
      setTableData(data);
    }
  }, [data]);

  const handleEditCellChange = (e) => {
    setEditedValue(e.target.value);
  };

  const handleEditCellBlur = async () => {
    if (editingCell) {
      const { rowIndex, columnName } = editingCell;
      const updatedData = [...tableData];
      updatedData[rowIndex][columnName] = editedValue;
      setTableData(updatedData);
      setEditingCell(null);

      try {
        await axios.post('/api/update', { rowIndex, columnName, value: editedValue });
        console.log('Datos guardados');
      } catch (error) {
        console.error('Error guardando los datos:', error);
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleEditCellBlur();
    }
  };

  const handleAddNewRow = () => {
    if (isConsultasPage) { // Solo permite agregar nueva fila si estamos en la página de Consultas
      setIsAddingNewRow(true);
      setNewRow(columns.reduce((acc, column) => {
        acc[column.name] = "";
        return acc;
      }, {}));
    }
  };

  const handleNewRowChange = (e, columnName) => {
    setNewRow({ ...newRow, [columnName]: e.target.value });
  };

  const handleNewRowBlur = async () => {
    if (isAddingNewRow) {
      const updatedData = [...tableData, newRow];
      setTableData(updatedData);
      setIsAddingNewRow(false);
      setNewRow({});

      try {
        await axios.post('http://localhost:5000/data', newRow);
        console.log('Nuevo registro guardado');
      } catch (error) {
        console.error('Error guardando el nuevo registro:', error);
      }
    }
  };

  const handleNewRowKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleNewRowBlur();
    }
  };

  const renderHeader = () => (
    <thead>
      <tr>
        {columns.map((column) => (
          <th key={column.name} className="text-left py-2 px-4 border-b border-gray-200 bg-white">
            {column.title}
          </th>
        ))}
      </tr>
    </thead>
  );

  const renderBody = () => (
    <tbody>
      {tableData.map((record, rowIndex) => (
        <tr key={rowIndex} className={rowIndex % 2 === 0 ? "bg-white" : "bg-gray-100"}>
          {columns.map((column) => (
            <td key={column.name} className="py-2 px-2 border-b">
              {column.render ? column.render(record, onEdit) : (
                editingCell && editingCell.rowIndex === rowIndex && editingCell.columnName === column.name ? (
                  <input
                    type="text"
                    value={editedValue}
                    onChange={handleEditCellChange}
                    onBlur={handleEditCellBlur}
                    onKeyDown={handleKeyDown}
                    className="border border-gray-300 rounded"
                    autoFocus
                  />
                ) : (
                  record[column.name]
                )
              )}
            </td>
          ))}
        </tr>
      ))}
      {isAddingNewRow && (
        <tr className="bg-gray-200">
          {columns.map((column) => (
            <td key={column.name} className="py-2 px-2 border-b">
              <input
                type="text"
                value={newRow[column.name]}
                onChange={(e) => handleNewRowChange(e, column.name)}
                onBlur={handleNewRowBlur}
                onKeyDown={handleNewRowKeyDown}
                className="border border-gray-300 rounded"
                autoFocus
              />
            </td>
          ))}
        </tr>
      )}
      {isConsultasPage && (
        <tr>
          <td colSpan={columns.length} className="py-2 px-2 border-b text-center">
            <button onClick={handleAddNewRow} className="text-blue-500">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
      <table className="min-w-full bg-white">
        {renderHeader()}
        {renderBody()}
      </table>
    </div>
  );
};

export default Table;
