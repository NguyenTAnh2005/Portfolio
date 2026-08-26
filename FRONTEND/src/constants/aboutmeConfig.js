import { FaGithub, FaFacebook, FaInstagram, FaPhone, FaEnvelope } from "react-icons/fa";

// Danh sách các Liên hệ 
export const CONTACT_CONFIG = {
    phone:   { icon: FaPhone, content:"+84 328884320",     styleClass: "bg-green-500 text-white" },
    github:  { icon: FaGithub, content:"NguyenTAnh2005",   styleClass: "bg-[#181717] text-white" },
    email1:  { icon: FaEnvelope, content:"23050118@student.bdu.edu.vn", styleClass: "bg-red-500 text-white" },
    email2:  { icon: FaEnvelope, content:"anhnguyentaun@gmail.com", styleClass: "bg-red-500 text-white" },
    facebook:{ icon: FaFacebook, content:"tuan.anh.514281", styleClass: "bg-[#1877F2] text-white" },
    instagram:{ icon: FaInstagram, content:"tanh_2005_",styleClass: "bg-gradient-to-tr from-[#f9ce34] via-[#ee2a7b] to-[#6228d7] text-white" },
};