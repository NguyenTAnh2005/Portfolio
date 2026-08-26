import clsx from "clsx";
import { Clock, Wrench } from "lucide-react";
import { LuGithub } from "react-icons/lu";
import { IoMailOutline } from "react-icons/io5";
import FadeInSection from "../components/wrapper/FadeInSection";
import { baseBorder } from "../utils/style";
const Contact = ({Icon, link, content}) =>{
    return (
        <a className="flex items-center justify-center gap-2 text-primary font-semibold" href={link}>
            <Icon size={24} />
            {content}
        </a>
    )
}
export const Maintenance = () =>{
    const img_url = "https://res.cloudinary.com/df5mtvzkn/image/upload/v1787728307/Portfolio/Constant/static-avt_fa69rw.jpg";
    return(
        <div className=" fixed flex top-0 left-0 items-center justify-center w-screen h-screen bg-black/80 z-5">
            <FadeInSection className="flex flex-col w-full max-w-md justify-center gap-4 items-center z-10 text-dark-text px-4">
                <span className="bg-primary-hover/40 w-fit p-3 rounded-xl text-primary ">
                    <Wrench strokeWidth={2} size={32}/>
                </span>
                <h1 className="text-4xl font-semibold">
                    We'll be back soon
                </h1>
                <p className="text-center text-dark-muted">
                    We are updating our website. Thanks for your patience. We will be back soon!
                </p>
                <div className="mx-auto max-w-sm mt-8">
                    <img className={clsx(baseBorder, "rounded-xl border-2")} src={img_url} alt="static image" loading="lazy" />
                </div>
                <div className="flex gap-2 bg-black/50 w-full py-2 justify-center items-center rounded-lg mt-8">
                    <Clock size={18} strokeWidth={3}/>
                    <span>
                        Back in a few hours
                    </span>
                </div>
                <div className=" flex gap-4">
                    <Contact
                        Icon={IoMailOutline}
                        link={"mailto:23050118@student.bdu.edu.vn"}
                        content={"Email me"}
                    />
                    <span className="text-dark-muted">|</span>
                    <Contact
                        Icon={LuGithub}
                        link={"https://github.com/NguyenTAnh2005"}
                        content={"Github"}
                    />
                </div>
            </FadeInSection>
        </div>
    )
}