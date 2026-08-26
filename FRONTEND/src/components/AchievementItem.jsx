import clsx from 'clsx';
import { CalendarDays } from 'lucide-react';
import { cutStrDate } from '../utils/dateISO';

import { Badge } from './ui/Badge';
import 
{ 
    animateFast, mutedText,
    cardTitle, metaLabel, body
} from '../utils/style';
import { ItemCard } from './wrapper/ItemCard';

export const AchivementItem = ({achievement}) =>{
    return(
        <ItemCard styleClass={clsx(
        " flex flex-col rounded-lg overflow-hidden group h-full",
        " border-2 "
        )}>
            <img 
                className={clsx( animateFast, " group-hover:scale-110", " aspect-video object-contain w-full")}
                src={achievement.img_url} alt={`img - ${achievement.title}`} loading='lazy'
            />
            <div className='flex flex-col p-4 gap-4 flex-1'>
                <p className={clsx(cardTitle, 'text-center text-primary')}>
                    {achievement.title}
                </p>
                <p className={clsx(body, mutedText)}>
                    {achievement.desc}
                </p>
                <div className='flex-1'></div>
                <Badge>
                    <span className={clsx( metaLabel, 
                        " flex gap-2 items-center p-2 w-fit ",
                    )}>
                        <CalendarDays size={20}/>
                        <span>
                            {cutStrDate(achievement.achieved_at)}
                        </span>
                    </span>
                </Badge>
            </div>
        </ItemCard>
    )
}