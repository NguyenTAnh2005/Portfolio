// Funct hỗ trợ xử lý khi gọi API endpoint cần nhận MultiPart thay vì JSON 
// -> parse class Pydantic thông thường.
// Funct nhận vào là 1 object từ biến useState
export const buildFormData = (data) =>{
// Do multipart nên các thành phần sẽ được gửi từ data của input từng field 
// nên nếu như không thay đổi (ko nhập) - sẽ gửi "" hay null nên nhiệm vụ Func 
// này là phát hiện có những trường nào có dấu hiệu trên sẽ loại bỏ, ko gửi 
// đi gọi API tránh ghi đè dữ liệu. 
// Dù bên backend có làm ntn rồi nhưng việc bảo mật 2 lớp FE BE là không bao giờ thừa 

// 1. Tạo mới Object FormData
    const formData = new FormData();    
    for (const key in data){
        const value = data[key];
        if (value !== undefined && value !== null){
            formData.append(key, value)
        }
    } 
    return formData;
}