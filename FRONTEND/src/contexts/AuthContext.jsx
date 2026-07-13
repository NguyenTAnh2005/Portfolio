/* eslint-disable react-refresh/only-export-components */

import {createContext, useContext, useState} from 'react';

const AuthContext = createContext();

export const AuthProvider = ({children})=>{
    const [token, setToken] = useState(()=> localStorage.getItem('jwt-token'));

    const login = (newToken) =>{
        setToken(newToken);
        localStorage.setItem('jwt-token', newToken);
    };

    const logout = () =>{
        setToken(null);
        localStorage.removeItem('jwt-token');
    };

    const value = {
        token,
        isAuthenticated: !!token, //token != null ? true : false
        login,
        logout
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () =>{
    return useContext(AuthContext);
}