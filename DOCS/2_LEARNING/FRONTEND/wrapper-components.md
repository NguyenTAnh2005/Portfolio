Pattern này lặp lại nhiều thì nên tách ra. Có vài cách, từ đơn giản đến "chuẩn" hơn:

## Cách 1: Tách `variants` ra file riêng (đơn giản, ít thay đổi code nhất)

```javascript
// utils/motionVariants.js
export const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.3 },
  transition: { duration: 0.6 },
};
```

Dùng lại bằng spread:

```javascript
import { fadeInUp } from "@/utils/motionVariants";

<motion.div {...fadeInUp} className="p-4">
  ...
</motion.div>;
```

Giảm từ 5 dòng props xuống còn 1 dòng spread.

## Cách 2: Tạo component `FadeInSection` wrapper (tối ưu nhất, khuyên dùng)

```jsx
// components/FadeInSection.jsx
import { motion } from "framer-motion";

export default function FadeInSection({
  children,
  className = "",
  delay = 0,
  duration = 0.6,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration, delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
```

Chỗ bạn dùng:

```jsx
<FadeInSection className="p-4">
  <div className="text-4xl gap-2 lg:text-8xl flex uppercase justify-center font-serif text-center lg:gap-8">
    <span>My</span>
    <span className="text-primary"> Projects</span>
  </div>
</FadeInSection>
```

Ngắn gọn hơn hẳn, và nếu sau này muốn đổi animation (ví dụ delay, duration, easing) thì chỉ sửa 1 chỗ, toàn bộ project tự cập nhật theo.

## Gợi ý thêm

Nếu bạn có nhiều loại animation khác nhau (fade up, fade left, scale...), có thể mở rộng component thành `Reveal` với prop `variant`:

```jsx
const variantsMap = {
  fadeUp: { initial: { opacity: 0, y: 20 }, whileInView: { opacity: 1, y: 0 } },
  fadeLeft: {
    initial: { opacity: 0, x: -20 },
    whileInView: { opacity: 1, x: 0 },
  },
};

export default function Reveal({
  children,
  className,
  variant = "fadeUp",
  duration = 0.6,
}) {
  const v = variantsMap[variant];
  return (
    <motion.div
      initial={v.initial}
      whileInView={v.whileInView}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
```

Cá nhân mình recommend **Cách 2** cho project của bạn — vừa đủ đơn giản, không over-engineer, mà giải quyết đúng vấn đề copy-paste. Sau này nếu thấy cần nhiều biến thể animation hơn thì mở rộng theo hướng cách 3 cũng chưa muộn.
Được, mình giải thích từ gốc nhé — vì đây là một trong những khái niệm quan trọng nhất của React, hiểu rõ sẽ giúp bạn tự thiết kế được nhiều component khác chứ không chỉ riêng animation.

## 1. `children` — chìa khóa của "wrapper"

React cho mỗi component một prop đặc biệt tên là `children`, chứa **những gì nằm giữa cặp thẻ mở/đóng** khi bạn dùng component đó.

```jsx
<FadeInSection>
  <div>Nội dung của tôi</div>
</FadeInSection>
```

Ở đây, `<div>Nội dung của tôi</div>` chính là `children` mà `FadeInSection` nhận được. Trong component, bạn chỉ cần đặt `{children}` ở nơi muốn nó xuất hiện:

```jsx
function FadeInSection({ children }) {
  return <motion.div>{children}</motion.div>;
}
```

→ Đây gọi là **composition** (kết hợp component): thay vì nhồi tất cả logic vào 1 chỗ, bạn "bọc" nội dung bên ngoài bằng 1 lớp hành vi (ở đây là animation).

## 2. Props — cách "wrapper" nhận tùy chỉnh

Component wrapper thường cần vài tham số để linh hoạt hơn (delay, className...). Bạn destructure chúng ngay trong tham số hàm:

```jsx
function FadeInSection({ children, className = "", delay = 0 }) {
  // className và delay có giá trị mặc định nếu không truyền vào
}
```

Khi dùng:

```jsx
<FadeInSection delay={0.2} className="p-4">
  <p>Xin chào</p>
</FadeInSection>
```

Nếu bạn không truyền `delay`, nó tự lấy `0` (giá trị mặc định) — đây là lý do bạn không bị lỗi khi quên truyền prop.

## 3. Vì sao đây "tối ưu" hơn copy-paste?

Vì bản chất `FadeInSection` chỉ là **một hàm JS trả về JSX**. Bạn gọi hàm đó nhiều lần thay vì viết lại logic nhiều lần — giống hệt việc bạn tách 1 hàm Python/JS ra để tái dùng, chỉ khác là "kết quả" ở đây là giao diện.

