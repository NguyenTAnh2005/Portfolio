import { useState, useEffect } from "react";
import clsx from "clsx";

import { achieveService } from "../../services/achievement";

import {StatusLoading, StatusNoData, StatusError} from "../../components/ui/FetchStatus";
import { PageTitleSection } from "../../components/ui/PageTitleSection";
import { AchivementItem } from "../../components/AchievementItem";
import FadeInSection from "../../components/wrapper/FadeInSection";
import { Pagination } from "../../components/ui/Pagination";
import { baseTextBg, animateSlow} from "../../utils/style";

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
        let new_skip = (page_number-1) * queryParam.limit;
        setqueryParam(prev => ({
            ...prev, skip: new_skip
        }));
        window.scroll(0, 0);
    }

    let content;
    if(loading){content = <StatusLoading/>}
    else if(error!=null){content = <StatusError message={error}/>} 
    else if(!data){content=<StatusNoData/>}
    else content = (
        <div className="flex flex-col gap-16">
            {/* Title Section */}
            <PageTitleSection
                title={"My Achievements"}
                desc={"My college journey: A collection of achievements and certificates. Tracking my personal growth every day."}
            />
            <div className="flex flex-col gap-8">
                {/* List Achievement */}
                <ListAchievement data={data} />
                {/* PAGINATION */}
                <Pagination
                    count_page={count_page} 
                    current_page={current_page}
                    onChangeIndexPage={handlePageIndexChange}
                />
            </div>
        </div>
    )
    return (
        <div className={clsx(baseTextBg, animateSlow)}>
            {content}
        </div>
    )
}

const ListAchievement = ({data}) =>{
    return(
        <FadeInSection className={clsx( " grid grid-cols-12")}>
            <div className="col-span-12 lg:col-span-10 lg:col-start-2 grid grid-cols-12 gap-8">
                {data.list_data.map((item) =>(
                    <div className="col-span-12 md:col-span-6 lg:col-span-4" key={`achievement-${item.id}`}>
                        <AchivementItem achievement={item} />
                    </div>
                    ))
                }
            </div>
        </FadeInSection>
    )
}