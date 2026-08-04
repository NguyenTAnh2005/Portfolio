import axiosInstance from './axiosConfig';
import { buildFormData } from '../utils/axiosHelper';

const END_POINT = '/timelines';
// tạo service gồm các func: 
export const TimelineService = {

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
        return response;
    }
    ,
    // POST - nhận đầu vào là FormData (buộc có đầy đủ các field)
    // create: async(data) =>{
    //     // eg: data = {title: "abc", desc:"Hi",...}
    //     const formData = buildFormData(data);
    //     const response = await axiosInstance.post(`${END_POINT}/`, formData);
    //     return response;
    // }
    // ,
    // PUT - Nhận vào: id cần sửa, FormData (Optional các field --> helper sẽ giúp bỏ những cái ko đổi)
    // update: async(id, data)=>{
    //     const formData = buildFormData(data);
    //     const response = await axiosInstance.put(`${END_POINT}/${id}`, formData);
    //     return response;
    // }
    // ,
    // DELETE - Nhận vào là id cần xóa
    // delete: async(id)=>{
    //     const response = axiosInstance.delete(`${END_POINT}/${id}`);
    //     return response;
    // }
}

