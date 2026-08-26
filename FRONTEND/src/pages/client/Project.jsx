import { useState, useEffect } from "react";
import clsx from "clsx";

import { projectService } from "../../services/project";
import { StatusError, StatusLoading, StatusNoData } from "../../components/ui/FetchStatus";
import { Pagination } from "../../components/ui/Pagination";
import { ProjectItem } from "../../components/ProjectItem";
import { GithubStat } from "../../components/GithubStat";
import FadeInSection from "../../components/wrapper/FadeInSection";
import { PageTitleSection } from "../../components/ui/PageTitleSection";

import { GithubStats } from "../../constants/projectConfig";
import 
{ 
    baseTextBg, animateSlow, sectionTitle
} from "../../utils/style";


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
        window.scroll(0, 0);
    }

    let content;
    if(loadingFirst){content = <StatusLoading/>}
    else if(error!=null){content = <StatusError message={error}/>} 
    else if(!data){content=<StatusNoData/>}
    else content = (
        <div className="flex flex-col gap-16">
            {/* Title Section */}
            <PageTitleSection
                title={"My Projects"}
                desc={"Through hands-on project work, I keep learning and growing in both Backend and Frontend."}
            />

            <div className="flex flex-col gap-8">
                {/* List Project Section */}
                <ListProjectSection data={data}/>
                {/* Pagination */}
                <Pagination
                    count_page={count_page}  
                    current_page={current_page} 
                    onChangeIndexPage={handlePageIndexChange}
                />
            </div>
            
            {/* Stat Section */}
            <StatSection list_stats ={GithubStats} />
        </div>
    )
    return (
        <div className={clsx( baseTextBg, animateSlow)}>
            {content}
        </div>
    )
}
const ListProjectSection = ({data}) =>{
    return(
        <FadeInSection>
            <div className={clsx(
                " grid grid-cols-12 "
            )}>
                <div className="col-span-12 lg:col-span-10 lg:col-start-2 grid grid-cols-12 gap-8">
                    {data.list_data.map((project)=>(
                            <div className="col-span-12 sm:col-span-6 xl:col-span-4" 
                                key={`project-${project.id}`}
                            >
                                    <ProjectItem    
                                        project={project}
                                    />
                            </div>
                        ))
                    }
                </div>
            </div>
        </FadeInSection>
    )
}

const StatSection = ({list_stats}) =>{
    return(
        <FadeInSection className="flex flex-col gap-4">
            <p className={clsx( sectionTitle, "text-center uppercase")}>
                My github stats
            </p>
            <div className="grid grid-cols-12 mt-4">
                <div className="col-span-12 lg:col-span-10 lg:col-start-2 grid grid-cols-12 gap-8">
                    {list_stats.map(item=>(
                            <div className="col-span-12 sm:col-span-6 xl:col-span-4" key={item.alt}>
                                <GithubStat src={item.src} alt={item.alt} /> 
                            </div>
                        ))
                    }
                </div>
            </div>
        </FadeInSection>
    )
}