// Xử lý chuỗi url bên contact sao cho oke nhất
export const buildContactURL = (url) =>{
    if (!url) return "";
    // Bỏ khoẳng trắng thừa nếu cón ở 2 bên chuỗi.
    let cleanedUrl = url.trim();
    // Xử lý email có chứa @.
    if(cleanedUrl.includes("@")){
        return `mailto:${url}`
    }
    // Xử lý chuỗi SDT có chứa 0 ở đầu.
    if(cleanedUrl.startsWith("0")){
        let phone = url.slice(1);
        return `tel:+84${phone}`
    }
    return cleanedUrl
};