import axios from 'axios';
import { authService } from './auth';
import { navigateLogIn } from '../utils/navigateLogIn';
import { tokenManager } from './tokenManager';

const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    headers:{
        'Content-Type': 'application/json',
    },
    // bật true để bắt buộc trình duyệt tự động đính kèm cookie vào request để gọi API.
    withCredentials:true
});

let accessToken = tokenManager.get();

axiosInstance.interceptors.request.use(
    
    (config) => {
        if(accessToken) config.headers.Authorization = `Bearer ${accessToken}`;
        return config;
    },
    (error) =>{
        return Promise.reject(error);
    }
);
// Cấu trúc response xem trong file doc note error handling nhé.

axiosInstance.interceptors.response.use(
    // Nhánh xử lý status thành công (201-299)
    // Tham số nhận vào đối tượng là 'response'
    // VÍ DỤ RESPONSE
    // {
    //   status: 200,
    //   statusText: "OK",
    //   headers: { "content-type": "application/json", ... },
    //   config: { ... },        // thông tin request đã gửi (url, method, headers...)
    //   request: XMLHttpRequest, // object request gốc (hiếm khi cần dùng tới)
    //=> data: {    // <-- đây mới là phần response.data bên dưới
    //     success: true,
    //     message: "🎉 Lấy thông tin Admin hiện tại thành công!",
    //     data: {
    //       id: 1,
    //       fullname: "...",
    //       email: "...",
    //       role: "ADMIN"
    //     }
    //   }
    // }
    (response) =>{
        // Cục Data này là cục chứa success:true, message:.. đó
        // Về phần login hay refresh thì dạng sẽ chứa "refresh_token":..., 
        // thì bên page login sẽ xử lý sau, may thí. 
        return response.data
    },

    // NHÁNH 2: Xử lý lỗi 401
    // Tham số nhận vào là đối tượng 'error
    //  Ví dụ Response
    // {
    //   message: "Request failed with status code 401",  // message chung của axios, không phải của bạn
    //   code: "ERR_BAD_REQUEST",
    //   config: { ... },
    //   request: XMLHttpRequest,
    //   response: {                 // <-- object này tồn tại NẾU server có trả về response (không phải lỗi mạng)
    //     status: 401,
    //     statusText: "Unauthorized",
    //     headers: { ... },
    //     data: {                   // <-- body lỗi thật sự, đúng shape từ exception_handler
    //       success: false,
    //       error_code: "WRONG_PASSWORD",
    //       message: "❌ Email hoặc mật khẩu chưa chính xác. Vui lòng kiếm tra lại!",
    //       data: null
    //     }
    //   }
    // }

    async (error) =>{
        // Bắt lỗi 401
        if(error.response && error.response.status === 401){
            // Gọi cấp access token ngầm
            try {
                const response_access = await authService.refreshToken();
                // Nếu thành công thì cập nhật access_token mới, retry request gốc.
                login(response_access.access_token);

            } catch (error) {
                // Nếu thất bại, clear state, điều hướng log-in.
                console.error("Lỗi: Phiên đăng nhập hết hạn, vui lòng đăng nhập lại. [ Mesage: ", error.message, " ]");
                clearToken();
                navigateLogIn();
            }
            
        }
        return Promise.reject(error.response?.data || error);
    }
    // (error) => {
    //     if(error.response && error.response.status === 401){
    //         console.error("Phiên đăng nhập hết hạn hoặc access token không hợp lệ!");
    //         localStorage.removeItem('jwt-token');
    //         if (window.location.pathname !== "/log-in"){
    //             window.location.href = '/log-in';
    //         }
    //     }
    //     return Promise.reject(error.response?.data || error);
    // }
);

export default axiosInstance;