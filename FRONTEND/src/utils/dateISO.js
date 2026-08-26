// Biến đổi chuỗi datetime ISO sang chuỗi bình thường date cho UI hiển thị bằng cách xử lý chuỗi. 
export const cutStrDate = (dateISO) =>{
    let dateOnly = dateISO.split('T')[0];
    return dateOnly;
}