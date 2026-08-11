import { useState, useEffect } from "react";
import clsx from "clsx";
import {Link} from "react-router-dom"
import { MapPinHouse } from 'lucide-react';
import { Check } from 'lucide-react';

import { indexService } from "../../services";
import { StatusNoData, StatusLoading, StatusError } from "../../components/FetchStatus";
import {ProjectItem} from "../../components/ProjectItem";
import {AchivementItem} from "../../components/AchievementItem";
import FadeInSection from "../../components/FadeInSection";

import { FaGithub, FaFacebook, FaInstagram, FaPhone, FaEnvelope } from "react-icons/fa";


const baseclass = ' text-light-text bg-light-surface dark:bg-dark-surface dark:text-dark-text ';
const baseTransition = ' transition-all ease-linear duration-500';

export const  DICT_CONFIG_CONTAG = {
    phone: {icon: FaPhone}, 
    github: {icon: FaGithub}, 
    email1: {icon: FaEnvelope}, 
    email2: {icon: FaEnvelope}, 
    facebook: {icon: FaFacebook}, 
    instagram: {icon: FaInstagram}
}

export default function Index(){
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);

    useEffect(()=>{
        // Cờ báo hiệu components còn sống, có trên trang html
        let isMounted = true;
        const fetchData = async()=>{
            try {
                if (isMounted){
                    const response = await indexService.get_list_data();
                    setData(response.data)
                }
            } 
            catch (err) {
                if (isMounted){
                    console.error(`Lỗi khi fetch data: ${err.message}`);
                    setError(err.message);
                }
            }
            finally {
                if(isMounted){setLoading(false)}
            }
        }

        fetchData();

        return ()=>{
            isMounted = false;
        }
    },[]);

    let content;
    if(loading){content = <StatusLoading/>}
    else if(error!=null){content = <StatusError message={error}/>} 
    else if(!data){content=<StatusNoData/>}
    else content= (
        <div className={clsx(
            baseclass, baseTransition
        )}>
            <InfoSection data_fetch={data.my_info} dict_config_contact={DICT_CONFIG_CONTAG}/>
            {/* <TechSection data_fetch={data.my_info}/>
            <TimelineSection data_fetch={data.list_timelines}/>
            <ProjectSection data_fetch={data.list_projects}/>
            <AchievementSection data_fetch={data.list_achievements}/> */}
        </div>
    )

    
    return (
        <div>
            {content}
        </div>
    )
}

const InfoSection = ({data_fetch, dict_config_contact}) =>{
    return(
        <FadeInSection className={clsx(
            "grid grid-cols-12 gap-6"
        )}>
            {/* LEFT INFO */}
            <div className={clsx(
                "flex flex-col gap-4",
                " col-span-9 col-start-2 lg:col-span-4 lg:col-start-2"
            )}>
                <div className="text-5xl font-semibold">
                    I'm
                    <br/>
                    <span className="text-primary">
                       {data_fetch.fullname} 
                    </span>
                </div>
                <p className="text-3xl font-semibold">
                    {data_fetch.major}
                </p>
                <div className=" flex items-center justify-center w-fit gap-2 rounded-lg font-light bg-primary p-2">
                    <MapPinHouse/>
                    {data_fetch.hometown}
                </div>
                <p className="font-light text-base">
                    {data_fetch.intro}
                </p>
                {/* List Contact */}
                <div className="flex gap-2">
                    {
                        data_fetch.contact.map((item)=>{
                            const config = dict_config_contact[item.name];
                            if (!config) return null;
                            return (
                                <ContactItem
                                    key={`contact-${item.name}`}
                                    Icon={config.icon}
                                    url = {
                                        item.name.startsWith('email')?`mailto:${item.url}`
                                        :item.name == "phone"?`tel:${item.url}`:item.url
                                    }
                                />
                            )
                        })
                    }
                </div>

            </div>

            {/* RIGHT IMAGE */}
            <div className={clsx(
                "flex justify-center items-center",
                " col-span-12 lg:col-span-4 lg:col-start-8"
            )}>
                <img 
                    className="max-w-md aspect-square rounded-full"
                    src="https://4kwallpapers.com/images/walls/thumbs_3t/26748.jpg" 
                    alt="my-info-avt" 
                />
            </div>

        </FadeInSection>
    )
}
const TechSection = ({data_fetch}) =>{
    return (
        <FadeInSection className="grid grid-cols-12 gap-6 py-8 px-8 lg:px-0">
            <ListTech
                list_data={data_fetch.language}
                title={"Programming Languages"}
                class_grid={"lg:col-start-1"}
            />
            <ListTech
                list_data={data_fetch.framework}
                title={"Library and Framework"}
                class_grid={"lg:col-start-7"}
            />
        </FadeInSection>
    )
}

