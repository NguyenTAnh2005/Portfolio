import { useState, useEffect } from "react";
import {Link} from "react-router-dom";
import clsx from "clsx";

import { MapPinHouse, UserPen, Check, ExternalLink } from 'lucide-react';

import { indexService } from "../../services";

import { StatusNoData, StatusLoading, StatusError } from "../../components/ui/FetchStatus";
import {ProjectItem} from "../../components/ProjectItem";
import {AchivementItem} from "../../components/AchievementItem";
import FadeInSection from "../../components/wrapper/FadeInSection";
import { Badge } from "../../components/ui/Badge";
import { DICT_CONFIG_CONTACT } from "../../constants/navigation";
import 
{ 
    baseTextBg, baseBackground, baseBorder,
    baseText, mutedText,bgSurface, 
    animateSlow, animateFast, hoverShadow,
    display, sectionTitle, cardTitle,
    body
} from "../../utils/style";
import {buildContactURL} from "../../utils/contactURL";


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
        <div className= "flex flex-col gap-24">
            <InfoSection data_fetch={data.my_info} dict_config_contact={DICT_CONFIG_CONTACT}/>
            <TechSection data_fetch={data.my_info.techstack}/>
            <TimelineSection data_fetch={data.list_timelines}/>
            <ProjectSection data_fetch={data.list_projects}/>
            <AchievementSection data_fetch={data.list_achievements}/>
        </div>
    )

    return (
        <div className={clsx( 
            baseTextBg, animateSlow
        )}>
            {content}
        </div>
    )
}

const ViewMore = ({link, content})=>{
    return(
        <Badge>
            <div className="flex gap-2 justify-center items-center text-lg px-4 py-2">
                <ExternalLink/>
                <Link to={link} >
                    View more {content} info 
                </Link>
            </div>
        </Badge>
    )
}

const InfoSection = ({data_fetch, dict_config_contact}) =>{
    return(
        <FadeInSection className={clsx(
            "grid grid-cols-12 gap-8"
        )}>
            {/* LEFT INFO */}
            <div className={clsx(
                "flex flex-col gap-4",
                " col-span-10 col-start-2 lg:col-span-6 lg:col-start-2"
            )}>
                <div className={clsx(display, " font-semibold")}>
                    I'm
                    <br/>
                    <span className="text-primary">
                       {data_fetch.fullname} 
                    </span>
                </div>
                <Badge styleClass={clsx("flex w-full lg:max-w-60 items-center justify-center lg:justify-start gap-2 p-2 mt-4")}>
                    <UserPen/>
                    {data_fetch.major}
                </Badge>
                <Badge styleClass={clsx("flex w-full lg:max-w-60 items-center justify-center lg:justify-start gap-2 p-2")}>
                    <MapPinHouse/>
                    {data_fetch.hometown}
                </Badge>
                <p className={clsx(mutedText)}>
                    {data_fetch.intro}
                </p>
                {/* List Contact */}
                <div className="flex gap-4 flex-wrap">
                    {
                        data_fetch.contact.map((item)=>{
                            const config = dict_config_contact[item.name];
                            if (!config) return null;
                            return (
                                <ContactItem
                                    key={`contact-${item.name}`}
                                    Icon={config.icon}
                                    url = {buildContactURL(item.url)}
                                />
                            )
                        })
                    }
                </div>
            </div>

            <div className="col-span-1 lg:hidden"/>

            {/* RIGHT IMAGE */}
            <div className={clsx(
                "flex justify-center items-center",
                " col-span-12 lg:col-span-4 lg:col-start-8"
            )}>
                <img 
                    className="max-w-md w-full aspect-square rounded-full"
                    src="https://4kwallpapers.com/images/walls/thumbs_3t/26748.jpg" 
                    alt="my-info-avt" 
                />
            </div>

        </FadeInSection>
    )
}

const ContactItem = ({url, Icon}) =>{
    return(
        <a className={clsx( animateFast,  
            baseText, baseBorder, " border-2 shadow-md rounded-md p-2",
            hoverShadow," hover:scale-[115%] hover:rotate-6 ")} 
            href={url} target="_blank"
        >
            <Icon size={24}/>
        </a>
    )
}

const TechSection = ({data_fetch}) =>{
    return (
        <FadeInSection className="grid grid-cols-12 gap-8">
            <div className={clsx(sectionTitle, "col-span-12 text-center capitalize")}>
                My Technologies
            </div>
            <div className="grid grid-cols-12 col-span-12 gap-8">
                {/* Datafetch đang là dạng JSONB - Object nên cần chuyển qua mảng cặp key - value */}
                {Object.entries(data_fetch).map(([name, value])=>(
                        <div className="col-span-12 lg:col-span-6 xl:col-span-3" 
                            key={`${name}`}
                        >
                            <ListTech title={`${name}`} list_data={value}/>
                        </div>
                    ))
                }
            </div>
        </FadeInSection> 
    )
}

