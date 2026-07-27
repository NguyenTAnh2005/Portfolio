import { useState, useEffect } from "react";
import { infoService } from "../../services/info";
import clsx from "clsx";
import { motion } from "framer-motion";

import {FaPython, FaJs, FaReact, FaBootstrap } from "react-icons/fa";
import { RiTailwindCssFill } from "react-icons/ri";
import { AiOutlineDotNet } from "react-icons/ai";
import { SiFastapi } from "react-icons/si";
import { TbBrandCpp, TbBrandCSharp } from "react-icons/tb";

import { FaGithub, FaFacebook, FaInstagram, FaPhone, FaEnvelope } from "react-icons/fa";


import MyAvt from "../../assets/me.jpg";
import { InfoBadge, TechBadge, ContactBadge } from "../../components/Badge";
import { StatusLoading, StatusError, StatusNoData } from "../../components/FetchStatus";

const baseclass = ' text-light-text bg-light-surface dark:bg-dark-surface dark:text-dark-text ';
const baseTransition = ' transition-all ease-linear duration-500';

// const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export default function AboutMe(){
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(()=>{
        // Nếu thắc mắc về cột ismouted thì tham khảo trong docs unMouted nhé!
        let isMouted = true;
        const fetchData = async () =>{
            try{
                setLoading(true);
                //  await sleep(2000);
                const response = await infoService.getInfo(1);
                if(isMouted) {setData(response.data);}
            }
            catch(err){
                if(isMouted)
                {
                    console.log("Lỗi: ", err);
                    setError(err.message);
                }
            }
            finally{
                if(isMouted){setLoading(false);}
            }
        }
        fetchData();
        return ()=>{
            isMouted=false;
        };
    },[]);

    let content;
    if (loading) {content = <StatusLoading/>;}
    else if(error!= null){ content = <StatusError message={error}/>;} 
    else if (!data){ content = <StatusNoData/>;} 
    else{
        content= (
            <div className="flex flex-col">
                {/* Hero */}
                <HeroSection data={data}/>
                {/* Bio*/}
                <BioSection data={data}/>
                {/* téch, libs */}
                <TechListSection data={data} config_lang={LANGUAGE_CONFIG}  config_lib={LIB_CONFIG}/>
                {/* Contact links */}
                <ContactSection data={data}/>
            </div>
    )}
    
    return (
        <div className="">
            <div className={clsx(baseclass, " ")}>
                {content}
            </div>
        </div>
    )
}

export const LANGUAGE_CONFIG = {
  "Python": { name: "Python", icon: FaPython, website: "https://python.org", styleClass: " bg-[#3776AB] text-white"},
  "C#": { name: "C#", icon: TbBrandCSharp ,website: "https://microsoft.com", styleClass: " bg-[#239120] text-white"},
  "C++": { name: "C++", icon: TbBrandCpp,  website: "https://isocpp.org",styleClass: " bg-[#00599C] text-white" },
  "JavaScript": { name: "JavaScript", icon: FaJs, website: "https://mozilla.org", styleClass: " bg-[#F7DF1E] text-black "}
};

export const LIB_CONFIG = { 
    "Bootstrap": { name: "Bootstrap",  icon: FaBootstrap, website: "https://getbootstrap.com", styleClass: "bg-[#7952B3] text-white font-semibold"},
    "React": {  name: "React", icon: FaReact, website: "https://react.dev",styleClass: "bg-[#61DAFB] text-[#20232A] font-bold" },
    "Tailwind": { name: "Tailwind", icon: RiTailwindCssFill, website: "https://tailwindcss.com",  styleClass: "bg-[#38BDF8] text-white font-semibold"},
    ".NET": {name: ".NET", icon: AiOutlineDotNet, website: "https://microsoft.com", styleClass: "bg-[#512BD4] text-white font-semibold"},
    "FastAPI": { name: "FastAPI",  icon: SiFastapi, website: "https://tiangolo.com", styleClass: "bg-[#009688] text-white font-semibold"}
};

export const CONTACT_CONFIG = {
    phone:   { icon: FaPhone, content:"+84 328884320",     styleClass: "bg-green-500 text-white" },
    github:  { icon: FaGithub, content:"NguyenTAnh2005",   styleClass: "bg-[#181717] text-white" },
    email1:  { icon: FaEnvelope, content:"23050118@student.bdu.edu.vn", styleClass: "bg-red-500 text-white" },
    email2:  { icon: FaEnvelope, content:"anhnguyentaun@gmail.com", styleClass: "bg-red-500 text-white" },
    facebook:{ icon: FaFacebook, content:"tuan.anh.514281", styleClass: "bg-[#1877F2] text-white" },
    instagram:{ icon: FaInstagram, content:"tanh_2005_",styleClass: "bg-gradient-to-tr from-[#f9ce34] via-[#ee2a7b] to-[#6228d7] text-white" },
};

