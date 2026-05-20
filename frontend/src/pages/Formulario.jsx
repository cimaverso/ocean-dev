import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import TiqueteForm from "../components/TiqueteForm";
import Sidebar from "../components/Layouts/Sidebar";
import Header from "../components/Layouts/Header";

const Formulario = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const initialData = location.state ? location.state.record : {};
  const initialFormType = location.state ? location.state.formType : "";

  const [formType, setFormType] = useState(initialFormType);

  const handleFormTypeChange = (e) => {
    const newFormType = e.target.value;
    if (initialData && initialData.id) {
      if (window.confirm("¿Quieres cancelar la finalización del registro?")) {
        setFormType(newFormType);
      }
    } else {
      setFormType(newFormType); 
    }
  };

  return (
    <>
      <div className="font-montserrat bg-[#F2F2F2]">
        <div className="flex h-full">
          <Sidebar />
          <div className="flex flex-col flex-1 w-screen h-dvh overflow-auto">
            <Header />
            <div>
              
              {initialData.tiquete ? (
                <TiqueteForm initialData={initialData} formType="FINALIZAR_SERVICIOS" />
              ) : (
                <TiqueteForm formType={formType} initialData={initialData} />
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Formulario;
