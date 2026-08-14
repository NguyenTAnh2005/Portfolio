import axiosInstance from "./axiosConfig";

const END_POINT = "/system-configs";

export const systemConfigService ={
    // GET - Nhận int là id cần tìm
    get: async(id) =>{
        // id: 1
        const response = await axiosInstance.get(`${END_POINT}/${id}`);
        return response;
    }
    ,
    // GetAll - Nhận object, axios tự parse -> chuỗi query param
    getAll: async(queryParam)=>{
        const response = await axiosInstance.get(`${END_POINT}/`, {params:queryParam});
        const configMap= {};
        response.data?.forEach((item)=>{
            configMap[item.name] = item.value;
        });
        return configMap;
    },
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
