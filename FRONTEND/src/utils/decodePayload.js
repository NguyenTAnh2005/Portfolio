const decodePayload = (jwt_token)=>{
    // jwt_token hiện tại là header.payload.signature
    let token_parts = jwt_token.split(".");
    // Chuẩn mã hóa của JWT là base64URL
    let payloadBase64URL = token_parts[1];

    // Độn thêm ký tự = để thành bội của 4
    let mod = payloadBase64URL.length%4;
    let paddingCount = mod === 0 ? 0 : 4 - mod;
    
    // Biến đổi ký tự hợp lệ ở base64 và độn ký tự cho chia hết 4
    let payloadBase64 = payloadBase64URL.replace(/-/g, '+').replace(/_/g, '/');
    for(let i = 1; i<=paddingCount; i++){
        payloadBase64+="=";
    }
    

    // Giải mã và chuyển qua JSON object  (window.atob)
    let JSONPayload = JSON.parse(window.atob(payloadBase64));
    // {
    //     "sub":"123@admin.com",
    //     "data":1,
    //     "exp":1788766746
    // }
    return JSONPayload.exp
}

const getExpireTime = (uetTime) =>{
    // uetTime là chuẩn thời gian web token tính bằng giây 
    // Unix Epoch Timestamp (tính bằng giây kể từ ngày 01/01/1970).
    // nhưng JS lại làm việc với mili giây nên cần * 1000 ở đây
    let newDate = new Date(uetTime*1000);
    return newDate.toLocaleString('vi-VN', {
        timeZone: 'Asia/Ho_Chi_Minh',
        hour12: false
        })
}


export const decodeTokenAndGetTimeISO = (jwt_token) =>{
    let uet_time = decodePayload(jwt_token);
    return getExpireTime(uet_time);
}