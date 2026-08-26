import { useState, useEffect } from "react";
import { infoService } from "../../services/info";
import clsx from "clsx";

import { useSystemConfig } from "../../contexts/SystemConfigContext";

import { CONTACT_CONFIG } from "../../constants/aboutmeConfig";
import FadeInSection from "../../components/wrapper/FadeInSection";
import { InfoBadge, ContactBadge, Badge } from "../../components/ui/Badge";
import { StatusLoading, StatusError, StatusNoData } from "../../components/ui/FetchStatus";

import 
{ 
    baseBorder, baseTextBg, bgSurface, mutedText,
    animateSlow, sectionTitle,
    bodyLarge, display,
    
} from "../../utils/style";
import { buildContactURL } from "../../utils/contactURL";

export default function AboutMe(){
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const {isAvailable} = useSystemConfig();

    useEffect(()=>{
        // Nếu thắc mắc về cột ismouted thì tham khảo trong docs unMouted nhé!
        let isMounted = true;
        const fetchData = async () =>{
            try{
                if(isMounted){
                    setLoading(true);
                    const response = await infoService.getInfo(1);
                    setData(response.data);
                }
            }
            catch(err){
                if(isMounted)
                {
                    console.error("Lỗi: ", err);
                    setError(err.message);
                }
            }
            finally{
                if(isMounted){setLoading(false);}
            }
        }
        fetchData();
        return ()=>{
            isMounted=false;
        };
    },[]);

    let content;
    if (loading) {content = <StatusLoading/>;}
    else if(error!= null){ content = <StatusError message={error}/>;} 
    else if (!data){ content = <StatusNoData/>;} 
    else{
        content= (
            <div className="flex flex-col gap-16">
                {/* Hero */}
                <HeroSection  data={data} isAvailable={isAvailable} />
                {/* Bio*/}
                <BioSection   data={data} />
                {/* téch, libs */}
                <TechListSection data={data} />
                {/* Contact links */}
                <ContactSection data={data} />
            </div>
    )}
    
    return (
        <div className={clsx(baseTextBg, animateSlow)}>
            {content}
        </div>
    )
}

const HeroSection = ({data, isAvailable})=>{
    // Danh sách các Badge hiển thị 
    const badge_list = [
        {keyName: "gender", icon:"♂️", content: data.gender ? "Male":"Female" },
        {keyName: "major", icon:"💼", content: data.major },
        {keyName: "location", icon:"🏠", content: data.hometown},
        {keyName: "contact", icon: "☎️", content: "Contact me"}
    ]
    return(
        <FadeInSection className="grid grid-cols-12 gap-8 lg:gap-0">
            {/* Thông tin cá nhân bên trái */}
            <div className={clsx( animateSlow,
                " col-span-12 flex flex-col gap-2 items-center",
                " lg:items-start lg:col-span-5 lg:col-start-2"
            )} >
                    <span className={clsx( display, " uppercase text-center")}>
                        <span>about </span>
                        <span className="text-primary">me</span>
                    </span>
                    <Badge styleClass={clsx("text-lg px-4 py-2 mt-4")}>
                        👤 {data.fullname}
                    </Badge>
                    <Badge styleClass={clsx("text-lg px-4 py-2 mb-4")}>
                            {isAvailable
                                ? "🎯 Available for work" 
                                :"❌ Not available for work"
                            } 
                    </Badge>
                    <p className={clsx(mutedText,
                        "text-center lg:text-start text-base italic ", 
                    )}>
                        {data.intro}
                    </p>
                    <div className="flex justify-center lg:justify-start flex-wrap gap-2 mt-4">
                        {badge_list.map(item =>(
                            <InfoBadge 
                                key={`badge-${item.keyName}`} 
                                keyName = {item.keyName} 
                                icon={item.icon} 
                                content={item.content}
                            />
                        ))}
                    </div>
            </div>
            {/* Avatar bên phải */}
            <div className={clsx(
                "col-span-12 flex justify-center items-center ", " lg:col-span-6"
            )} >
                <img
                className={clsx( animateSlow, baseBorder, " w-full aspect-[1/1] max-w-[360px] rounded-xl border-4")}
                // src={MyAvt}
                src="https://4kwallpapers.com/images/walls/thumbs_3t/26748.jpg" 
                alt="about-me-avt"/>
            </div>
        </FadeInSection>

    )
}

const BioSection = ({data}) =>{
    return(
        <FadeInSection>
            <p className={clsx( sectionTitle, "italic text-center max-w-xl mx-auto")}>
                "{data.bio}"
            </p>
        </FadeInSection>
    )
}

const ListTech = ({list_data, title, keyname}) =>{
    return(
        <div className="flex flex-col gap-2">
            <p className={clsx(bodyLarge)}>
                {title}
            </p>
            <div className="flex flex-wrap gap-4">
                {list_data.map((item, index)=>(
                    <Badge key={`${keyname}-${index}`} styleClass={clsx("font-bold font-mono py-2 px-4 text-center")}>
                        {item}
                    </Badge>
                ))}
            </div>
        </div>
    )
}

const TechListSection = ({data})=>{
    return(
        <FadeInSection className={clsx(
            bgSurface, animateSlow, " border-2", baseBorder,
            "flex flex-col gap-8 px-4 py-8 rounded-2xl justify-start"
        )}>
            <div className="mb-4">
                <p className={clsx( sectionTitle, " text-center mb-4")}>
                    My Technology 
                </p>
                <p className={clsx(mutedText, bodyLarge, "text-center")}>
                    Anything about IT that I know 
                </p>
            </div>

            <ListTech
                list_data={data.techstack.language} 
                keyname={"language"}
                title={"Programming language"}
            />
            <ListTech
                list_data={data.techstack.framework} 
                keyname={"framework"}
                title={"Framework and Library"}
            />
            <ListTech
                list_data={data.techstack.database} 
                keyname={"database"}
                title={"Database"}
            />
            <ListTech
                list_data={data.techstack.tools} 
                keyname={"tool"}
                title={"Tools"}
            />
        </FadeInSection>
        
    )
}

const ContactSection = ({ data }) => {
    return(
        <FadeInSection className={clsx(animateSlow,
            " flex flex-col gap-4 lg:px-16"
        )}>
            <div className="mb-4">
                <p className={clsx( sectionTitle, " text-center mb-4")}>
                    Contact me
                </p>
                <p className={clsx(mutedText,bodyLarge, "text-center")}>
                    Leave a message. I'm always here to listen. 
                </p>
            </div>
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
                            url={buildContactURL(item.url)}
                        />
                    );
                })}
            </div>
        </FadeInSection>
    )
}