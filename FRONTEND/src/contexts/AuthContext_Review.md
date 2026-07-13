# Tài liệu kỹ thuật: Core Authentication Context (AuthContext.jsx)

Tài liệu này giải phẫu chi tiết cơ chế hoạt động của module `AuthContext.jsx` trong kiến trúc React, giải thích lý do tại sao các pattern cụ thể lại được áp dụng dưới góc độ hiệu năng và thiết kế hệ thống.

---

## 1. Bản chất của Context API (`createContext`)

```javascript
const AuthContext = createContext();
```

- **Vấn đề giải quyết:** Trong React, dữ liệu mặc định chảy theo một chiều từ cha xuống con thông qua `props`. Đối với các state toàn cục (global state) như thông tin đăng nhập, việc truyền `props` qua hàng chục tầng component trung gian tạo ra vấn đề **Prop Drilling** (khoan nhồi props), làm code rườm rà và khó bảo trì.
- **Cơ chế hoạt động:** `createContext()` khởi tạo một đối tượng Context. Đối tượng này chứa hai thành phần cốt lõi của React là `Provider` (Nguồn cung cấp) và `Consumer` (Nguồn tiêu thụ). Nó mở ra một "đường hầm" (tunnel) trong Virtual DOM, cho phép dữ liệu đi thẳng từ component Root đến bất kỳ component con nào mà không cần đi qua các node trung gian.

---

## 2. Component Composition và `children` Prop

```javascript
export const AuthProvider = ({ children }) => { ... }

```

- **Định nghĩa kỹ thuật:** `children` là một prop mặc định (built-in prop) trong mọi React Component. Nó chứa cấu trúc cây Virtual DOM (các React Elements) được lồng bên trong thẻ mở và thẻ đóng của component cha.
- **Ứng dụng (Component Composition):** Bằng cách nhận `children` và render `<AuthContext.Provider>{children}</AuthContext.Provider>`, `AuthProvider` hoạt động như một Wrapper Component. Nó bọc toàn bộ App tree lại, cho phép bất kỳ component nào nằm trong `children` đều có quyền truy xuất vào vùng nhớ của Context.

---

## 3. Tối ưu I/O với Lazy State Initialization (Khởi tạo State lười biếng)

```javascript
const [token, setToken] = useState(() => localStorage.getItem("jwt-token"));
```

- **Cơ chế Re-render của React:** Mỗi khi state thay đổi, component sẽ bị re-render (gọi lại toàn bộ hàm functional component).
- **Nút thắt cổ chai (Bottleneck):** Đọc dữ liệu từ `localStorage` là một thao tác I/O đồng bộ (Synchronous I/O). Nếu viết `useState(localStorage.getItem('jwt-token'))`, thao tác block main-thread này sẽ bị thực thi lặp đi lặp lại một cách vô nghĩa trong mỗi chu kỳ re-render, gây suy giảm hiệu năng (Performance degradation).
- **Giải pháp:** Bằng cách truyền vào một callback function `() => ...`, React áp dụng cơ chế **Lazy Initialization**. Callback này được đảm bảo chỉ được invoke (gọi) duy nhất một lần trong pha khởi tạo đầu tiên (Initial Mount Phase). Ở các lần re-render tiếp theo, React sẽ hoàn toàn bỏ qua callback này và sử dụng cached state trên RAM.

---

## 4. Quản lý Side Effects và State Updates

```javascript
const login = (newToken) => {
  setToken(newToken);
  localStorage.setItem("jwt-token", newToken);
};
```

- **Tính nhất quán của dữ liệu (Data Consistency):** Hàm `login` và `logout` chịu trách nhiệm đồng bộ hóa state trên RAM (React State) và bộ nhớ vật lý của trình duyệt (`localStorage`).
- **Kích hoạt chu kỳ Render:** Khi `setToken` được gọi, React đưa component `AuthProvider` vào hàng đợi (queue) để re-render. Quá trình này sẽ tính toán lại object `value` và ép tất cả các components đang subscribe (đăng ký) vào `AuthContext` cập nhật lại UI với dữ liệu mới.

---

## 5. Type Coercion (Ép kiểu dữ liệu)

```javascript
isAuthenticated: !!token,

```

- **Lý do áp dụng:** Biến `token` hiện tại mang kiểu dữ liệu `String` hoặc `null`. Nhiều cơ chế bảo vệ điều hướng (như `ProtectedRoute`) đòi hỏi việc đánh giá logic phải dựa trên kiểu `Boolean` nguyên thủy (Primitive Boolean) để tránh các side-effect không mong muốn do truthy/falsy evaluation gây ra.
- **Toán tử Not kép (`!!`):** \* Dấu `!` thứ nhất ép kiểu biến thành `Boolean` và đảo ngược giá trị logic (ví dụ: `null` thành `true`).
- Dấu `!` thứ hai đảo ngược kết quả lần nữa để trả về giá trị logic gốc (thành `false`).
- Đây là pattern ép kiểu nhanh và an toàn nhất với chi phí tính toán O(1).

---

## 6. Đóng gói Logic với Custom Hook (`useAuth`)

```javascript
export const useAuth = () => {
  return useContext(AuthContext);
};
```

- **Design Pattern (Encapsulation - Tính đóng gói):** Thay vì bắt các component tiêu thụ (Consumers) phải import cả hàm `useContext` của thư viện React và biến `AuthContext`, ta đóng gói chúng lại vào một Custom Hook duy nhất.

**Tại sao phải đẻ thêm cái hàm này?**
Giả sử ở trang `Login.jsx` bạn muốn lấy hàm `login` ra dùng. Nếu không có dòng này, bạn sẽ phải làm 2 việc cực kỳ phiền phức:

1. `import { useContext } from 'react'`
2. `import { AuthContext } from './contexts/AuthContext'`
3. Viết code: `const { login } = useContext(AuthContext);`

Để file nào cũng phải import 2 thứ như vậy thì quá mệt mỏi. Nên bạn tạo sẵn cái hàm `useAuth` này làm phím tắt. Từ nay ở bất kỳ đâu, bạn chỉ cần gõ đúng 1 dòng:
`const { login } = useAuth();`

- **Lợi ích:** \* Giảm boilerplate code ở phía Consumer.
- Ẩn giấu chi tiết triển khai bên trong. Sau này nếu logic Auth thay đổi (ví dụ chuyển sang dùng Redux hay Zustand), ta chỉ cần sửa ở file này, các file UI bên ngoài (`Login.jsx`, `Dashboard.jsx`) đang dùng hàm `useAuth()` không cần phải đụng đến một dòng code nào.
