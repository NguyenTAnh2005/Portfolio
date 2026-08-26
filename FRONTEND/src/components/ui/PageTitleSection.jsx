import clsx from "clsx";
import { display, mutedText, bodyLarge } from "../../utils/style";
import FadeInSection from "../wrapper/FadeInSection";

export const PageTitleSection = ({title, desc}) =>{
    return(
        <FadeInSection>
            <p className={clsx(display, "text-primary text-center uppercase text-wrap")}>
                {title}
            </p>
            <p className={clsx( mutedText, bodyLarge,
                ' text-center mx-auto mt-4 max-w-5xl '
            )}>
                {desc}
            </p>
        </FadeInSection>
    )
}
