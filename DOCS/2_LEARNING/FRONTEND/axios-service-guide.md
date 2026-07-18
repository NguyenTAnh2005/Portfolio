## Tài liệu giải thích Axios Service (AXIOS_SERVICE_GUIDE.md)

### 1. 📌 Tổng quan (Overview):

- Phần axiosConfig.js sẽ hỗ trợ việc cài đặt một cấu hình gọi API giúp tránh lặp lại code mỗi khi gọi API
- Các file js còn lại sẽ hỗ trợ đóng gói việc gọi API thành 1 function, mỗi khi các file jsx gọi API thì chỉ cần import service, gọi hàm và truyền param là được.

### 2. 🔌 Cấu hình Axios Instance - [[File Code here](./axiosConfig.js)]

- axios.create dùng để tạo sẫn và cấu hình mặc định một số thuộc tính tránh việc lặp code trong việc gọi API như:
- baseURL: Cấu hình đường dẫn mặc định giúp code gọn hơn, thay vì gõ lặp lại http://localhost.....
- headers: Báo trước cho backend biết cục data bên này gửi là định dạng gì - trong code là định dạng JSON

* Riêng cái API Login thì do bên backend yêu cầu hơi khác nên ta sẽ code dạng headers khác hơn với service này - auth.js.

#### Phổ cập thêm

    - Headers (Vỏ phong bì): Nơi chứa các thông tin mô tả để bưu điện phân loại thư.
    - Content-Type: Báo cho Backend biết ruột thư đang chứa cái gì (JSON, Form chữ, hay File hình ảnh) để Backend biết đường mà dịch.
    - Authorization: Nơi bạn kẹp cái thẻ VIP (Access Token). Bất cứ API nào yêu cầu đăng nhập, Backend sẽ lục cái Header này đầu tiên để kiểm tra thẻ.
    - Body (Ruột thư): Nơi chứa dữ liệu thực tế bạn muốn gửi đi (ví dụ: email, password, thông tin user cần update).
    - Status Code (Dấu mộc phản hồi): Backend đọc thư xong sẽ đóng mộc gửi về.
        + 2xx (200, 201): Xanh chín, thành công.
        + 4xx (400, 401, 403, 404): Lỗi từ phía Frontend (gửi sai định dạng, sai pass, không có Token, hoặc tìm không thấy ID).
        + 5xx (500): Lỗi do Backend code sai bị sập (lúc này bạn phải quay lại mở terminal Backend lên xem lỗi gì).

### 3. 🛡️ Interceptors (Chốt chặn trung gian) - [[File Code here](./axiosConfig.js)]

Đây là thành phần rất quan trọng và thường khó hiểu trong Axios.

- Request Interceptor: Giúp tự động nhét jwt token vào header mỗi khi gọi API thông qua biến token được lưu trên Localstoarge.
- Response Interceptor: Phân tích dữ liệu trả về, dựa vào cái status code, nếu 200 OK thì lấy dữ liệu trong cục res, còn lỗi (401,...) thì sẽ deal thích hợp. (VD: Lỗi token hết hạn thì xóa biến token localstoarge, đá về trang login).

### 4. 🚀 Cách sử dụng (Usage Examples)

Tất cả các hàm gọi API sẽ được viết tập trung tại thư mục `services`. Tại đây, chúng ta sẽ import `axiosInstance` để sử dụng.

**A. GET (Lấy dữ liệu từ Backend về)**
Dùng để lấy danh sách hoặc lấy chi tiết 1 đối tượng.

- **Truyền tham số (Query Params):** Thường dùng để phân trang hoặc lọc dữ liệu.
- **Ví dụ Code:**

```js
import axiosInstance from "./axiosConfig";

export const userService = {
  // Lấy danh sách (Ví dụ URL sẽ thành: /users?page=1&limit=10)
  getAllUsers: async (page, limit) => {
    const response = await axiosInstance.get("/users", {
      params: { page: page, limit: limit },
    });
    return response; // Dữ liệu đã được Interceptor bóc hộp sẵn
  },

  // Lấy chi tiết 1 user theo ID (Truyền ID thẳng vào URL)
  getUserById: async (userId) => {
    const response = await axiosInstance.get(`/users/${userId}`);
    return response;
  },
};
```

**B. POST (Gửi dữ liệu mới lên Backend)**
Dùng khi muốn tạo mới một dòng dữ liệu trong Database (như tạo User mới, tạo Project mới).

- **Gửi Body (JSON):** Axios tự động biến Object của JavaScript thành JSON nhờ cấu hình `Content-Type` mặc định.
- **Ví dụ Code:**

```js
createUser: async (userData) => {
  // userData là một Object: { username: "abc", email: "abc@gmail.com" }
  // Tham số thứ 1 là URL, tham số thứ 2 là Body (Ruột thư)
  const response = await axiosInstance.post("/users", userData);
  return response;
};
```

- **Ngoại lệ (Upload File hoặc Form Data):** Nếu API yêu cầu gửi ảnh hoặc giống như API Login yêu cầu định dạng `x-www-form-urlencoded`, ta phải ghi đè `headers` ngay tại hàm đó (như đã làm ở `authService.js`).

**C. PUT / PATCH (Cập nhật dữ liệu đã có)**
Dùng khi người dùng sửa thông tin cá nhân.

- **Kết hợp cả URL và Body:** Phải chỉ định rõ đang sửa ID nào (trên URL) và nội dung sửa là gì (trong Body).
- **Ví dụ Code:**

```js
updateUser: async (userId, updateData) => {
  const response = await axiosInstance.put(`/user/info/${userId}`, updateData);
  return response;
};
```

**D. DELETE (Xóa dữ liệu)**

- **Truyền ID:** Tương tự như GET chi tiết, chỉ cần ném ID vào đường dẫn.
- **Ví dụ Code:**

```js
deleteUser: async (userId) => {
  const response = await axiosInstance.delete(`/users/${userId}`);
  return response;
};
```

---

### 5. 🛠️ Quy ước xử lý lỗi (Error Handling)

Quy trình báo lỗi của hệ thống chúng ta đi theo 3 bước chặt chẽ: Backend báo lỗi -> Interceptor ném lỗi -> Component bắt lỗi và hiển thị.

**Bước 1: Tại Interceptor (Đã làm ở axiosConfig.js)**
Nhờ lệnh `Promise.reject(error.response?.data || error)`, Interceptor đã bóc sẵn cái hộp lỗi của FastAPI (chứa `success`, `message`, `error_code`) và ném văng ra ngoài.

**Bước 2: Tại Component (Nơi người dùng nhìn thấy)**
Bắt buộc phải dùng cú pháp `try...catch` bọc quanh lệnh gọi API. Tất cả lỗi do Interceptor ném ra sẽ rơi thẳng vào khối `catch`.

**Ví dụ Code cách bắt lỗi:**

```js
const handleUpdate = async () => {
  try {
    // Cố gắng gọi API
    const response = await userService.updateUser(1, { username: "Tuan_Anh" });
    alert(response.message); // In ra chữ "Cập nhật thành công!"
  } catch (error) {
    // Lỗi rớt vào đây! error lúc này chính là cái ruột AppException từ Backend
    console.error("Mã lỗi:", error.error_code);

    // Cập nhật State để in ra màn hình cho người dùng đọc
    setErrorMessage(error.message || "Đã xảy ra lỗi hệ thống!");
  }
};
```
