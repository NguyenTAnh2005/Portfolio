import clsx from "clsx";

import { ChevronRight } from 'lucide-react';
import { ChevronLeft } from 'lucide-react';


export const Pagination = ({current_page, count_page, onChangeIndexPage}) =>{
    let list_page_index = []
    list_page_index.push(<PagePrev key={`page-index-prev`} current_page={current_page} onChangeIndexPage={onChangeIndexPage}/>)
    for (let i = 1; i<count_page+1; i++){
        list_page_index.push(
            <PageIndex 
                key={`page-index-${i}`} page_num={i} 
                current_page={current_page} 
                onChangeIndexPage={onChangeIndexPage}
            />
        )
    }
    list_page_index.push(<PageNext key={`page-index-next`} current_page={current_page} count_page={count_page} onChangeIndexPage={onChangeIndexPage}/>)

    return (
        <div className="flex gap-2 justify-center">
            {list_page_index}
        </div>
    )
}

const PageIndex = ({current_page, page_num, onChangeIndexPage}) =>{
    // console.log(current_page);
    return(
        <span
            className={clsx(
                "flex justify-center items-center px-4 py-2 rounded-md bg-primary/15 cursor-pointer",
                page_num == current_page && " text-primary border border-primary "
            )}
            onClick={()=>{onChangeIndexPage(page_num)}} 
        >
            {page_num}
        </span>
    )
}

const PagePrev = ({current_page, onChangeIndexPage}) =>{
    const handleChangePrev = () =>{
        if (current_page >1){
            onChangeIndexPage(current_page-1);
        }
    }
    return(
        <span
            className={clsx(
                "flex justify-center items-center px-4 py-2 rounded-md bg-primary/15 cursor-pointer",
            )}
            onClick={handleChangePrev} 
        >
            <ChevronLeft/>
        </span>
    )
}

const PageNext = ({current_page, count_page, onChangeIndexPage}) =>{
    const handleChangeNext = () =>{
        if (current_page < count_page){
            onChangeIndexPage(current_page + 1);
        }
    }
    return(
        <span
            className={clsx(
                "flex justify-center items-center px-4 py-2 rounded-md bg-primary/15 cursor-pointer",
            )}
            onClick={handleChangeNext} 
        >
            <ChevronRight/>
        </span>
    )
}