const ContactItem = ({url, Icon}) =>{
    return(
        <a className=" text-dark-text border-dark-text border-2 rounded-md p-2" href={url} target="_blank">
            <Icon size={24}/>
        </a>
    )
}
const TechItem = ({name})=>{
    return(
        <span 
            className={clsx(
                "inline-block px-3 py-1 font-semibold rounded-md",
                " bg-primary/20 text-primary dark:bg-primary/10"
            )}>
            {name}
        </span>
    )
}

const ListTech = ({list_data, title, class_grid}) =>{
    return(
        <div className={clsx(
            "col-span-12 border flex flex-col rounded-md p-4 gap-4",
            " bg-light-bg border-light-text/15 dark:bg-dark-bg dark:border-dark-text/15",
            "lg:col-span-5 lg:col-start-2", class_grid
        )}>
            <span className="font-semibold text-2xl">
                {title}
            </span>
            <div className="flex flex-wrap gap-2">
                {list_data.map((item)=>(
                    <TechItem name={item} key={`${item}`}/>
                ))}
            </div>
        </div>
    )
}




const TimelineIndexItem = ({timeline}) =>{
    return(
        <div className="flex gap-4 z-10 ">
            {/* ICON */}
            <div className="flex flex-col gap-4 items-center">
                <span className={clsx(
                    "border-2  h-fit p-1 rounded-full",
                    " dark:bg-primary dark:text-dark-text",
                    "  bg-dark-text border-primary text-primary "
                )}>
                    <Check strokeWidth={3} size={20}  className=""/>
                </span>
                <div className="flex-1 bg-gradient-to-b from-primary to-transparent w-1 rounded-full ">
                </div>
            </div>
            {/* Content */}
            <div className={clsx(
                "flex flex-col gap-2 border w-full py-2 px-4 rounded-lg",
                " bg-light-surface dark:bg-dark-surface",
                " border-light-text/15 dark:border-dark-text/15"
            )}>
                <p className="text-2xl font-semibold">
                    {timeline.title}
                </p>
                <p className="text-light-muted dark:text-dark-muted">
                    📍 {timeline.organization}
                </p>
                <p className="text-primary font-semibold mt-4">
                    {timeline.start_end}
                </p>
            </div>
        </div>
    )
}

const TimelineSection = ({data_fetch}) =>{
    return(
        <FadeInSection className="grid grid-cols-12 gap-8 mt-16">
            <div className="col-span-12 text-center text-5xl font-semibold uppercase">
                My Timeline
            </div>
            <div className={clsx(
                " col-span-10 col-start-2 lg:col-span-6 lg:col-start-4",
                " p-8 lg:p-16 flex flex-col gap-8 rounded-xl border-2",
                " border-light-text/15 dark:border-dark-text/15",
                " bg-light-bg dark:bg-dark-bg"
            )}>
                {data_fetch.map((timeline)=>(
                    <TimelineIndexItem
                        key={`timeline-${timeline.id}`} timeline={timeline}
                    />
                ))}
            </div>
            <div className="col-span-12 flex justify-center">
                <span className={clsx(
                    "inline-block px-3 py-1 font-semibold rounded-md",
                    " bg-primary/20 text-primary dark:bg-primary/10"
                )}>
                    <Link to={"/timeline"}>
                        View more timeline info. 
                    </Link>
                </span>
            </div>
        </FadeInSection>
    )
}


const ProjectSection = ({data_fetch}) =>{
    return(
        <FadeInSection className="grid grid-cols-12 mt-16">
            <div className="col-span-12 text-center text-5xl font-semibold uppercase">
                My Projects
            </div>
            <div className="grid grid-cols-12 col-span-12 gap-6 py-8 px-8 lg:px-0 lg:col-span-10 lg:col-start-2">
            {
                data_fetch.map((project) =>(
                    <ProjectItem 
                        key={`project-${project.id}`}
                        project={project}
                    />
                ))
            }
            </div>
            <div className="col-span-12 flex justify-center">
                <span className={clsx(
                    "inline-block px-3 py-1 font-semibold rounded-md",
                    " bg-primary/20 text-primary dark:bg-primary/10"
                )}>
                    <Link to={"/project"}>
                        View more projects info. 
                    </Link>
                </span>
            </div>
        </FadeInSection>
    )
}

const AchievementSection = ({data_fetch}) =>{
    return(
        <FadeInSection className="grid grid-cols-12 mt-16">
            <div className="col-span-12 text-center text-5xl font-semibold uppercase">
                My Achievements
            </div> 
            <div className="grid grid-cols-12 col-span-12 gap-6 py-8 px-8 lg:px-0 lg:col-span-10 lg:col-start-2">
            {
                data_fetch.map((achievement) =>(
                    < AchivementItem
                        key={`project-${achievement.id}`}
                        achievement={achievement}
                    />
                ))
            }
            </div>
            <div className="col-span-12 flex justify-center">
                <span className={clsx(
                    "inline-block px-3 py-1 font-semibold rounded-md",
                    " bg-primary/20 text-primary dark:bg-primary/10"
                )}>
                    <Link to={"/achievement"}>
                        View more achievements info. 
                    </Link>
                </span>
            </div>
        </FadeInSection>
    )
}