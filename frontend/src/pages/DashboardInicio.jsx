import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import { Link } from "react-router-dom";

const data = {
  ingresos: [
    { label: "Altos", value: "120.000 Tn", change: "10.26%" },
    { label: "Bajos", value: "236.000 Tn", change: "18.26%" },
    { label: "Medios", value: "236.000 Tn", change: "18.26%" },
  ],
  despachos: [
    { label: "Trafigura", value: "105.458 Tn", change: "25.26%" },
    { label: "Coquecol", value: "105.458 Tn", change: "5.26%" },
    { label: "Milpa", value: "105.458 Tn", change: "30.26%" },
  ],
};

function DashboardInicio() {
  return (
    <div className="h-dvh font-montserrat bg-[#F2F2F2]">
      <div className="flex">
        <Sidebar />
        <div className="flex flex-col flex-1 w-full">
          <Header />
          <div className="m-2 p-4">
            <div className="m-2 p-5 xl:max-2xl:h-96 text-ocean1">
              <h3 className="text-xl  font-bold ">INGRESOS</h3>
              <div className="grid grid-cols-3 gap-4 m-3">                
                {data.ingresos.map((item, index) => (
                  <div key={index} className="p-2 bg-[#6D80A6] h-42 xl:h-52  hover:drop-shadow-2xl rounded-lg">
                    <div className="w-11/12 h-3/4 xl:max-2xl:w-5/6 m-2 p-3 bg-[#F2F2F2] bg-opacity-25 border-l-3 border-ocean5 flex flex-col justify-center 	">
                    <h4 className="m-1 text-xl font-semibold xl:text-2xl">{item.label}</h4>
                    <p className="m-1 text-2xl font-bold xl:text-3xl">{item.value}</p>
                    </div>
                    <p className="m-1 ml-5 text-gray-950 font-medium xl:text-xl">{item.change}</p>
                  </div>
                  
                ))}                
              </div>
            </div>
            <div className="m-2 p-5 xl:max-2xl:h-96 text-ocean1">
              <h3 className="text-xl  font-bold ">DESPACHOS</h3>
              <div className="grid grid-cols-3 gap-4 m-3">                
                {data.despachos.map((item, index) => (
                  <div key={index} className="p-2 bg-[#6D80A6] h-42 xl:h-52 hover:drop-shadow-2xl rounded-lg">
                    <div className="w-11/12 h-3/4 xl:w-11/12 m-2 p-3 bg-[#F2F2F2] bg-opacity-25 border-l-3 border-ocean5 flex flex-col justify-center	">
                    <h4 className="m-1 text-xl font-semibold xl:text-2xl">{item.label}</h4>
                    <p className="m-1 text-2xl font-bold xl:text-3xl">{item.value}</p>
                    </div>
                    <p className="m-1 ml-5 text-gray-950 font-medium xl:text-xl">{item.change}</p>
                  </div>
                  
                ))}                
              </div>
            </div>
            <div className="m-4 p-2 flex justify-end text-ocean1 ">
              <button className="bg-white font-bold px-4 w-42 h-12 mt-10 hover:drop-shadow-2xl rounded "><Link to="./Formulario.jsx">
                CREAR INGRESO
              </Link></button>
            </div>
          </div>
        </div>
      </div>
    </div> 
  );
}

export default DashboardInicio;
