import { motion } from "framer-motion";
import { Frown, Annoyed, ArrowRight} from "lucide-react";
import clsx from 'clsx';
export const StatusLoading =()=>{
    return(
        <div  className="flex flex-col justify-center items-center gap-4 h-[50vh]">
            <motion.div className="w-10 h-10 border-4 border-solid rounded-full dark:border-white dark:border-t-primary border-primary border-t-white"
            animate={{rotate:360}}
            transition={{  duration: 1, repeat: Infinity, ease:"linear"}}>
            </motion.div>
            
            <span className="text-2xl">
                Waiting to load data!
            </span>
        </div>
    )
}

export const ContactButton = ({baseClass}) =>{
    return(
        <a href="https://www.facebook.com/tuan.anh.514281/?locale=vi_VN" target="blank"
        className={clsx(baseClass, "flex justify-center gap-2 p-2 rounded-md font-semibold transition-all duration-200 ease-linear")}>
            <ArrowRight />
            <span>
                Contact support here!
            </span>
        </a>
    )
}

export const StatusError = ({message}) =>{
    return(
        <div className="flex justify-center h-[50vh] items-center">
            <div className="flex flex-col items-center max-w-md w-full p-8 rounded-xl bg-light-surface gap-4 transition-all duration-500 ease-linear">
                <div className="bg-red-100 text-red-600 p-4 rounded-full">
                    <Frown size={40}/>
                </div>
                <div className="flex flex-col items-center gap-2">
                    <span className="text-xl text-red-800 font-bold">
                        Oops! Some thing went wrong.
                    </span>
                    <span className="text-base text-red-400">
                        {message}
                    </span>
                </div>
                <ContactButton
                baseClass={"bg-red-200 text-red-600 hover:bg-red-600 hover:text-red-200 mt-4"}
                />

            </div>
        </div>
    )
}

export const StatusNoData = () =>{
    return(
        <div className="flex justify-center h-[50vh] items-center">
            <div className="flex flex-col items-center max-w-md w-full p-8 rounded-xl bg-light-surface gap-4 transition-all duration-500 ease-linear">
                <div className="bg-gray-200 text-gray-600 p-4 rounded-full">
                    <Annoyed size={40}/>
                </div>
                <div className="flex flex-col items-center gap-2 text-center">
                    <span className="text-xl text-gray-800 font-bold">
                        No Data Available
                    </span>
                    <span className="text-base text-gray-400">
                        The connection is okay but there're no data from response.
                    </span>
                </div>

                <ContactButton
                baseClass={"bg-gray-200 text-gray-600 hover:bg-gray-600 hover:text-gray-200 mt-4"}
                />
            </div>
        </div>
    )
}