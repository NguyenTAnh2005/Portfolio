import axios from 'axios';

const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    headers:{
        'Content-Type': 'application/json',
    }
});

axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('jwt-token');
        if(token) config.headers.Authorization = `Bearer ${token}`;
        return config;
    },
    (error) =>{
        return Promise.reject(error);
    }
);

axiosInstance.interceptors.response.use(
        // {
        //     "status": 200,
        //     "headers": { ... },
        //     "config": { ... },
        //     "data": { 
        //         "success": true, 
        //         "message": "Đăng nhập thành công!", 
        //         "data": { "access_token": "...", "token_type": "bearer" } 
        //     }
        // }
    (response) =>{
        return response.data
    },
    (error) => {
        if(error.response && error.response.status === 401){
            console.error("Phiên đăng nhập hết hạn hoặc access token không hợp lệ!");
            localStorage.removeItem('jwt-token');
            if (window.location.pathname !== "/log-in"){
                window.location.href = '/log-in';
            }
        }
        return Promise.reject(error.response?.data || error);
    }
);

export default axiosInstance;