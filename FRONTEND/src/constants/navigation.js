
//  CLIENT LAYOUT 
// Các nav điều hướng
export const ListNavItems = [
    {"link":"/", "content": "Home"},
    {"link":"/about-me", "content": "About me"},
    {"link":"/timeline", "content": "Timeline"},
    {"link":"/project", "content": "Project"},
    {"link":"/achievement", "content": "Achievement"},
]
// Các quick link ở Footer
export const ListQuickLinks = [
    {"content":"About me", "link":"/about-me"},
    {"content": "Timeline", "link":"/timeline"},
    {"content": "Project", "link":"/project"},
    {"content": "Achievement", "link":"/achievement"},
]
export const ListContacts = [
    {"content":"23050118@bdu.edu.vn", "link":""},
    {"content": "+84328884320", "link":""},
    {"content": "More contact info", "link":"/about-me"},
]

import { FaGithub, FaFacebook, FaInstagram, FaPhone, FaEnvelope } from "react-icons/fa";
// INDEX
export const  DICT_CONFIG_CONTACT = {
    phone: {icon: FaPhone}, 
    github: {icon: FaGithub}, 
    email1: {icon: FaEnvelope}, 
    email2: {icon: FaEnvelope}, 
    facebook: {icon: FaFacebook}, 
    instagram: {icon: FaInstagram}
}
