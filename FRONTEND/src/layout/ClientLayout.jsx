import { Outlet, Link, useLocation } from "react-router-dom";
import ThemeToggle from "../components/ThemeToggle";
import { AnimatePresence, motion } from "framer-motion";
import { Menu, X } from "lucide-react";
import { useState, useEffect } from "react";
import clsx from "clsx";

const baseclass = ' text-light-text bg-light-surface dark:bg-dark-surface dark:text-dark-text ';
const baseTransition = ' transition-all ease-linear duration-500 ';

function ClientLayout(){
    return (
        <div className="relative flex flex-col">
            <Header/>
            <div className={clsx(baseTransition, baseclass, "  py-4")}>
                <Outlet/>
            </div>
            <Footer/>
        </div>
    )
}

const Header = () =>{
    const location = useLocation();
    const [expand, setExpand] = useState(false);
    const changeModeExpand = () =>{
        setExpand(prev => !prev);
    };
    useEffect(()=>{
        setExpand(false);
    },[location.pathname])
    const NavItems = [
        {"link":"/", "content": "Home"},
        {"link":"/about-me", "content": "About Me"},
        {"link":"/timeline", "content": "Timeline"},
        {"link":"/project", "content": "Project"},
        {"link":"/achievement", "content": "Achievement"},
    ]
    return (
        <>
            <div className = {clsx(baseTransition, "text-light-text bg-light-bg dark:bg-dark-bg dark:text-dark-text", "sticky top-0 flex items-center justify-between px-4 md:px-8 lg:px-12 py-4 shadow-md z-50" )}>
                <div className="flex justify-center items-center gap-2">
                    <span className="text-xl btn-primary">
                        A
                    </span>
                    <span className="text-2xl font-semibold">
                            Portfolio
                    </span>
                </div>
                <div className=" hidden gap-4 lg:flex lg:justify-center">
                    {NavItems.map(item =>(
                        <NavItem
                            location={location}
                            content={item.content} 
                            linkTo={item.link} 
                            key={`nav-item-${item.link}`}
                        />
                    ))}
                </div>
                <div className="flex items-center gap-4">
                    <ThemeToggle/>
                    <div className="btn-primary p-2 lg:hidden transition-all duration-500 ease-in-out" onClick={changeModeExpand}>
                        {/* Hiệu ứng tham khảo AI */}
                        {!expand ? (
                            <motion.div
                                key="menu"
                                initial={{ opacity: 0, rotate: -90 }}
                                animate={{ opacity: 1, rotate: 0 }}
                                exit={{ opacity: 0, rotate: 90 }}
                                transition={{ duration: 0.2 }}
                            >
                                <Menu/>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="close"
                                initial={{ opacity: 0, rotate: 90 }}
                                animate={{ opacity: 1, rotate: 0 }}
                                exit={{ opacity: 0, rotate: -90 }}
                                transition={{ duration: 0.2 }}
                            >
                                <X />
                            </motion.div>
                        )}
                        
                    </div>
                </div>
            </div>
            <div className="sticky top-24 right-0 ">
            <AnimatePresence>
                {expand&&(
                    <motion.div 
                        initial={{opacity:0, y:0}} 
                        animate={{opacity:1, y:0}}
                        // Giúp menu trượt lên + mờ dần
                        exit={{opacity:0, y:-20}}
                        transition={{duration:0.5, ease:"easeInOut"}}
                        className=" absolute top-0 right-[2.5%] w-[95%] flex flex-col gap-4 items-start p-4 bg-light-bg dark:bg-dark-bg lg:hidden z-40 card">
                        {NavItems.map(item =>(
                            <NavItem
                                location={location}
                                content={item.content} 
                                linkTo={item.link} 
                                key={`nav-item-${item.link}`}
                            />
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
            </div>
        </>            


    )
};

const NavItem = ({linkTo, content, location}) =>{
    // Sử dụng useLocation để lấy đầy đủ đường dẫn hiện tại 
    
    let isActive = false;

    // Nếu link đang là index page thì buộc đường dẫn hiện tại phải khớp "/"
    if(linkTo === "/"){
        isActive = location.pathname === "/";
    }
    // Nếu link khác với index thì chỉ cần pathname start với link đó (VD: /about-me/....)
    else{
        isActive = location.pathname.startsWith(linkTo);
    }

    return(
        <Link to = {linkTo}
        className= {`relative px-2 py-1 cursor-pointer transition-colors duration-300
            ${
                isActive 
                ? ' text-primary font-semibold'
                : " text-light-muted dark:text-dark-muted hover:text-primary-hover"
            }
        `}
        >
            <span className='relative z-10 text-base lg:text-xl'>
                {content}
            </span>

            {
                isActive && (
                    // CODE THAM KHẢO AI 
                    <motion.div
                        layoutId=" navbar-magic-line" // Cần thiết để chuyển động mượt từ link này sang link kia 
                        className='absolute bottom-0 left-2 right-2 h-[2px] bg-primary rounded-sm'
                        // Cấu hình độ nảy của hiệu ứng (càng stiffness cao càng nhanh, damping là lực cản)
                        transition={{ type: "spring", stiffness: 550, damping: 50 }}
                    />
                )
            }
        </Link>
    )
}

function Footer(){
    return(
        <div id="FOOTER" className={`bg-dark-bg text-light-muted  text-sm
                                     py-12`}>
            {/* Nửa trên chứa các cục thông tin */}
            <div className={`flex flex-col gap-12 px-6 lg:flex-row lg:justify-between lg:px-12`}>
                {/* Cột 1: Thương hiệu */}
                <div className="flex flex-col gap-3 lg:max-w-sm">
                    <h2 className="text-dark-text tracking-tight 
                                    font-bold text-3xl">
                        Nguyen Tuan Anh
                    </h2>
                    <h4 className="text-base font-medium">
                        🏫 Binh Duong University - Software Engineer 🖥💻
                    </h4>
                    <p className="leading-relaxed">
                        I may have less experience, but I have a limitless drive to learn.
                    </p>
                </div>
                {/*Cột 2: Quick Links  */}
                <div className="flex flex-col gap-3">
                    <h2 className="text-dark-text 
                                    text-lg font-semibold mb-2">
                        Quicklink
                    </h2>
                    <QuickLinkItem content={"About me"} link={"/about-me"} />
                    <QuickLinkItem content={"Projects"} link={"/project"} />
                    <QuickLinkItem content={"Timelines"} link={"/timeline"} />
                    <QuickLinkItem content={"Achievements"} link={"/achievement"} />
                </div>
                {/*Cột 3: Contact */}
                <div className="flex flex-col gap-3">
                    <h2 className="text-dark-text 
                                    text-lg font-semibold mb-2">
                        Contact Me
                    </h2>
                    <QuickLinkItem content={"23050118@bdu.edu.vn"} />
                    <QuickLinkItem content={"+84 328884320"} />
                    <QuickLinkItem content={"More contact info"} link={"/about-me"} />
                </div>
            </div>

            {/* Nửa dưới chứa thông tin bản quyền */}
            <div className="flex flex-col items-center gap-8 mt-12">
                <hr className="w-[95%] border-[1/2px] border-light-muted  dark:border-dark-muted" />
                <p className="text-base">
                    © 2026 Nguyen Tuan Anh. All rights reserved.
                </p>
            </div>

        </div>

    )
}

function QuickLinkItem({content, link = ""}){
    
    return(
        <>
        {
            link == ""?(
            <span
                className="hover:text-primary-hover transition-all duration-300 ease-linear"
            >
                {content}
            </span>
            ):(
            <Link
                to = {link}
                className="hover:text-primary-hover transition-all duration-300 ease-linear"
            >
                {content}
            </Link>
            )
        }
        </>
    )
}


export default ClientLayout;