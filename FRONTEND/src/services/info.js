import axiosInstance from "./axiosConfig";

const ENDPOINT = "/info";

export const infoService = {
    getInfo: async (id) =>{
        const response = await axiosInstance.get(`${ENDPOINT}/${id}`);
        return response;
    },
    updateInfo: async(id, param) =>{
        const response = await axiosInstance.put(`${ENDPOINT}/${id}`, param);
        return response;
    }
}