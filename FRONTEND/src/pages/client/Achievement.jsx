import { useState, useEffect } from "react";
import clsx from "clsx";

import { achieveService } from "../../services/achievement";

import {StatusLoading, StatusNoData, StatusError} from "../../components/FetchStatus";
import { AchivementItem } from "../../components/AchievementItem";
import FadeInSection from "../../components/FadeInSection";
import { Pagination } from "../../components/Pagination";

const baseclass = ' text-light-text bg-light-surface dark:bg-dark-surface dark:text-dark-text ';
const baseTransition = ' transition-all ease-linear duration-500';

export default function Achievement(){
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [queryParam, setqueryParam] = useState({
        skip: 0,
        limit: 6,
        sort_by:"id",
        order:"asc",
    });

    useEffect(()=>{
        let isMounted = true;
        const fetchData = async ()=>{
            try {
                if (isMounted){
                    const response = await achieveService.list_achieve(queryParam);
                    setData(response.data);
                }
            } 
            catch (err) {
                if (isMounted){
                    console.error(`Lỗi: ${err}`);
                    setError(err.message);
                }
            }
            finally{
                if (isMounted){
                    setLoading(false);
                }
            }
        }
        fetchData();
        return ()=>{
            isMounted = false;
        };
    },[queryParam]);
    const current_page = Math.floor(queryParam.skip/queryParam.limit) + 1;
    const count_page = data ? Math.ceil(data.total / queryParam.limit) : 1;

    const handlePageIndexChange = (page_number) =>{
        let new_skip = (page_number-1) * page_number;
        setqueryParam(prev => ({
            ...prev, skip: new_skip
        }));
    }

    let content;
    if(loading){content = <StatusLoading/>}
    else if(error!=null){content = <StatusError message={error}/>} 
    else if(!data){content=<StatusNoData/>}
    else content = (
        <div>
            {/* Title Section */}
            <TitleSection/>
            {/* List Achievement */}
            <ListAchievement data={data} />
            {/* PAGINATION */}
            <div className="p-4">
                <Pagination
                    count_page={count_page} 
                    current_page={current_page}
                    onChangeIndexPage={handlePageIndexChange}
                />
            </div>


        </div>
    )
    return (
        <div className={clsx('card ',baseclass, baseTransition)}>
            {content}
        </div>
    )
}

const ListAchievement = ({data}) =>{
    return(
        <FadeInSection className={clsx(
            " grid grid-cols-12 gap-6 lg:gap-12 p-8"
        )}>
            {
                data.list_data.map((item) =>(
                    <AchivementItem achievement={item} key={`achievement-${item.id}`}/>
                ))
            }
        </FadeInSection>
    )
}


const TitleSection = () =>{
    return(
        <FadeInSection>
            <div className='text-4xl gap-2 lg:text-8xl flex uppercase justify-center font-serif text-center lg:gap-8'>
                <span>my</span>
                <span className='text-primary'> achievements</span>
            </div>
            <p className={clsx(
                "text-light-muted dark:text-dark-muted mt-4",
                ' text-base text-center font-serif lg:text-3xl mx-auto indent-6 max-w-5xl '
            )}>
                 My college journey: A collection of achievements and certificates. Tracking my personal growth every day.
            </p>
        </FadeInSection>
    )
}