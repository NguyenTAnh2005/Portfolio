## 1. Khái niệm cơ bản cần biết

Chỉ cần 3 thứ:

- **`motion.div`** (hoặc `motion.span`,...) thay cho `div` thường — để nó có thể animate.
- **`initial`** / **`animate`**: trạng thái bắt đầu và trạng thái kết thúc (dùng cho load-trang).
- **`whileInView`** + **`viewport`**: animate khi phần tử lướt vào khung nhìn (dùng cho scroll-reveal).

## 2. Fade up khi load trang (áp dụng cho `HeroSection`)

```jsx
<motion.div
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, ease: "easeOut" }}
    className={clsx(...)}
>
    ...
</motion.div>
```

- `initial`: trước khi render xong → mờ (opacity 0) và lệch xuống 30px (y: 30).
- `animate`: chạy ngay khi mount → hiện rõ, về đúng vị trí.
- `transition`: kiểm soát tốc độ/kiểu chuyển động.

Muốn các badge trong Hero xuất hiện **lần lượt** (stagger) thay vì cùng lúc, dùng `staggerChildren`:

```jsx
const container = {
    hidden: {},
    show: {
        transition: { staggerChildren: 0.15 }
    }
};
const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.5 } }
};

// Div cha
<motion.div variants={container} initial="hidden" animate="show" className="flex ...">
    {badge_list.map(item => (
        <motion.div key={...} variants={item}>
            <InfoBadge ... />
        </motion.div>
    ))}
</motion.div>
```

## 3. Fade up khi lướt tới (áp dụng cho `TechListSection`, `ContactSection`)

Đổi `animate` thành `whileInView`:

```jsx
<motion.div
    initial={{ opacity: 0, y: 40 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, amount: 0.2 }}
    transition={{ duration: 0.6, ease: "easeOut" }}
    className={clsx(...)}
>
    ...
</motion.div>
```

Giải thích `viewport`:

- `once: true` → chỉ chạy animation 1 lần (rất nên dùng, không thì cuộn lên cuộn xuống nó chạy lại hoài, rối mắt).
- `amount: 0.2` → chỉ cần 20% phần tử lọt vào khung nhìn là kích hoạt (giá trị từ 0 đến 1).

## 4. Áp vào cấu trúc hiện tại của bạn

Với 4 section (`Hero`, `Bio`, `TechList`, `Contact`), cách đơn giản nhất và đủ đẹp:

- `HeroSection`: dùng `initial` + `animate` (chạy ngay khi trang load, vì nó luôn nằm trên đầu, không cần chờ scroll).
- `BioSection`, `TechListSection`, `ContactSection`: dùng `initial` + `whileInView` (vì nằm dưới, cần cuộn tới mới thấy).

Ví dụ sửa `BioSection`:

```jsx
const BioSection = ({ data }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.6 }}
      className={clsx(baseTransition, " col-span-12 text-3xl py-16 px-8 ")}
    >
      <p className="italic font-serif text-center max-w-lg mx-auto">
        "{data.bio}."
      </p>
    </motion.div>
  );
};
```

Làm tương tự cho `TechListSection` và `ContactSection` (đổi thẻ `div` ngoài cùng thành `motion.div`, thêm 4 prop trên).

## Vài lưu ý nhỏ

- **Không lồng quá nhiều `motion.div` animate riêng lẻ** trong cùng 1 section nếu không cần thiết — dễ bị rối và tốn hiệu năng. Ưu tiên animate ở cấp section, chỉ dùng stagger khi thực sự muốn hiệu ứng "từng cái một" như bạn nói ban đầu.
- **`amount`** nên để nhỏ (0.1–0.3) cho section cao, để nó chạy sớm hơn một chút, cảm giác mượt hơn là chờ cuộn hết cả section mới chạy.
- Bạn không cần học sâu, chỉ với `initial` / `animate` / `whileInView` / `viewport` / `transition` là đủ dùng cho 90% các trường hợp fade-up thông thường như thế này.
