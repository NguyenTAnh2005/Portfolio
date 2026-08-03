import { useState, useEffect } from "react";
import clsx from "clsx";
// import { motion } from "framer-motion";

import { projectService } from "../../services/project";
import { StatusError, StatusLoading, StatusNoData } from "../../components/FetchStatus";
import { ProjectItem } from "../../components/ProjectItem";
import { GithubStat } from "../../components/GithubStat";
import { Pagination } from "../../components/Pagination";
import FadeInSection from "../../components/FadeInSection";


const baseclass = ' text-light-text bg-light-surface dark:bg-dark-surface dark:text-dark-text ';
const baseTransition = ' transition-all ease-linear duration-500';

const GithubStats = [
    { 
        "src":"https://github-readme-stats.shion.dev/api?username=NguyenTAnh2005&hide_border=false&include_all_commits=false&count_private=false",
        "alt":"github-stat-commit-count"
    },
    { 
        "src":"https://streak-stats.demolab.com/?user=NguyenTAnh2005&hide_border=false",
        "alt":"github-streak-stats"
    },
    { 
        "src":"https://github-readme-stats.shion.dev/api/top-langs/?username=NguyenTAnh2005&hide_border=false&include_all_commits=false&count_private=false&layout=compact",
        "alt":"github-stat-top-lang"
    }
]

export default function Project(){
    const [loadingFirst, setLoadingFirst] = useState(true);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [queryParam, setQueryParam] = useState({
        skip: 0,
        limit: 6,
        sort_by: "id",
        order: "desc"
    });
    

    useEffect(()=>{
        // Cờ báo components còn sống
        let isMounted = true;
        const fetchData = async () => {
            try{
                if (isMounted){
                    const response = await projectService.listProject(queryParam);
                    setData(response.data);
                }
            }
            catch(err){
                if (isMounted){
                    setError(err.message)
                }
            }
            finally{
                if (isMounted){
                    setLoadingFirst(false);
                }
            }
        }
        fetchData();
        
        // Khi tác động làm cho component "chết" thì set false ??? tìm hiểu thêm
        return () =>{
            isMounted = false;
        };
    },[queryParam]);

    let count_page = data ? Math.ceil(data.total/queryParam.limit) : 1;
    let current_page = Math.floor(queryParam.skip/queryParam.limit)+1;

    const handlePageIndexChange = (page_number) =>{
        let new_skip = (page_number - 1 ) * queryParam.limit;
        setQueryParam(prev =>({
            ...prev, skip:new_skip
        }));
    }

    let content;
    if(loadingFirst){content = <StatusLoading/>}
    else if(error!=null){content = <StatusError message={error}/>} 
    else if(!data){content=<StatusNoData/>}
    else content = (
        <div>
            {/* Title Section */}
            <TitleSection/>
            {/* List Project Section */}
            <ListProjectSection data={data}/>
            {/* Pagination */}
            <Pagination
                count_page={count_page}  
                current_page={current_page} 
                onChangeIndexPage={handlePageIndexChange}
            />
            {/* Stat Section */}
            <StatSection list_stats ={GithubStats} />
        </div>
    )
    return (
        <div className={clsx( 'card ', baseTransition, baseclass)}>
            {content}
        </div>
    )


}

const TitleSection = () =>{
    return(
        <FadeInSection className='p-4 '>
            <div className='text-4xl gap-2 lg:text-8xl flex uppercase justify-center font-serif text-center lg:gap-8'>
                <span>My</span>
                <span className='text-primary'> Projects</span>
            </div>
        </FadeInSection>
    )
}

const ListProjectSection = ({data}) =>{
    return(
        <FadeInSection className="py-8 lg:py-16 px-8 lg:px-16">
            <div className={clsx(
                " grid grid-cols-12 gap-6 md:gap-8"
            )}>
                {
                    data.list_data.map((project, index)=>(
                        <ProjectItem 
                            key={`project-${index}`}
                            project={project}
                        />
                    ))
                }
            </div>
        </FadeInSection>
    )
}

const StatSection = ({list_stats}) =>{
    return(
        <FadeInSection className="py-8 lg:py-16 px-8 lg:px-16 flex flex-col gap-4">
            <p className="text-center text-5xl uppercase font-semibold ">
                My github stats
            </p>
            <div className="grid grid-cols-12 gap-6 ">
                { 
                    list_stats.map(item=>(
                        <GithubStat key={item.alt} src={item.src} alt={item.alt} />
                    ))
                }
            </div>
        </FadeInSection>
    )
}