/**
 * Formulario.jsx
 * Proyecto Ocean — Sistema de pesaje
 *
 * Página contenedora de TiqueteForm.
 * Recibe estado desde navigate() en Registro.jsx o acceso directo.
 */

import React from "react";
import { useLocation } from "react-router-dom";
import Sidebar     from "../components/Layouts/Sidebar";
import Header      from "../components/Layouts/Header";
import TiqueteForm from "../components/TiqueteForm";
import "./Formulario.css";

const Formulario = () => {
  const location      = useLocation();
  const initialData   = location.state?.record   || {};
  const initialFormType = location.state?.formType || "";

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <Header />
        <div className="formulario-content">
          <TiqueteForm
            formType={initialFormType}
            initialData={initialData}
          />
        </div>
      </div>
    </div>
  );
};

export default Formulario;