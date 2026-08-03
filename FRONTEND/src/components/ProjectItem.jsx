import clsx from "clsx";
import { FaGithub } from "react-icons/fa";

const baseTransition = ' transition-all ease-linear duration-500';

const TechTag = ({content}) =>{
    return(
        <span 
            className={clsx( baseTransition,
                " text-xs lg:text-sm flex justify-center items-center border p-1  rounded-md ",
                " border-primary/30 dark:border-primary/40",
                " text-primary bg-primary/10 dark:bg-primary/15"
            )}
        >
            {content}
        </span>
    )
}

export const ProjectItem = ({project}) =>{
    return(
        <div className={clsx( 
            " col-span-12 md:col-span-6 lg:col-span-4 flex flex-col h-full",
            " transition-all ease-linear duration-200",
            "  rounded-xl border-2 shadow-lg",
            " bg-light-bg dark:bg-dark-bg",
            " border-primary/30 dark:border-primary/40",
            " hover:shadow-primary"
        )}>
            <img 
                className={clsx(
                    "rounded-t-xl ",
                )}
                src={project.img_url} alt={`project-${project.title}`} 
            />
            <div className="flex flex-col flex-1 p-4 gap-2">
                <span className="text-xl font-bold text-center">
                    {project.title}
                </span>
                <p className=" text-sm lg:text-base text-light-muted dark:text-dark-muted indent-8 ">
                    {project.desc}
                </p>
                <div className="flex flex-1 flex-wrap gap-2 mt-2">
                    {project.list_tech.map(tech=>(
                            <TechTag key={tech} content={tech} />
                        ))
                    }
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                    {project.list_lang.map(tech=>(
                            <TechTag key={tech} content={tech} />
                        ))
                    }
                </div>
                <div className="flex-1">

                </div>
                <a 
                    className={clsx( baseTransition,
                        " w-fit p-2 flex gap-2 items-center justify-center rounded-md mx-auto border ",
                        "border-primary/30 dark:border-primary/40",
                        " text-light-text dark:text-dark-text ",
                        " hover:dark:bg-light-bg hover:bg-dark-bg",
                        " hover:dark:text-light-text hover:text-dark-text"
                    )}
                    href={project.project_url} target="_blank"
                >
                    <FaGithub size={24}/>
                    <span 
                    className="text-sm font-semibold">
                        View Project in Github
                    </span>

                </a>
            </div>
            
        </div>
    )
}
