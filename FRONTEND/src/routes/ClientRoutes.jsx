import { Routes, Route } from "react-router-dom";

import Achievement from "../pages/client/Achievement";
import AboutMe from "../pages/client/AboutMe";
import Index from "../pages/client/Index";
import Project from "../pages/client/Project";
import Timeline from "../pages/client/Timeline";

const ClientRoutes = () =>{
    return(
        <Routes>
            <Route>
                <Route index element={<Index/>}/>
                <Route path="about-me" element={<AboutMe/>}/>
                <Route path="timeline" element={<Timeline/>}/>
                <Route path="project" element={<Project/>}/>
                <Route path="achievement" element={<Achievement/>}/>
            </Route>
        </Routes>
    )
};

export default ClientRoutes;