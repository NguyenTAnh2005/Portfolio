import { CircleCheckBig } from "lucide-react"
import clsx from "clsx";
import { motion } from "framer-motion";


const baseclass = ' text-light-text bg-light-surface dark:bg-dark-surface dark:text-dark-text ';
const baseTransition = ' transition-all ease-linear duration-500';


export const  TimelineItem = ({data, index}) =>{
    const isEven = index % 2 === 0;
    
    return (
        // Grid tổng, 1fr auto 1fr
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.6 }}
            className={clsx( baseTransition, "grid grid-cols-[auto_1fr] lg:grid-cols-[1fr_auto_1fr] gap-8 items-center z-10")}>
            {/* Div rỗng độn */}
            <div className={clsx("hidden lg:block ", isEven ? "lg:order-1" : " lg:order-3")}></div>
            {/* Icon - luôn ở cột giữa (auto), tuyệt đối center */}
            <div className={clsx(baseTransition,"w-fit text-primary p-1.5 rounded-full bg-light-bg border-2 border-primary", " lg:order-2 dark:text-dark-text dark:bg-primary")}>
                <CircleCheckBig strokeWidth={2} size={28}/>
            </div>
            {/* Content */}
            <div className={clsx(
                " flex gap-8 items-center border-2 p-4 rounded-2xl hover:cursor-pointer transition-all ease-linear duration-200 hover:shadow-lg hover:shadow-primary hover:-translate-y-2 ", 
                "border-primary/30 bg-primary/10 dark:border-primary/40 dark:bg-primary/15 ",
                isEven?" lg:order-3":" lg:order-1" )
            }>
                <img 
                    className={clsx("w-16 h-16 rounded-full", " lg:h-20 lg:w-20 xl:w-24 xl:h-24", !isEven&&" lg:order-last")} 
                    src={data.img_url} alt={`Timeline: ${data.title}`} 
                />
                <div className={clsx("flex flex-col ", !isEven&&" lg:items-end lg:text-end")}>
                    <span className="font-semibold text-lg lg:text-2xl mb-2 uppercase"> {data.title}</span>
                    <span className={clsx("text-base lg:text-xl py-1 px-2 rounded-md w-fit border", "bg-primary/15 text-primary border-primary/40")}> {data.start_end}</span>
                    <p className="text-xs lg:text-base mt-4 text-light-muted dark:text-dark-muted "> {data.desc}</p>
                </div>
            </div>
        </motion.div>
    )
}