## 4. Điểm hay cần biết thêm: Spread props (`...rest`)

Nếu sau này bạn muốn `FadeInSection` nhận **thêm bất kỳ prop nào khác** của `motion.div` mà không cần khai báo hết (ví dụ `onClick`, `style`...), dùng rest spread:

```jsx
function FadeInSection({ children, className = "", delay = 0, ...rest }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.6, delay }}
      className={className}
      {...rest} // các prop khác được "bắn" thẳng vào motion.div
    >
      {children}
    </motion.div>
  );
}
```

`...rest` gom mọi prop chưa được destructure ở trên vào 1 object, rồi bạn "trải" (spread) nó ra lại trên `motion.div`. Đây là pattern rất phổ biến khi viết wrapper component vì nó giữ được sự linh hoạt của component gốc (ở đây là `motion.div`).

## 5. Khi nào nên tạo wrapper?

Quy tắc thực tế (không phải giáo điều): nếu bạn **copy-paste cùng 1 khối JSX/props từ 3 chỗ trở lên**, đó là dấu hiệu nên tách. Ít hơn thì có thể chưa cần, tránh over-engineer sớm.

---

Tóm gọn: wrapper component = một hàm nhận `children` (nội dung bên trong) + `props` (tùy chỉnh) → trả về JSX đã "bọc sẵn" logic dùng chung. Bạn có câu hỏi nào cụ thể hơn về cách nó hoạt động không, hay muốn thử áp dụng luôn vào project của bạn?

## So sánh 2 kiểu truyền dữ liệu vào component

### Kiểu bạn đã biết — `ProjectItem` (data props)

```jsx
<ProjectItem project={project} />
```

Bạn truyền vào một **object dữ liệu** (`project` chứa `title`, `image`, `description`...). Bên trong `ProjectItem`, component tự quyết định **toàn bộ cấu trúc JSX**:

```jsx
function ProjectItem({ project }) {
  return (
    <div>
      <img src={project.image} />
      <h3>{project.title}</h3>
      <p>{project.description}</p>
    </div>
  );
}
```

→ Bạn không được chọn `<img>` đặt ở đâu, `<p>` hiện thế nào — cấu trúc JSX **cố định sẵn bên trong**, bạn chỉ đổi dữ liệu.

### Kiểu wrapper — `FadeInSection` (children props)

```jsx
<FadeInSection>
  <div>Bất kỳ JSX nào bạn muốn</div>
</FadeInSection>
```

Ở đây bạn không truyền dữ liệu để component tự dựng JSX — bạn **truyền thẳng JSX đã dựng sẵn** vào, component chỉ "bọc" thêm hành vi animation xung quanh nó:

```jsx
function FadeInSection({ children }) {
  return <motion.div>{children}</motion.div>; // không biết bên trong là gì, không quan tâm
}
```

→ `FadeInSection` **không biết và không cần biết** bên trong là `ProjectItem`, hay `<h1>`, hay cả một `<form>` phức tạp. Nó chỉ lo mỗi việc: cho cái gì vào thì fade-in cái đó.

## Điểm khác biệt cốt lõi

|                                       | `ProjectItem`                           | `FadeInSection`                                 |
| ------------------------------------- | --------------------------------------- | ----------------------------------------------- |
| Nhận gì                               | **Dữ liệu** (object, string, number...) | **JSX/component khác** (`children`)             |
| Ai quyết định cấu trúc HTML bên trong | Component đó tự quyết                   | Người gọi (nơi dùng nó) tự quyết                |
| Mục đích                              | Hiển thị 1 loại dữ liệu cụ thể          | Thêm hành vi/style cho **bất kỳ nội dung nào**  |
| Ví dụ tương tự                        | `UserCard`, `ProductItem`               | `Modal`, `Tooltip`, `ScrollReveal`, `Container` |

Bạn có thể tưởng tượng `children` giống như một cái **hộp rỗng có sẵn hiệu ứng** (hộp quà có nơ sẵn) — bạn nhét bất cứ thứ gì vào cũng được, còn `ProjectItem` giống một **khuôn đúc cố định** — chỉ đổ đúng loại "nguyên liệu" (dữ liệu project) vào thì mới ra hình đúng.

## Kết hợp cả 2 trong thực tế

Hai kiểu này không loại trừ nhau — bạn hoàn toàn dùng lồng vào nhau:

```jsx
<FadeInSection delay={0.2}>
  <ProjectItem project={project} />
</FadeInSection>
```

