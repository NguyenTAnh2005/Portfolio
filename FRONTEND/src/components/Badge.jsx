import clsx from "clsx";

const baseclass = ' text-light-text bg-light-surface dark:bg-dark-surface dark:text-dark-text ';
const baseTransition = ' transition-all ease-linear duration-500';

export const InfoBadge = ({icon, content}) =>{
    return(
        <span className={clsx(" px-4 py-1 border-2 flex justify-start w-fit items-center gap-2 rounded-md ",
         "bg-primary/10 dark:bg-primary/5 border-primary/30 dark:border-primary/40")}>
            <span className="text-xl">{icon} </span>
            <span>{content}</span>
        </span>
    )
}
export const TechBadge = ({name, icon:Icon, website, styleClass}) => {
    return (
        <a 
            href={website} 
            target="_blank" 
           title={`Visit ${name} org website!`}
        >
            <div className={clsx(""
                ," flex items-center justify-start gap-2 rounded-lg w-fit min-w-32 border-2 p-2 duration-[250ms] hover:shadow-lg hover:shadow-primary hover:-translate-y-1"
                ,"bg-primary/10 border-primary/30 dark:bg-primary/15 dark:border-primary/40 text-primary "
                )}>
                <span className={clsx("flex justify-center items-center w-10 h-10 rounded-lg font-bold uppercase ", styleClass)}>
                    <Icon size={25} />
                </span>
                <p className={clsx(baseTransition, "text-lg text-light-text dark:text-dark-text")}>
                    {name}
                </p>
            </div>

        </a>
    )
}

export const ContactBadge = ({icon: Icon, name, content, url, styleClass}) => {
    return (
        <a 
            href={url} 
            target="_blank" 
            title={`Contact ${name}!`}
        >
            <div className={clsx(baseTransition
                ," flex items-center justify-start gap-2 rounded-lg w-80 border-2 p-2 duration-[250ms] hover:shadow-lg hover:shadow-primary hover:-translate-y-1"
                ,"bg-primary/10 border-primary/30 dark:bg-primary/15 dark:border-primary/40 text-primary "
                )}>
                <span className={clsx("flex justify-center items-center w-10 h-10 px-2 rounded-lg font-bold uppercase ", styleClass)}>
                    <Icon size={20} />
                </span>
                <p className={clsx(baseTransition, "text-base text-light-text dark:text-dark-text ")}>
                    {content}
                </p>
            </div>

        </a>
    )
}
