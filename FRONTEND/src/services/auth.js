import axiosInstance from "./axiosConfig";

export const authService = {
    login: async (email, password) =>{
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await axiosInstance.post('/auth/login', formData, {headers:{'Content-Type': 'application/x-www-form-urlencoded'}});
        return response;
    },
    getMe: async () =>{
        const response = await axiosInstance.get('/auth/get-me');
        return response;
    }
}