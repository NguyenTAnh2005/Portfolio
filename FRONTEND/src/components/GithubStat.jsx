export const GithubStat = ({src, alt}) =>{
    return(
        <div className="col-span-12 md:col-span-6 lg:col-span-4 flex items-center justify-center">
            <img 
                className="max-w-md w-full h-auto object-contain" 
                src={src} 
                alt={alt} 
            />
        </div>
    )
}