const ListTech = ({list_data, title }) =>{
    return(
        <div className={clsx( animateSlow, 
            "border-2", baseBorder, bgSurface, 
            " flex flex-col rounded-md gap-4 p-4 h-full"
        )}>
            <span className={clsx(cardTitle, "text-center font-semibold capitalize")}>
                {title}
            </span>
            <div className="flex flex-wrap gap-4 justify-start">
                {list_data.map((item, index)=>(
                    <Badge key={`${index}-${item}`} styleClass={clsx("font-bold font-mono py-2 px-4 text-center")}>
                        {item}
                    </Badge>
                ))}
                {/* {list_data.map((item, index)=>{
                    if(index<3){
                        return(
                        <Badge key={`${index}-${item}`} styleClass={clsx("font-bold font-mono py-2 px-4 text-center")}>
                            {item}
                        </Badge>
                        )
                    }
                })}
                {
                    list_data.length>3 &&(
                    <Badge styleClass={"flex justify-center items-center px-2 rounded-full"}>
                        {`+${list_data.length-3}`}
                    </Badge>
                    )
                } */}

            </div>
        </div>
    )
}

const TimelineIndexItem = ({timeline}) =>{
    return(
        <div className={clsx( animateSlow," flex gap-4 z-10 ")}>
            {/* ICON */}
            <div className="hidden md:flex flex-col gap-4 items-center ">
                <span className={clsx(animateSlow,
                    " h-fit p-1 rounded-full",
                    " bg-primary text-dark-text",
                    // " bg-dark-text border-primary text-primary "
                )}>
                    <Check strokeWidth={3} size={24}  className=""/>
                </span>
                <div className="flex-1 bg-gradient-to-b from-primary to-transparent w-1 rounded-full ">
                </div>
            </div>
            {/* Content */}
            <div className={clsx(animateSlow, baseBackground, baseBorder,
                " flex flex-col w-full py-2 px-4 rounded-lg border-2"
            )}>
                <p className={clsx(cardTitle)}>
                    {timeline.title}
                </p>
                <p className={clsx( body, mutedText)}>
                   {timeline.organization}
                </p>
                <Badge styleClass={"font-semibold mt-4 px-2 py-1 font-mono"}>
                    {timeline.start_end}
                </Badge>
            </div>
        </div>
    )
}

const TimelineSection = ({data_fetch}) =>{
    return(
        <FadeInSection className="grid grid-cols-12 gap-8">
            <div className={clsx( sectionTitle, "text-center col-span-12")}>
                My Timeline
            </div>
            <div className={clsx( animateSlow, baseBorder, bgSurface,
                " col-span-12 md:col-span-10 md:col-start-2 lg:col-span-8 lg:col-start-3",
                " p-8 lg:p-16 flex flex-col gap-8 rounded-xl border-2"
            )}>
                {data_fetch.map((timeline)=>(
                    <TimelineIndexItem
                        key={`timeline-${timeline.id}`} timeline={timeline}
                    />
                ))}
            </div>
            <div className="col-span-12 flex justify-center">
                <ViewMore link={"/timeline"} content={"Timelines"}/>
            </div>
        </FadeInSection>
    )
}

const ProjectSection = ({data_fetch}) =>{
    return(
        <FadeInSection className="grid grid-cols-12 gap-8">
            <div className={clsx( sectionTitle, "text-center col-span-12")}>
                My Projects
            </div>
            <div className="grid grid-cols-12 col-span-12 gap-8 lg:col-span-10 lg:col-start-2">
                {data_fetch.map((project)=>(
                    <div className="col-span-12 sm:col-span-6 xl:col-span-4"   key={`project-${project.id}`}>
                            <ProjectItem project={project} />
                    </div>
                    ))
                }
            </div>
            <div className="col-span-12 flex justify-center">
                <ViewMore link={"/project"} content={"Projects"}/>
            </div>
        </FadeInSection>
    )
}

const AchievementSection = ({data_fetch}) =>{
    return(
        <FadeInSection className="grid grid-cols-12 gap-8">
            <div className={clsx( sectionTitle, " text-center col-span-12")}>
                My Achievements
            </div>
            <div className="grid grid-cols-12 col-span-12 gap-8 lg:col-span-10 lg:col-start-2">
                {data_fetch.map((achievement)=>(
                    <div className="col-span-12 md:col-span-6 lg:col-span-4"   key={`achievement-${achievement.id}`}>
                            <AchivementItem achievement={achievement}/>
                    </div>
                    ))
                }
            </div>
            <div className="col-span-12 flex justify-center">
                <ViewMore link={"/achievement"} content={"Achievements"}/>
            </div>
        </FadeInSection>
    )
}

