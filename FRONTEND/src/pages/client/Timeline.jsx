import clsx from 'clsx';
import {StatusLoading, StatusError, StatusNoData} from '../../components/ui/FetchStatus';
import { useState, useEffect } from "react";
import {TimelineService} from "../../services/timeline";
import { GraduationCap } from 'lucide-react';
import 
{ 
    baseBackground, baseTextBg, 
    animateSlow,
    sectionTitle, bodyLarge,
} from '../../utils/style';
import { Badge } from '../../components/ui/Badge';

import { TimelineItem } from '../../components/TimelineItem';
import FadeInSection from '../../components/wrapper/FadeInSection';
import { PageTitleSection } from '../../components/ui/PageTitleSection';

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
        <div className='flex flex-col gap-16'>
            {/* Title */}
            <PageTitleSection
                title={"My Journey"}
                desc={"From beginning to now. My journey of learning, growing, and chasing my software engineering dream."}
            />
            {/* List Timeline */}
            <ListTimelineSection data={data} />
            {/* Abstract Section */}
            <AbstractSection/>
        </div>
    )
    return (
        <div className={clsx(baseTextBg, animateSlow)}>
            {content}
        </div>
    )
}
const ListTimelineSection = ({data}) =>{
    return(
        <div className={clsx("relative flex flex-col gap-8")} >
            <div className='hidden md:inline-block absolute top-0 bottom-0 bg-primary/30 dark:bg-primary/40 w-1 rounded-full z-5 left-4 lg:left-1/2 lg:-translate-x-1/2'></div>
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
        <FadeInSection className={clsx( animateSlow, baseBackground, "py-4 rounded-xl")}>
            <div className='flex flex-col gap-8'>
                <div className='flex justify-center'>
                    <Badge>
                        <div className='p-4'>
                            <GraduationCap size={48}/>
                        </div>
                    </Badge>
                </div>


                <p className={clsx(sectionTitle, "text-center")}>
                    The Journey still there
                </p>
                <div className={clsx(bodyLarge, " italic mx-auto indent-6 max-w-5xl")}>
                    " I was a shy kid with average grades. I felt hopeless about my English score in the final high school exam. I had never used a laptop before.
                    Then in university, I learned to be more confident. I worked hard to improve my English and learn to code.
                    <br />
                    <br />
                    <span className='text-primary'> Now,</span> I want to become a <span className='text-primary font-bold'> software engineer</span> one day. I will keep trying to achieve that. "
                </div>
            </div>
            <div className='flex flex-col items-center gap-4 md:flex-row justify-center md:gap-8 mt-8'>
                {listTag.map((item, index)=>(
                    <Badge key={`major-tag-${index}`}>
                        <div className={clsx(bodyLarge, " font-mono w-fit px-4 py-2")} >
                            {item.content}
                        </div>
                    </Badge>
                    ))
                }
            </div>
        </FadeInSection>
    )
}