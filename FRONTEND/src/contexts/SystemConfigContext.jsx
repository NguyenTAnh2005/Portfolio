
//  1 provider  chứa fetch 3 biến từ backend bỏ về 3 useState
// Gom các giá trị bỏ vào 1 biến value
// Trả về 1 provider có value = value

import { createContext, useContext, useState, useEffect } from "react";
import { systemConfigService } from "../services/systemConfig";
import { StatusLoading, StatusError, StatusNoData } from "../components/FetchStatus";

const SystemConfigContext = createContext();

export const SystemConfigProvider = ({children}) =>{
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [queryParam, setQueryparam] = useState({
        skip: 0,
        limit: 30
    });

    useEffect(()=>{
        let isMounted = true;
        const fetchData = async () =>{
            if (isMounted){
                try {
                    const response = await systemConfigService.getAll(queryParam);
                    setData(response);
                } catch (err) {
                    console.error("Lỗi: ", err.message);
                    setError(err.message);

                }
                finally{
                    setLoading(false);
                }
            }
        }
        fetchData();

        return ()=>{
            isMounted = false;
        }

    },[queryParam]);

    const value = {
        isAvailable: data? data.available_for_work: false,
        resumeURL: data? data.resume_url :"",
        isMaintenance: data?data.web_maintenance_mode:false
    }

    let content;
    if(loading){content = <StatusLoading/>}
    else if(error!=null){content = <StatusError message={error}/>} 
    else if(!data){content=<StatusNoData/>}
    else(
        content=(
            <SystemConfigContext.Provider value={value}>
                {children}
            </SystemConfigContext.Provider>
        )
    )

    return content;
}

export const useSystemConfig = () =>{
    return useContext(SystemConfigContext);
}
