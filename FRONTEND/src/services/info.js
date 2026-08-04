import axiosInstance from "./axiosConfig";

const ENDPOINT = "/infos";

export const infoService = {
    getInfo: async (id) =>{
        const response = await axiosInstance.get(`${ENDPOINT}/${id}`);
        return response;
    }
    ,
    // updateInfo: async(id, param) =>{
    //     const response = await axiosInstance.put(`${ENDPOINT}/${id}`, param);
    //     return response;
    // }
}