`FadeInSection` lo animation, `ProjectItem` lo hiển thị dữ liệu — mỗi component chỉ làm đúng 1 việc. Đây chính là lý do pattern `children` mạnh: nó cho phép bạn **tái dùng animation cho mọi loại nội dung**, kể cả những component bạn chưa viết ra ở thời điểm viết `FadeInSection`.
Được, mình đi từng ví dụ một, giải thích **tại sao bản chất công việc của nó buộc phải dùng `children`** chứ không phải data props.

## Câu hỏi cốt lõi cần tự hỏi trước khi chọn pattern

> "Component này có cần biết **nội dung bên trong là gì** để hoạt động không?"

- Nếu **có** → dùng data props (như `ProjectItem`)
- Nếu **không, nó chỉ làm 1 việc chung (bọc, canh giữa, thêm hiệu ứng...) mà không quan tâm bên trong là gì** → dùng `children` (wrapper)

## Đi qua từng ví dụ

### `Modal` (hộp thoại popup)

Việc của `Modal` là: hiện overlay đen mờ phía sau, canh giữa màn hình, có nút đóng, khóa scroll trang... Nhưng **nội dung bên trong modal** thì thiên biến vạn hóa — có lúc là form đăng nhập, có lúc là ảnh phóng to, có lúc là bảng xác nhận xóa.

```jsx
<Modal isOpen={isOpen} onClose={handleClose}>
    <LoginForm />
</Modal>

// hoặc

<Modal isOpen={isOpen} onClose={handleClose}>
    <img src={bigImage} />
</Modal>
```

Nếu bạn viết `Modal` kiểu data props, bạn sẽ phải làm 1 component `Modal` riêng cho từng loại nội dung (`LoginModal`, `ImageModal`, `ConfirmModal`...) — trùng lặp code cho phần overlay/canh giữa/đóng mở, chỉ khác phần nội dung. Dùng `children` giải quyết đúng vấn đề này.

### `Tooltip` (chú thích khi hover)

Việc của nó: định vị box nhỏ cạnh con trỏ, hiện khi hover, ẩn khi rời chuột. Nhưng **nội dung tooltip** có thể là 1 dòng text, có thể là 1 danh sách, có thể là 1 ảnh preview.

```jsx
<Tooltip content="Click để lưu">
  <button>💾</button>
</Tooltip>
```

Ở đây `children` (`<button>`) là phần tử được hover vào, còn `content` là data prop bình thường cho phần chữ hiện ra. → Thấy không, 1 component có thể **kết hợp cả 2 kiểu cùng lúc** tùy phần nào cần linh hoạt, phần nào cố định.

### `ScrollReveal` / `FadeInSection` (như ví dụ trước)

Việc của nó: theo dõi khi nào phần tử vào viewport rồi chạy animation. Nó hoàn toàn **không quan tâm** phần tử đó là `<h1>`, là card, hay cả 1 section dài. → Buộc phải dùng `children`.

### `Container` (giới hạn max-width, canh giữa trang)

```jsx
function Container({ children }) {
  return <div className="max-w-7xl mx-auto px-4">{children}</div>;
}
```

Việc của nó chỉ là tạo khung layout — trang nào, nội dung gì đặt vào cũng canh giữa và giới hạn chiều rộng như nhau. Không có lý do gì nó cần biết nội dung bên trong.

## Ngược lại — khi nào KHÔNG nên dùng wrapper mà nên dùng data props

Nếu component của bạn **cần biết chi tiết dữ liệu để hiển thị đúng cấu trúc**, ví dụ:

```jsx
function ProjectItem({ project }) {
  // Cần biết project.image ở đâu để đặt <img>, project.tags để render list...
  // Không thể "generic hóa" được vì cấu trúc HTML phụ thuộc vào loại dữ liệu
}
```

`ProjectItem` không thể là wrapper vì nếu bạn truyền `children` vào, bạn vẫn phải tự viết `<img>`, `<h3>`, `<p>` ở **nơi gọi component** — vậy thì tách component ra để làm gì, mất hết lợi ích tái sử dụng cấu trúc hiển thị.

## Quy tắc quyết định nhanh

| Câu hỏi                                                                                                          | Trả lời "có" → dùng                |
| ---------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| Component có logic/behavior chung (animation, positioning, modal, layout...) không phụ thuộc nội dung bên trong? | `children` (wrapper)               |
| Component cần hiển thị 1 cấu trúc cố định dựa trên shape dữ liệu cụ thể?                                         | data props                         |
| Cả hai — có cả phần hành vi chung lẫn phần cần dữ liệu cụ thể?                                                   | Kết hợp cả 2 (như ví dụ `Tooltip`) |

Áp dụng vào đúng case của bạn: `FadeInSection` bọc quanh section "My Projects" — nó không cần biết bên trong là tiêu đề hay là cả list project, nó chỉ lo animation. Đúng chuẩn để dùng `children`.
