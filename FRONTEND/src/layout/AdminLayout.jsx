import { Outlet, Link, useLocation, useNavigate } from "react-router-dom";
import clsx from "clsx";
import ThemeToggle from "../components/ui/ThemeToggle";
import { Menu, MoveLeft, LayoutDashboard, Info, AlarmClock, Folder, Trophy, UserKey, MonitorCog, LogOut } from "lucide-react";
import { useState, useEffect } from "react";
import { authService } from "../services/auth";
import { cuttingString } from "../utils/string";
import { decodeTokenAndGetTimeISO } from "../utils/decodePayload";
import { Badge } from "../components/ui/Badge";

import { useAuth } from "../contexts/AuthContext";

const baseclass = 'bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text  transition-all ease-linear duration-500';

function AdminLayout(){
    return (
        <div className=" relative flex">
            <AdminNavBar />
            <div className={`bg-light-surface dark:bg-dark-surface flex-1 min-h-screen overflow-y-auto`}>
                <Outlet/>
            </div>
        </div>
    )
}

const AdminNavBar = () =>{
    const {logout, accessToken} = useAuth();
    const navigate = useNavigate();
    const [showLogoutModal, setShowLogoutModal] = useState(false);

    const location = useLocation();
    const [isOpen, setIsOpen] = useState(false);
    const toggleNav = () => setIsOpen(prev => !prev);

    const [loading, setLoading] = useState(false);
    const [currentInfo, setCurrentInfo] = useState(null);

    useEffect(()=>{
        const fetchInfo = async () =>{
            try{
                setLoading(true);
                const response = await authService.getMe();
                setCurrentInfo(response.data);
                console.log("Dữ liệu Admin:", response.data);
            }
            catch (error){console.error("Lỗi: ", error);}
            finally{setLoading(false)}
        }
        fetchInfo();
        console.log(currentInfo);
    },[]);

    const confirmLogout = () =>{
        logout();
        setShowLogoutModal(false);
        navigate("/log-in")
    };

    const adminNavItems = [
        {"content": "Dash Board", "link": "/admin", "Icon": LayoutDashboard},
        {"content": "Infomation", "link": "/admin/manage-info", "Icon": Info},
        {"content": "Timelines", "link": "/admin/manage-timelines", "Icon": AlarmClock},
        {"content": "Projects", "link": "/admin/manage-projects", "Icon": Folder},
        {"content": "Achievements", "link": "/admin/manage-achieves", "Icon": Trophy},
        {"content": "Role - User", "link": "/admin/manage-roleuser", "Icon": UserKey},
        {"content": "Sys Config", "link": "/admin/manage-config", "Icon": MonitorCog}
    ];
    return(
        <>
            {isOpen && 
                ( <div className=" fixed inset-0 bg-black/50 z-30 lg:hidden" onClick={toggleNav}/>)
            }
            <button onClick={toggleNav} className={clsx( "fixed top-6 left-2 z-50 lg:hidden",
            "bg-primary text-white p-2 rounded-full", "flex justify-center items-center shadow-md")}>
                {isOpen ? <MoveLeft size={20}/> : <Menu size={20}/> }
            </button>
            <nav className = {clsx(baseclass, "flex flex-col card rounded-none h-screen gap-4 w-64 shrink-0 overflow-y-auto",
                 "fixed top-0 left-0 z-40 transition-all duration-500",
                 isOpen? "translate-x-0" : "-translate-x-full",
                 "lg:static lg:translate-x-0"
            )}>
                <div className="flex items-center justify-end gap-4 border-b pb-2 border-gray-300 dark:border-gray-700">
                    <span className="text-lg font-bold tracking-tight">Portfolio Admin</span>
                    <ThemeToggle/>
                </div>
                {
                    adminNavItems.map(item =>(
                        <NavItem
                            key={`admin-nav-${item.link}`}
                            location={location}
                            link={item.link}
                            content={item.content}
                            Icon={item.Icon}
                        />
                    ))

                }
                <div className="flex-1">
                    <span>
                        Hạn của token hiện tại:
                    </span>
                    <br></br>
                    <Badge>
                        <span>
                            {decodeTokenAndGetTimeISO(accessToken)}
                        </span>
                    </Badge>

                </div>
                {
                    loading? <div className="text-xs text-center p-2">Đang tải...</div>
                    : <CurrentAdminInfo prop_data={currentInfo}/>
                }
                <Logout onClick={()=>setShowLogoutModal(true)}/>
            </nav>
                {
                    showLogoutModal&&(
                        <LogoutModal 
                            onCancel={()=>setShowLogoutModal(false)}
                            onConfirm={confirmLogout}
                        />
                    )
                }
        </>
    )};

const NavItem = ({link, content, Icon, location}) =>{
    let isActive = false;
    if(link === "/admin"){
        isActive = location.pathname === "/admin";
    }
    else{
        isActive = location.pathname.startsWith(link);
    }
    return(
        <div className="flex">
            <Link  
                to={link}
                className = {clsx( "flex justify-start gap-2 p-2 w-full rounded-md ", "text-light-text dark:text-dark-text ",
                    isActive && "bg-primary text-white")}
            >
                <Icon />
                <span className="">
                    {content}
                </span>
            </Link>
        </div>
    )};

const CurrentAdminInfo = ({prop_data}) =>{
    if (!prop_data) return null;

    return(
        <>
            <div className="flex items-center justify-start gap-2 p-2 rounded-lg border-2 border-dashed 
                             transition-all ease-in-out duration-500
                             border-primary/40 bg-primary/10
                             dark:border-primary/30 dark:bg-primary/15">
                <span className="text-white bg-primary text-xl flex justify-center items-center w-12 h-12 rounded-full uppercase">
                    {cuttingString(prop_data.username)}
                </span>
                <div className="flex flex-col text-xs">
                    <span className="font-semibold text-base ">
                        {prop_data.username}
                        </span>
                    <span className="italic text-light-muted dark:text-dark-muted">
                        {prop_data.email}
                    </span>
                </div>
            </div>
        </>
    )};

const Logout = ({onClick}) =>{
    return(
            <div className="btn-primary flex justify-center gap-2 cursor-pointer" onClick={onClick}>
                <LogOut/>
                <span>
                    Log Out
                </span>
            </div>
    )};

const LogoutModal = ({onConfirm, onCancel}) =>{
    return(
        <div onClick={onCancel} className="fixed flex top-0 left-0 items-center justify-center w-screen h-screen inset-0 bg-black/50 z-50">
            <div className=" card flex flex-col text-center w-96 font-bold">
                <p className="text-xl uppercase mb-6">Attention</p>
                <p className="mb-12">Are you sure to log out?</p>
                <div className="flex justify-center gap-8 ">
                    <button 
                        className="px-5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 font-medium" 
                        onClick={onCancel}
                    >
                        Cancel
                    </button>
                    <button className="btn-primary" onClick={onConfirm}>Log Out</button>
                </div>
            </div>
        </div>
    )
}

export default AdminLayout;