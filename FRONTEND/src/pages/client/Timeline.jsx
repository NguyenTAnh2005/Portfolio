import {StatusLoading, StatusError, StatusNoData} from '../../components/FetchStatus';
import { useState, useEffect } from "react";
import {TimelineService} from "../../services/timeline";
// import { motion } from 'framer-motion';

import clsx from 'clsx';
import { TimelineItem } from '../../components/TimelineItem';
import FadeInSection from '../../components/FadeInSection';

const baseclass = ' text-light-text bg-light-surface dark:bg-dark-surface dark:text-dark-text ';
const baseTransition = ' transition-all ease-linear duration-500';

const listTag = [
    {content:"🎨 Frontend Developer",},
    {content:"⚙️ Backend Developer"},
    // {content:""}
]

export default function Timeline(){
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [queryParam, setQueryparam] = useState({
        skip: 0,
        limit: 30,
        sort_by: "id",
        order: "asc"
    });

    useEffect(()=>{
        let isMounted = true;
        const fetchData = async()=>{
            try
            {
                if (isMounted){
                    const response = await TimelineService.getAll(queryParam);
                    setData(response.data);
                }
            }
            catch(err){
                if (isMounted){
                    console.error("Lỗi: ", err);
                    setError(err.message);
                }
            }
            finally{
                if (isMounted){setLoading(false);}
            }
        };
        fetchData();
        return ()=>{
            isMounted = false;
        };
    },[queryParam]);

    let content;
    if(loading){content = <StatusLoading/>}
    else if(error!=null){content = <StatusError message={error}/>} 
    else if(!data){content=<StatusNoData/>}
    else content = (
        <div>
            {/* Title */}
            <TitleSection/>
            {/* List Timeline */}
            <ListTimelineSection data={data} />
            {/* Abstract Section */}
            <AbstractSection/>
        </div>
    )
    return (
        <div className={clsx('card ',baseclass, baseTransition)}>
            {content}
        </div>
    )
}

const TitleSection = () =>{
    return(
        <FadeInSection>
            <div className='text-4xl gap-2 lg:text-8xl flex uppercase justify-center font-serif text-center lg:gap-8'>
                <span>my</span>
                <span className='text-primary'> journey</span>
            </div>
            <p className={clsx(
                "text-light-muted dark:text-dark-muted ",
                ' text-base text-center font-serif lg:text-3xl mx-auto indent-6 max-w-5xl '
            )}>
                From beginning to now. My journey of learning, growing, and chasing my software engineering dream.
            </p>
        </FadeInSection>
    )
}

const ListTimelineSection = ({data}) =>{
    return(
        <div className={clsx("relative flex flex-col gap-16 mt-16")} >
            <div className='absolute top-0 bottom-0 bg-primary/30 dark:bg-primary/40 w-1 rounded-full z-5 left-5 lg:left-1/2 lg:-translate-x-1/2'></div>
            {
                data.list_data.map((item, index)=>(
                    <TimelineItem data={item} index={index} key={`timeline_item_${item.sort_order}`}/>
                ))
            }
        </div>
    )
}

const AbstractSection = () =>{
    return(
        <FadeInSection className='p-4 mt-16'>
            <div className='flex flex-col gap-8'>
                <div className='bg-primary/10 dark:bg-primary/15 text-2xl lg:text-6xl w-fit mx-auto rounded-xl p-4'>
                    🌱
                </div>
                <p className='text-center text-2xl lg:text-6xl font-serif'>
                    The Journey still there
                </p>
                <div className={clsx(' text-base lg:text-3xl font-serif italic mx-auto indent-6 max-w-5xl ')}>
                    " I was a shy kid with average grades. I felt hopeless about my English score in the final high school exam. I had never used a laptop before.
                    Then in university, I learned to be more confident. I worked hard to improve my English and learn to code.
                    <br />
                    <br />
                    <span className='text-primary'> Now,</span> I want to become a <span className='text-primary font-bold'> software engineer</span> one day. I will keep trying to achieve that. "
                </div>
            </div>
            <div className='flex justify-center gap-8 mt-8'>
                {listTag.map((item, index)=>(
                        <div className="tech-tag text-base lg:text-2xl " key={`major-tag-${index}`}>
                            {item.content}
                        </div>
                    ))
                }
            </div>
        </FadeInSection>
    )
}