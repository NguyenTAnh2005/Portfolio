import clsx from "clsx";

import {
    baseBorder, baseText, baseBackground,
    animateFast, animateSlow,
    bgSurface,
    hoverShadow
} from "../../utils/style";


export const InfoBadge = ({icon, keyName, content}) => {
    const isContact = keyName === "contact";
    const className = clsx(animateSlow, isContact && "cursor-pointer",
        "px-4 py-2 w-60 border-2 flex justify-start items-center gap-2 rounded-md",
        baseBackground, baseBorder
    );

    if (isContact) {
        return (
            <a href="#contact" className={className}>
                <span className="text-xl">{icon} </span>
                <span>{content}</span>
            </a>
        );
    }

    return (
        <div className={className}>
            <span className="text-xl">{icon} </span>
            <span>{content}</span>
        </div>
    );
}

export const ContactBadge = ({icon: Icon, name, content, url, styleClass}) => {
    return (
        <a 
            href={url} 
            target="_blank"
            rel="noopener noreferrer" 
            title={`Contact ${name}!`}
        >
            <div className={clsx(animateFast, baseText, hoverShadow, 
                " flex items-center justify-start gap-2 rounded-md w-80 border-2 p-2 hover:scale-95",
                baseBorder, bgSurface
            )}>
                <span className={clsx("flex justify-center items-center w-10 h-10 px-2 rounded-full font-bold uppercase ", styleClass)}>
                    <Icon size={20} />
                </span>
                <p className="">
                    {content}
                </p>
            </div>

        </a>
    )
}

export const Badge = ({children, styleClass}) =>{
    return(
        <span className={clsx(
            styleClass, animateFast,
            "bg-primary/20 text-primary dark:bg-primary/10 font-semibold rounded-md w-fit"
        )}>
            {children}
        </span>
    )
}
