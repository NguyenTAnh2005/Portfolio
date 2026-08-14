import {Navigate, Outlet} from 'react-router-dom';
import { useSystemConfig } from '../contexts/SystemConfigContext';
import { Maintenance } from '../pages/Maintenance';

export default function ProtectedConfig(){
    const {isMaintenance} = useSystemConfig();
    if (isMaintenance){
        return <Maintenance/>
    }
    return(
        <Outlet/>
    )
}