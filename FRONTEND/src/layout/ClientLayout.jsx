import { Outlet, Link, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { useState, useEffect } from "react";
import clsx from "clsx";
import { Menu, X } from "lucide-react";
import { Button } from "../components/wrapper/Button";

import {useSystemConfig} from "../contexts/SystemConfigContext";
import { ListNavItems, ListQuickLinks, ListContacts } from "../constants/navigation";
import ThemeToggle from "../components/ui/ThemeToggle";
import 
{ 
    baseTextBg, animateSlow, animateFast, bgSurface, baseText

} from "../utils/style";

const pageSpaceX = ' px-4 md:px-8 lg:px-12 ';
const pageSpacing = `${pageSpaceX} py-16`;
const pageWidth = ' max-w-7xl mx-auto ';

export const ClientLayout=()=>{
    const {resumeURL} = useSystemConfig();
    const location = useLocation();
    
    // Tự động cuộn lên đầu trang 
    useEffect(()=>{
        window.scroll(0, 0);
    },[location]);

    return (
        <div className="relative ">
            {/* HEADER */}
            <div className={clsx( animateSlow, bgSurface, baseText,
                pageSpaceX, "py-4 ",
                "  shadow-lg sticky top-0 right-0 z-50"
            )}>
                <Header NavItems={ListNavItems} location={location}/>
            </div>
            <div className={clsx( 
                animateSlow,  pageSpacing, baseTextBg
            )}>
                <Outlet/>
            </div>
            <div className={clsx( pageSpaceX, "py-4", animateSlow, 
                " bg-dark-surface text-light-muted"
            )}>
                <Footer resumeURL={resumeURL} listContacts={ListContacts} listQuickLinks={ListQuickLinks}/>
            </div>
        </div>
    )
}

const Header = ({NavItems, location}) =>{
    const [expand, setExpand] = useState(false);
    const changeModeExpand = () =>{
        setExpand(prev => !prev);
    };
    useEffect(()=>{
        setExpand(false);
    },[location.pathname]);

    return (
        <>
            {/* Header ngang */}
            <div className = {clsx( animateSlow, pageWidth,
                    " flex items-center justify-between" 
            )}>
                <Link to={"/"} className="flex justify-center items-center gap-2">
                    <span className="text-xl bg-primary text-dark-text px-4 py-2 rounded-md">
                        A
                    </span>
                    <span className="text-2xl font-semibold">
                            Portfolio
                    </span>
                </Link>
                <div className=" hidden gap-4 md:flex md:justify-center">
                    {NavItems.map(item =>(
                        <NavItem location={location} content={item.content} 
                            linkTo={item.link}  key={`nav-item-${item.link}`}
                        />
                    ))}
                </div>
                <div className="flex items-center gap-4">
                    <ThemeToggle/>
                    <div className="btn-primary p-2 md:hidden transition-all duration-500 ease-in-out" onClick={changeModeExpand}>
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
            {/* Header dọc ẩn hiện */}
            <AnimatePresence>
                {expand&&(
                    <motion.div 
                        initial={{opacity:0, y:0}} 
                        animate={{opacity:1, y:0}}
                        // Giúp menu trượt lên + mờ dần
                        exit={{opacity:0, y:-20}}
                        transition={{duration:0.5, ease:"easeInOut"}}
                        className=" absolute top-full right-[2.5%] w-[95%] flex flex-col gap-4 items-start p-4 bg-light-bg dark:bg-dark-bg md:hidden z-40 card">
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
        className = {clsx(
            "relative px-2 py-1 cursor-pointer transition-colors duration-300",
            isActive ? " text-primary font-semibold":"text-light-muted dark:text-dark-muted "
        )}>
            <span className={clsx(animateFast,
                "relative z-10 text-base lg:text-xl hover:text-primary-hover")}>
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
};

const Footer=({resumeURL, listQuickLinks, listContacts})=>{
    const groupFlex = " flex flex-col gap-3 "
    return(
        <div className={clsx(pageWidth, " grid grid-cols-12 text-sm")}>
            {/* Thương hiệu */}
            <div className={clsx(" col-span-12 md:col-span-7", groupFlex )}>
                <h2 className="text-dark-text tracking-tight font-bold text-3xl">
                    Nguyen Tuan Anh
                </h2>
                <h4 className="text-base font-medium">
                    🏫 Binh Duong University - Software Engineer 🖥💻
                </h4>
                <p className="leading-relaxed">
                    I may have less experience, but I have a limitless drive to learn.
                </p>
            </div>
            {/* Quick Links  */}
            <div className={clsx("col-span-12 md:col-span-2 ", groupFlex )}>
                <h2 className="text-dark-text text-lg font-semibold mb-2">
                    Quicklink
                </h2>
                {listQuickLinks.map((item)=>(
                    <QuickLinkItem key={`quick-link-${item.content}`} content={item.content} link = {item.link} />
                ))}
            </div>

            {/* Contact */}
            <div className={clsx("col-span-12 md:col-span-3 ", groupFlex )}>
                <h2 className="text-dark-text text-lg font-semibold mb-2">
                    Contact Me
                </h2>
                {listContacts.map((item)=>(
                    <QuickLinkItem key={`quick-link-${item.content}`} content={item.content} link = {item.link} />
                ))}
            </div>

            {/* Thông tin bản quyền */}
            <div className="col-span-12 flex flex-col items-center gap-8 mt-12">
                <hr className="w-full border border-dark-muted" />
                <p className="text-base">
                    © 2026 Nguyen Tuan Anh. All rights reserved.
                </p>
            </div>
            {/* Nút link đến Cv PDF */}
            <div className="col-span-12 flex justify-end mt-6 px-8">
                <Button style={"rounded-md px-4 py-2"}>
                    <a href={resumeURL} className={clsx( "rounded-md text-lg w-fit cursor-pointer")}>
                        View My CV
                    </a>
                </Button>

            </div>
        </div>

    )
};

const QuickLinkItem = ({content, link = ""})=>{
    return(
        <Link to = {link} className="hover:text-primary-hover transition-all duration-300 ease-linear">
            {content}
        </Link>
    )
};

export default ClientLayout;