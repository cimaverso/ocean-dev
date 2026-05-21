/**
 * SelectField.js
 * Proyecto Ocean — Sistema de pesaje
 *
 * Props:
 *   label       {string}    — Etiqueta del campo
 *   id          {string}    — ID del input (accesibilidad)
 *   options     {Array}     — [{ value, label }] — el padre es responsable del fetch
 *   value       {any}       — Valor seleccionado actual
 *   onChange    {Function}  — (selectedOption) => void
 *   isDisabled  {boolean}   — Deshabilitar el select
 *   isLoading   {boolean}   — Mostrar spinner de carga
 *   placeholder {string}    — Texto placeholder
 *   onAddNew    {Function}  — Opcional. Si se provee, muestra botón "+ Añadir"
 *                             Recibe (formData) => Promise<{ value, label }>
 *                             El componente agrega el nuevo ítem al select y lo selecciona
 *   addNewFields {Array}    — Opcional. [{ key, label }] campos del modal de añadir
 *                             Ej: [{ key: "nombre", label: "Nombre" }]
 *
 * ELIMINADO:
 *   apiEndpoint     — el padre fetcha y pasa options
 *   postApiEndpoint — reemplazado por onAddNew callback
 */

import React, { useState } from "react";
import Select from "react-select";
import "./SelectField.css";

const SelectField = ({
  label,
  id,
  options = [],
  value,
  onChange,
  isDisabled  = false,
  isLoading   = false,
  placeholder = "Seleccionar...",
  onAddNew    = null,
  addNewFields = [],
}) => {
  const [isModalOpen, setIsModalOpen]   = useState(false);
  const [formData, setFormData]         = useState({});
  const [isSaving, setIsSaving]         = useState(false);
  const [localOptions, setLocalOptions] = useState(options);

  // Sincronizar opciones externas cuando el padre las actualiza
  // Se usa key en el padre para forzar re-mount si cambian drásticamente,
  // pero también actualizamos localmente para el caso de añadir uno nuevo
  const mergedOptions = [
    ...options,
    // Incluir opciones añadidas localmente que no estén ya en options
    ...localOptions.filter(
      (lo) => !options.find((o) => o.value === lo.value)
    ),
  ];

  // Valor formateado para react-select
  const selectedOption =
    mergedOptions.find((o) => o.value === value) ?? null;

  // ── Handlers modal ──────────────────────────────────────────────────────
  const handleOpenModal = () => {
    setFormData(
      addNewFields.reduce((acc, f) => ({ ...acc, [f.key]: "" }), {})
    );
    setIsModalOpen(true);
  };

  const handleFieldChange = (key, val) => {
    setFormData((prev) => ({ ...prev, [key]: val }));
  };

  const handleSave = async () => {
    if (!onAddNew) return;
    setIsSaving(true);
    try {
      const newOption = await onAddNew(formData); // { value, label }
      if (newOption) {
        setLocalOptions((prev) => [...prev, newOption]);
        onChange(newOption);
      }
      setIsModalOpen(false);
    } catch (err) {
      console.error("Error al guardar nuevo ítem:", err);
    } finally {
      setIsSaving(false);
    }
  };

  // ── Componente de mensaje sin opciones (con botón añadir) ───────────────
  const NoOptionsMessage = () => (
    <div className="select-field__menu-footer">
      <span>Sin resultados</span>
      {onAddNew && (
        <button
          className="select-field__add-btn"
          onMouseDown={(e) => {
            e.preventDefault(); // Evita que el select se cierre
            handleOpenModal();
          }}
        >
          <i className="bi bi-plus-lg" aria-hidden="true" />
          Añadir
        </button>
      )}
    </div>
  );

  // ── Componente de pie del menú (siempre visible si onAddNew existe) ─────
  const MenuFooter = ({ innerProps }) => (
    onAddNew ? (
      <div className="select-field__menu-footer" {...innerProps}>
        <span />
        <button
          className="select-field__add-btn"
          onMouseDown={(e) => {
            e.preventDefault();
            handleOpenModal();
          }}
        >
          <i className="bi bi-plus-lg" aria-hidden="true" />
          Añadir nuevo
        </button>
      </div>
    ) : null
  );

  return (
    <>
      <div className="select-field">
        {label && (
          <label className="select-field__label" htmlFor={id}>
            {label}
          </label>
        )}

        <div className="select-field__control-wrapper">
          <Select
            inputId={id}
            value={selectedOption}
            onChange={onChange}
            options={mergedOptions}
            isDisabled={isDisabled}
            isLoading={isLoading}
            placeholder={placeholder}
            classNamePrefix="rsel"
            noOptionsMessage={() => <NoOptionsMessage />}
            components={onAddNew ? { MenuList: MenuListWithFooter(MenuFooter) } : undefined}
            menuPosition="fixed"
            menuPortalTarget={document.body}
            styles={{
              menuPortal: (base) => ({ ...base, zIndex: 9999 }),
            }}
          />
        </div>
      </div>

      {/* ── Modal añadir nuevo ── */}
      {isModalOpen && (
        <div
          className="select-field__modal-overlay"
          onClick={(e) => {
            if (e.target === e.currentTarget) setIsModalOpen(false);
          }}
          role="dialog"
          aria-modal="true"
          aria-labelledby={`modal-title-${id}`}
        >
          <div className="select-field__modal">
            <h3
              className="select-field__modal-title"
              id={`modal-title-${id}`}
            >
              Añadir {label}
            </h3>

            {addNewFields.map(({ key, label: fieldLabel, type = "text" }) => (
              <div key={key} className="select-field__modal-field">
                <label htmlFor={`modal-field-${key}`}>{fieldLabel}</label>
                <input
                  id={`modal-field-${key}`}
                  type={type}
                  value={formData[key] || ""}
                  onChange={(e) => handleFieldChange(key, e.target.value)}
                  placeholder={`Ingrese ${fieldLabel.toLowerCase()}`}
                  autoComplete="off"
                />
              </div>
            ))}

            <div className="select-field__modal-actions">
              <button
                className="select-field__modal-cancel"
                onClick={() => setIsModalOpen(false)}
                disabled={isSaving}
              >
                Cancelar
              </button>
              <button
                className="select-field__modal-save"
                onClick={handleSave}
                disabled={isSaving}
              >
                {isSaving ? "Guardando..." : "Guardar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

// ── HOC: envuelve MenuList de react-select para inyectar footer ─────────────
const MenuListWithFooter = (Footer) => {
  const MenuList = ({ children, ...props }) => (
    <div>
      <div>{children}</div>
      <Footer />
    </div>
  );
  MenuList.displayName = "MenuListWithFooter";
  return MenuList;
};

export default SelectField;