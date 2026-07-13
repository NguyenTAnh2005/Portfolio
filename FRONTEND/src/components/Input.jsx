import { Eye, EyeClosed} from 'lucide-react';
import { useState } from "react";

export const Input = ({inputType, Icon, label, required = true, placeHolder, isPassword = false, value, onChange}) =>{
    const [ showPassword, setShowPassword] = useState(false);
    const changeModeType = () =>{
        setShowPassword(prevResult => !prevResult);
    };

    return (
        <div className='flex-col my-3'>
            <p className='text-start text-base font-semibold'>
                {label}
            </p>
            <div className='flex relative border-light-muted border border-solid items-center px-1 rounded-md'>
                <input
                    value={value}
                    onChange={onChange} 
                    required = {required}
                    placeholder={placeHolder}
                    type = { !isPassword 
                        ? inputType 
                        : (showPassword? "text" : "password")
                    }
                    className='text-light-text dark:text-dark-text bg-light-bg dark:bg-dark-bg focus:outline-none indent-7 w-full p-2'
                />

                <Icon className='text-light-muted dark:text-dark-muted absolute'/>
                
                {isPassword && (
                        <div onClick={changeModeType} className='cursor-pointer'>
                            {showPassword? <Eye/> : <EyeClosed/>}
                        </div>
                )}
            </div>
        </div>
    )
}