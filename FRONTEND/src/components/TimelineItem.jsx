import clsx from "clsx";
import { Check } from 'lucide-react';


import FadeInSection from "./wrapper/FadeInSection";
import { ItemCard } from "./wrapper/ItemCard";
import 
{ 
    baseBorder, mutedText,animateSlow,
    cardTitle, metaLabel, body
} from "../utils/style";
import { Badge } from "./ui/Badge";

export const  TimelineItem = ({data, index}) =>{
    const isEven = index % 2 === 0;
    
    return (
        // Grid tổng, 1fr auto 1fr
        <FadeInSection className={clsx( 
            "grid grid-cols-[auto_1fr] lg:grid-cols-[1fr_auto_1fr] gap-0 md:gap-8 items-center z-10"
        )}>
            {/* Div rỗng độn */}
            <div className={clsx("hidden lg:block ", isEven ? "lg:order-1" : " lg:order-3")}/>

            {/* Icon - luôn ở cột giữa (auto), tuyệt đối center */}
            <div className={clsx(
                animateSlow, "hidden md:inline-block ",
                " p-1 w-fit rounded-full border-2 lg:order-2 ",
                " dark:text-dark-text dark:bg-primary text-primary bg-light-surface  border-primary",
            )}>
                <Check strokeWidth={3} size={28}/>
            </div>

            {/* Content */}
            <ItemCard  styleClass ={clsx(
                "flex flex-col items-center p-4 rounded-lg gap-4 border-2",
                isEven?" lg:order-3":" lg:order-1"
            )}>
                <div className={clsx(
                    "flex w-full gap-4 items-center", 
                    isEven?" lg:justify-start" : "lg:justify-end"
                )}>
                    <img className={clsx(
                        " w-16 h-16 rounded-full", 
                        " lg:h-20 lg:w-20", 
                        !isEven&&" lg:order-last",
                        " border-2 ", baseBorder,
                    )} 
                        src={data.img_url} alt={`Timeline: ${data.title}`} 
                    />
                    <div className={clsx( animateSlow, "flex flex-col gap-4", !isEven&&" lg:items-end")}>
                        <span className={clsx(cardTitle)}> 
                            {data.title}
                        </span>
                        <Badge>
                            <span className={clsx(animateSlow, metaLabel, " px-2 py-1 ")}>
                                {data.start_end}
                            </span>
                        </Badge>

                    </div>
                </div>
                <p className={clsx( body, mutedText, 
                    !isEven&& " lg:text-end"
                )}> 
                    {data.desc}
                </p>
            </ItemCard>
        </FadeInSection>
    )
}