const HeroSection = ({data})=>{
    const badge_list = [
        {keyName: "gender", icon:"👤", content: data.gender ? "Male":"Female" },
        {keyName: "major", icon:"💼", content: data.major },
        {keyName: "location", icon:"🏠", content: data.hometown}
    ]
    return(
        <motion.div 
        // Tham Khảo copy paste
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.6 }}
        className="grid grid-cols-12 gap-8 py-8">
            <div className={clsx("col-span-12 px-8 flex flex-col gap-2 items-center ", "transition-all duration-500 ease-linear ", " lg:col-span-7")} >
                    <span className={clsx("text-8xl uppercase font-serif mt-8")}>
                        <span>about </span>
                        <span className="text text-primary">me</span>
                    </span>
                    <span className={clsx("px-3 py-1 rounded-md border-2 text-lg font-bold mb-8 w-fit", baseTransition , " duration-100 hover:scale-105",
                        "bg-primary/10  border-primary/30  dark:bg-primary/5 dark:border-primary/40")}>
                        {data.fullname}
                    </span>
                    <span className={clsx("text-center text-base italic mb-8 px-8 lg:px-0 ", "text-light-muted dark:text-dark-muted")}>
                        {data.intro}
                    </span>
                    <div className="flex flex-wrap gap-4">
                    </div>
                    <div className="flex justify-center flex-wrap gap-2 md:gap-4 lg:gap-8">
                        {badge_list.map(item =>(
                            <InfoBadge key={`badge ${item.keyName}`} icon={item.icon} content={item.content}/>
                        ))}
                        <span className="cursor-pointer">
                            <a href="#contact"> <InfoBadge icon={"☎️"} content={"Contact me"}/> </a>
                        </span>
                    </div>
            </div>
            <div className={clsx("col-span-12 flex justify-center items-center ", " lg:col-span-5 lg:col-start-8")} >
                <img
                className={clsx(baseTransition, " w-full aspect-[1/1] rounded-lg border-4 ", "max-w-80 dark:border-primary/80 border-primary/60", " lg:max-w-80 ")}
                // src={MyAvt}
                src="https://4kwallpapers.com/images/walls/thumbs_3t/26748.jpg" 
                alt="about-me-avt"/>
            </div>
        </motion.div>
    )
}
const BioSection = ({data}) =>{
    return(
        <motion.div
        // Tham Khảo copy paste
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.6 }}
         className={clsx(baseTransition, " col-span-12 text-4xl py-16 px-8 "," ")}>
            <p className="italic font-serif text-center max-w-xl mx-auto">
                "{data.bio}."
            </p>
        </motion.div>
    )
}

const renderTechBadges = (dataFetch, dataConfig) =>{
    const content = (
        dataFetch?.map((item)=>{
            const config = dataConfig[item];
            if (!config){
                console.warn(`Chưa có config cho: ${item}`);
                return null;
            }
            return(
                <TechBadge
                key={config.name} name={config.name}  website={config.website} 
                styleClass={config.styleClass}icon={config.icon}/>
            )
        })
    )
    return(
        <>
        {content}
        </>
    );
}
const TechListSection = ({data, config_lang, config_lib})=>{
    return(
        <motion.div
        // Tham Khảo copy paste
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.6 }}
        className={clsx(baseTransition, " p-8 flex flex-col gap-24 lg:grid lg:grid-cols-12 ")}>
            <div className="flex flex-col gap-8 lg:grid lg:col-span-6 lg:justify-center lg:items-start lg:h-fit">
                <p className="text-3xl uppercase text-center font-bold">
                    Programming Languages
                </p>
                <div className="flex gap-8 flex-wrap justify-center lg:justify-start">
                    {renderTechBadges(data.language, config_lang)}
                </div>
            </div>
            <div className="flex flex-col gap-8 lg:grid lg:col-span-6 lg:justify-center lg:items-start lg:h-fit">
                <p className="text-3xl uppercase text-center font-bold ">
                    Frameworks & Library
                </p>
                <div className="flex gap-8 flex-wrap justify-center lg:justify-start">
                    {renderTechBadges(data.framework, config_lib)}
                </div>
            </div>
        </motion.div>
    )
}

const ContactSection = ({ data }) => {
    return(
        <motion.div 
        // Tham Khảo copy paste
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.6 }}
        className={clsx(baseTransition, " flex flex-col gap-8 py-16 lg:px-16")}>
            <p className="text-4xl font-bold text-center uppercase ">
                Contact me
            </p>
            <div id="contact" className="flex flex-wrap justify-center gap-4">
                {data.contact.map((item) => {
                    const config = CONTACT_CONFIG[item.name];
                    if (!config) return null;
                    return (
                        <ContactBadge
                            key={item.name}
                            icon={config.icon}
                            styleClass={config.styleClass}
                            name={item.name}
                            content={config.content}
                            url={item.name.startsWith("email") ? `mailto:${item.url}`
                                : item.name === "phone" ? `tel:${item.url}` : item.url}
                        />
                    );
                })}
            </div>
        </motion.div>
    )
}