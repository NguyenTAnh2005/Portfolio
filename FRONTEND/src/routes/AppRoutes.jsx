import { BrowserRouter, Routes, Route } from "react-router-dom";
import ClientRoutes from "./ClientRoutes";
import AdminRoutes from "./AdminRoutes";
import Login from "../pages/Login";
import ProtectedAuth from "./ProtectedAuth";
import ProtectedConfig from "./ProtectedConfig";
import { AuthProvider } from "../contexts/AuthContext";
import { SystemConfigProvider } from "../contexts/SystemConfigContext";
import {ToastContainer} from 'react-toastify';

import 'react-toastify/dist/ReactToastify.css'; // Import CSS của thư viện Toastify

const  AppRoutes= () =>{
    return(
        <BrowserRouter>
            <ToastContainer theme="colored" position="top-right" autoClose={2500}/>
            <Routes>
                {/* ================================================== */}
                {/* TRANG ĐỘC LẬP: Không Navbar, Không Sidebar         */}
                {/* ================================================== */}
                <Route path="/log-in" element={
                        <AuthProvider>
                            <Login/>
                        </AuthProvider>
                    }/>

                {/* ================================================== */}
                {/* TRANG CHO CLIENT (HEADER, FOOTER, CÁC NỘI DUNG....)*/}
                {/* ================================================== */}
                <Route element={
                    <SystemConfigProvider>
                        <ProtectedConfig/>
                    </SystemConfigProvider>
                }>
                    <Route path="/*" element={<ClientRoutes/>}/>
                </Route>
                {/* ================================================== */}
                {/* TRANG CHO ADMIN QUẢN LÝ                            */}
                {/* ================================================== */}
                <Route element={
                    <AuthProvider>
                        <ProtectedAuth/>
                    </AuthProvider>
                }>
                    <Route path="/admin" element={<AdminRoutes/>}/>
                </Route>
            </Routes>
        </BrowserRouter>
    )
};
export default AppRoutes;
