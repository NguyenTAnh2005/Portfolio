import axiosIntance from './axiosConfig';

const ENDPOINT = "/index-list";

export const indexService = {
    get_list_data: async()=>{
        const response = await axiosIntance.get(`${ENDPOINT}`);
        return response
    }
}