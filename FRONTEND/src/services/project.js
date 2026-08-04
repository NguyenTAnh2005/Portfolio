import axiosInstance from "./axiosConfig";
import { buildFormData } from "../utils/axiosHelper";

const ENDPOINT = "/projects";

export const projectService = {
    getProject: async (id)=>{
        const response = await axiosInstance.get(`/${ENDPOINT}/${id}`);
        return response;
    }
    ,
    listProject: async (queryParam)=>{
        const response = await axiosInstance.get(`${ENDPOINT}/`,{params:queryParam});
        return response;
    }
    ,
    // Code bên ADMIN sẽ hoàn thiện tiếp
    // createProject: async() =>{}
    // ,
    // updateProjectText: async() =>{}
    // ,
    // updateProjectImg: async() =>{}
    // ,
    // syncProject: async()=>{}
    // ,
    // deleteProject: async()=>{}
}