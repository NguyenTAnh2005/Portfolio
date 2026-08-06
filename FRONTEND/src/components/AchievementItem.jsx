import clsx from 'clsx';
import { CalendarDays } from 'lucide-react';
import { cutStrDate } from '../utils/dateISO';

const baseTransition = ' transition-all ease-linear duration-500';
export const AchivementItem = ({achievement}) =>{
    return(
        <div className={clsx( "duration-200 ", baseTransition,
            "col-span-12 md:col-span-6 lg:col-span-4 border overflow-hidden group",
            " flex flex-col rounded-lg",
            " dark:bg-dark-bg bg-light-bg ",
            " border-light-text/15 dark:border-dark-text/15",
            " hover:shadow-lg hover:shadow-primary"

        )}>
            <img 
                className={clsx( "transition-all duration-200 ease-linear", "rounded-t-lg group-hover:scale-105")}
                src={achievement.img_url} alt={`img - ${achievement.title}`} 
            />
            <div className='flex flex-col p-4 gap-2 flex-1'>
                <p className='text-xl font-bold text-center text-primary'>
                    {achievement.title}
                </p>
                <p className='text-sm text-light-muted dark:text-dark-muted mt-2'>
                    {achievement.desc}
                </p>
                <div className='flex-1'></div>
                <span className={clsx( baseTransition, 
                    "flex gap-2 items-center mt-4 rounded-lg p-2 w-fit border-2 ",
                    " bg-light-surface text-primary border-primary",
                    " dark:bg-primary  dark:text-dark-text"
                )}>
                    <CalendarDays/>
                    <span className='text-sm font-semibold'>
                        {cutStrDate(achievement.achieved_at)}
                    </span>
                </span>
            </div>
        </div>
    )
}