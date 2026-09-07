/* eslint-disable react-refresh/only-export-components */

import {createContext, useContext, useEffect, useState} from 'react';
import { authService } from '../services/auth';
import { StatusLoading, StatusError } from '../components/ui/FetchStatus';
import { tokenManager } from '../services/tokenManager';

const AuthContext = createContext();

export const AuthProvider = ({children})=>{
    const [accessToken, setAccessToken] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(()=>{
        let isMounted = true;
        const getToken = async () =>{
            try {
                if(isMounted){
                    setLoading(true);
                    const response = await authService.refreshToken();
                    setAccessToken(response.access_token);
                    tokenManager.setOneSide(response.access_token);
                }
            } catch (err) {
                // Bỏ qua lỗi 401 - Bên Protected sẽ xử lý thêm sau
                if(isMounted){
                    if(err.response & err.response?.status !== 401){
                        console.error("Lỗi: "+ err.message);
                        setError(err.message);
                    }
                }
            }
            finally{
                if(isMounted){setLoading(false);}
            }
        }
        getToken();
        // Đăng ký các function bên tokenManger
        tokenManager.subcribe(setAccessToken);

        return ()=>{
            isMounted = false;
            // Khi components bị unmount (không được tải lên) thì hủy sub bên tokenManger
            tokenManager.unSubcribe(setAccessToken);
        }
    },[]);

    const clearToken = () =>{
        setAccessToken(null);
        tokenManager.clear();
    }

    const login = (newToken) =>{
        // Lưu access_token vào state, refresh thì trình duyệt tự lo, JS không đụng vào được.
        setAccessToken(newToken);
        tokenManager.setOneSide(newToken);
    };

    async function logout(){ 
        // Gọi logout để backend làm việc các thứ sau đó xóa access_token
        await authService.logOut();
        clearToken();
    };

    const value = {
        accessToken,
        // (if access_token là access_token khác null)
        // Dấu ! đầu tiên: nếu !access_token -> nếu có token thì là False, không có thì là True
        // Dấu ! thứ high: biến đổi ngược lại cho đúng, Ô khê.
        isAuthenticated: !!accessToken,
        clearToken, 
        login,
        logout
    };

    let content;
    if (loading) {content=<StatusLoading/>}
    else if (error){content = <StatusError message={error}/>}
    else {
        content=(
            <AuthContext.Provider value={value}>
                {children}
            </AuthContext.Provider>
        )
    }

    return content;
};

export const useAuth = () =>{
    return useContext(AuthContext);
}