import { PageTitleSection } from "../../components/ui/PageTitleSection";
import { Link } from "react-router-dom";
import { Button } from "../../components/wrapper/Button";
import FadeInSection from "../../components/wrapper/FadeInSection";
import clsx from "clsx";
import { baseBorder } from "../../utils/style";

export const NotFound = ()=>{
    const img_url = "https://res.cloudinary.com/df5mtvzkn/image/upload/v1787728307/Portfolio/Constant/static-avt_fa69rw.jpg";
    return(
        <FadeInSection>
            <PageTitleSection
                title={"Error 404 - Not Found "}
                desc={"We can't found the page with your url. Please check again."}
            />
            <div className="mx-auto max-w-sm mt-8">
                <img className={clsx(baseBorder, "rounded-xl border-2")} src={img_url} alt="static image" loading="lazy" />
            </div>
            <Button style={" w-fit mx-auto px-4 rounded-md py-2 mt-8"}>
                <Link to={"/"} className="text-lg">
                    Go back to Home Page
                </Link>
            </Button>
        </FadeInSection>
    )
}