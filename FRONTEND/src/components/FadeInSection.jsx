import { motion } from "framer-motion";

const FadeInSection = ({children, className, delay = 0, duration = 0.6})=>{
    return(
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration, delay }}

            className={className}
        >
            {children}
        </motion.div>
    )
}
export default FadeInSection;