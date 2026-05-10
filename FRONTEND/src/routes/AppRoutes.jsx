import { BrowserRouter, Routes, Route } from "react-router-dom";
import ClientRoutes from "./ClientRoutes";
import AdminRoutes from "./AdminRoutes";
import Login from "../pages/Login";

const  AppRoutes= () =>{
    return(
        <BrowserRouter>
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
                <Route path="/admin/*" element={<AdminRoutes/>}/>

            </Routes>
        </BrowserRouter>
    )
};
export default AppRoutes;
