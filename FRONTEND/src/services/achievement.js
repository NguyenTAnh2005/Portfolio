import {buildFormData}  from "../utils/axiosHelper";
import axiosInstance from "./axiosConfig";

const END_POINT = '/achievements';

export const achieveService = {
    get_by_id: async(id) =>{
        const response = await axiosInstance.get(`${END_POINT}/${id}`);
        return response;
    }
    ,
    list_achieve: async(queryParam) =>{
        const response = await axiosInstance.get(`${END_POINT}/`, {params:queryParam});
        return response;
    }
    ,
    create: async(createData)=>{
        const formCreate = buildFormData(createData);
        const response = await axiosInstance.post(`${END_POINT}/`, formCreate);
        return response;
    }
    ,
    update: async(id, updateData) =>{
        const formUpdate = buildFormData(updateData);
        const response = await axiosInstance.put(`${END_POINT}/${id}`, formUpdate);
        return response;
    }
    ,
    delete: async(id) =>{
        const response = await axiosInstance.delete(`${END_POINT}/${id}`);
        return response;
    }
}