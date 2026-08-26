import clsx from "clsx";
import { FaGithub } from "react-icons/fa";

import 
{ 
    baseBorder, mutedText,baseText,
    animateFast, animateSlow,
    cardTitle, body, metaLabel
  
} from "../utils/style";
import { Badge } from "./ui/Badge";
import { ItemCard } from "./wrapper/ItemCard";
const TechTag = ({content}) =>{
    return(
        <Badge>
            <div className={clsx(metaLabel, animateSlow, " px-2 py-1" )}>
                {content}
            </div>
        </Badge>

    )
}

const ViewProject = ({url})=>{
    return(
        <a className={clsx( animateSlow, baseBorder, baseText, 
            " p-2 flex gap-2 items-center justify-center rounded-md border ",
            " hover:dark:bg-light-bg hover:bg-dark-bg",
            " hover:dark:text-light-text hover:text-dark-text"
            )}
            href={url} target="_blank"
        >
            <FaGithub size={20}/>
            <span 
            className="text-xs lg:text-sm font-semibold">
                View in Github
            </span>

        </a>
    )
}

export const ProjectItem = ({project}) =>{
    return(
        <ItemCard  styleClass={clsx(
            " flex flex-col h-full rounded-md group overflow-hidden",
            " border-2 ",
        )}>
            <img className={clsx( animateFast, baseBorder, 
                " border-b-2 group-hover:scale-110 aspect-video object-contain w-full",
                )}
                src={project.img_url} alt={`project-${project.title}`} loading="lazy"
            />
            <div className={clsx(animateSlow, "flex flex-col flex-1 p-4 gap-2")}>
                <span className={clsx(cardTitle, "text-center")}>
                    {project.title}
                </span>
                <p className={clsx( mutedText, body)}>
                    {project.desc}
                </p>
                <div className="flex flex-wrap gap-2 mt-2">
                    {project.list_tech.map(tech=>(
                            <TechTag key={tech} content={tech} />
                        ))
                    }
                    {project.list_lang.map((tech)=>(
                            <TechTag key={tech} content={tech} />
                        ))
                    }
                </div>
                <div className="flex-1"/>
                <div>
                    <ViewProject url={project.project_url}/>
                </div>
            </div>
        </ItemCard>
    )
}

