import { Routes, Route } from "react-router-dom";

import Achievement from "../pages/client/Achievement";
import AboutMe from "../pages/client/AboutMe";
import Index from "../pages/client/Index";
import Project from "../pages/client/Project";
import Timeline from "../pages/client/Timeline";

import { NotFound } from "../pages/client/NotFound";

import ClientLayout from "../layout/ClientLayout";

const ClientRoutes = () =>{
    return(
        <Routes>
            <Route element={<ClientLayout/>}>
                <Route index element={<Index/>}/>
                <Route path="about-me" element={<AboutMe/>}/>
                <Route path="timeline" element={<Timeline/>}/>
                <Route path="project" element={<Project/>}/>
                <Route path="achievement" element={<Achievement/>}/>
                <Route path= "*" element={<NotFound/>}/>
            </Route>
        </Routes>
    )
};

export default ClientRoutes;