import { BrowserRouter, Routes, Route } from "react-router-dom";
import ClientRoutes from "./ClientRoutes";
import AdminRoutes from "./AdminRoutes";
import Login from "../pages/Login";
import ProtectedRoute from "./ProtectedRoutes";
import { AuthProvider } from "../contexts/AuthContext";
import {ToastContainer} from 'react-toastify';

import 'react-toastify/dist/ReactToastify.css'; // Import CSS của thư viện Toastify

const  AppRoutes= () =>{
    return(
        <AuthProvider>
            <BrowserRouter>

            <ToastContainer theme="colored" position="top-right" autoClose={2500}/>
            
                <Routes>
                    {/* ================================================== */}
                    {/* TRANG ĐỘC LẬP: Không Navbar, Không Sidebar         */}
                    {/* ================================================== */}
                    <Route path="log-in" element={<Login/>}/>

                    {/* ================================================== */}
                    {/* TRANG CHO CLIENT (HEADER, FOOTER, CÁC NỘI DUNG....)*/}
                    {/* ================================================== */}
                    <Route path="/*" element={<ClientRoutes/>}/>

                    {/* ================================================== */}
                    {/* TRANG CHO ADMIN QUẢN LÝ                            */}
                    {/* ================================================== */}
                    <Route element={<ProtectedRoute/>}>
                        <Route path="/admin/*" element={<AdminRoutes/>}/>
                    </Route>

                </Routes>
            </BrowserRouter>
        </AuthProvider>
    )
};
export default AppRoutes;
