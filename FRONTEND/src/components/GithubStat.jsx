export const GithubStat = ({src, alt}) =>{
    return(
        <div className=" flex items-center justify-center">
            <img 
                className="max-w-md w-full h-auto object-contain" 
                src={src} 
                alt={alt} 
            />
        </div>
    )
}