import { Routes, Route } from "react-router-dom";

import Achievements from "../pages/admin/Achievements";
import DashBoard from "../pages/admin/DashBoard";
import Info from "../pages/admin/Info";
import Projects from "../pages/admin/Projects";
import RoleUser from "../pages/admin/RoleUser";
import SystemConfigs from "../pages/admin/SystemConfigs";
import Timelines from "../pages/admin/Timelines";

import AdminLayout from "../layout/AdminLayout";


const  AdminRoutes = () =>{
    return(
        <Routes>
            <Route element={<AdminLayout/>}>
                <Route index element={<DashBoard/>}/>
                <Route path="manage-info" element={<Info/>}/>
                <Route path="manage-timelines" element={<Timelines/>}/>
                <Route path="manage-projects" element={<Projects/>}/>
                <Route path="manage-achieves" element={<Achievements/>}/>
                <Route path="manage-roleuser" element={<RoleUser/>}/>
                <Route path="manage-config" element={<SystemConfigs/>}/>
            </Route>
        </Routes>
    )
}

export default AdminRoutes;