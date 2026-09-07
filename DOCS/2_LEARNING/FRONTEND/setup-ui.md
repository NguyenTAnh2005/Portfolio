# `🎯 Note về  Frontend Style & Design System`

> Tài liệu tham khảo về cách tổ chức cấu trúc cho hệ thống UI frontend."

---

## 1. Nguyên tắc tổ chức Style — 3 tầng

Nhiều người mới học Tailwind hay bị rối vì không phân biệt "style nên nằm ở đâu". Có 3 tầng, mỗi tầng vai trò khác nhau:

| Tầng                    | Vị trí               | Vai trò                               | Đặc điểm                                   |
| ----------------------- | -------------------- | ------------------------------------- | ------------------------------------------ |
| **1. Design Tokens**    | `tailwind.config.js` | Nguyên liệu thô: màu, spacing, font   | Giá trị tuyệt đối, không đổi theo ngữ cảnh |
| **2. Style Primitives** | `utils/style.js`     | Tổ hợp class tĩnh, dùng lại nhiều nơi | KHÔNG có props, KHÔNG bọc children         |
| **3. Components**       | `components/`        | UI có logic, biến thể, bọc nội dung   | CÓ props/variant, CÓ children              |

**Quy tắc quyết định nhanh — trả lời 2 câu hỏi:**

1. Style này có thay đổi theo prop/context không? (VD: badge có contact thì là `<a>`, không thì là `<div>`)
2. Style này có bọc nội dung con (children) không?

→ Nếu **có 1 trong 2** → phải là **Component** (Tầng 3).
→ Nếu **không cái nào** → chỉ là **Style Primitive** (Tầng 2), để trong `style.js` là đủ.

**Dấu hiệu Tầng 2 đang bị lẫn Tầng 3** (cần dọn lại):

- Một khái niệm UI (badge, section title, card...) vừa có string trong `style.js`, vừa có component riêng → 2 nguồn sự thật, dễ lệch nhau khi sửa 1 chỗ quên chỗ kia.
- Một string trong `style.js` chứa cỡ chữ/heading lặp lại ở nhiều page (`sectionTitle`) → bản chất đó là 1 UI pattern có thể cần mở rộng sau (thêm icon, đổi theo breakpoint) → nên là component.

---

## 2. Design Tokens — Màu sắc

Ví dụ:

```js
primary: {
  DEFAULT: '#D98C2B',   // ember — accent chính, dùng tiết chế
  hover:   '#B8701C'
},
light: {
  bg:      '#FAF7F1',   // nền tổng thể
  surface: '#FFFCF6',   // nền card/box
  text:    '#24211D',   // chữ chính
  muted:   '#7A7369'    // chữ phụ — cùng họ ấm với text
},
dark: {
  bg:      '#14181C',
  surface: '#1C2126',
  text:    '#F4F1EA',
  muted:   '#9C9686'
}
```

### Sử dụng bảng màu hợp lý

| Token       | Dùng cho                                                                     |
| ----------- | ---------------------------------------------------------------------------- |
| `primary`   | CTA chính (nút "View CV"), active state (nav underline), tech tag, icon nhấn |
| `*.text`    | Chữ nội dung chính, heading                                                  |
| `*.muted`   | Mô tả phụ, ngày tháng, label thứ yếu                                         |
| `*.surface` | Nền Card, Navbar, block nổi lên khỏi `bg`                                    |
| `*.bg`      | Nền tổng thể trang                                                           |

**Lưu ý dùng `primary`:** chỉ 1 accent cho cả trang. Nếu sau này cần thêm màu semantic (success/error cho form validation chẳng hạn) — đó là bộ token khác, không lấy `primary` làm luôn màu lỗi.

---

## 3. Typography — Hệ thống chữ

### 3.1 Chọn bao nhiêu font, vì sao

Nguyên tắc: **tối đa 2 typeface cho 1 trang**, mỗi typeface có **vai trò rõ ràng**, không chọn vì "nhìn đẹp".

| Vai trò          | Font               | Dùng cho                             | Lý do                                                                                             |
| ---------------- | ------------------ | ------------------------------------ | ------------------------------------------------------------------------------------------------- |
| UI / Body        | **Inter**          | Heading, đoạn văn, nút, nav          | Dễ đọc, trung tính, đã quen dùng — giữ nguyên                                                     |
| Meta / Technical | **JetBrains Mono** | Tech tag, ngày tháng, label hệ thống | Nội dung đó thực chất mang tính "dữ liệu/code" — dùng monospace là có lý do, không phải trang trí |

Không thêm font thứ 3 (VD: 1 font display "đẹp" riêng cho hero) trừ khi có lý do cụ thể — thêm font là thêm 1 request mạng + 1 rủi ro không đồng bộ nhịp điệu trang.

### 3.2 Cách load font — tránh lỗi hiệu năng thường gặp

Người mới hay mắc lỗi: import cả family (`Inter:wght@100..900`) trong khi chỉ dùng 2-3 weight → tải dư không cần thiết.

**Chỉ import đúng các weight thực sự dùng.** Với hệ thống weight ở mục 3.4 (400/500/700), URL Google Fonts nên là:

```
family=Inter:wght@400;500;700
family=JetBrains+Mono:wght@400;500
```

thay vì dải `100..900` như hiện tại trong `index.css`. Giảm dung lượng tải font đáng kể mà không mất gì.

`display=swap` (đã có sẵn trong import hiện tại) — giữ nguyên, đây là thực hành đúng: cho phép trình duyệt hiện chữ bằng font hệ thống trước, thay bằng Inter khi tải xong, tránh trang trắng chờ font.

### 3.3 Type Scale — cỡ chữ theo cấp độ

Không nên tự ý chọn `text-5xl` hay `text-3xl` theo cảm tính mỗi page — cần 1 thang cố định, dùng xuyên suốt:

```js
// ============ TYPE SCALE (5 bậc + 1 biến thể) ============

// BẬC 1 - DISPLAY: Chữ to nhất toàn site.
// Dùng cho: Tiêu đề chính của TỪNG TRANG (Hero text ở Home, tiêu đề "Về tôi", "Dự án", "Timeline"...)
// Vị trí: Luôn là dòng chữ đầu tiên, to nhất khi vừa vào 1 trang/section lớn nhất.
export const display = " text-4xl md:text-6xl font-bold";

// BIẾN THỂ CỦA BODY (không phải bậc riêng) - Dùng CHUNG cho cả 2 chỗ dưới đây:
// 1) Dòng bổ trợ ngay dưới `display` (VD: câu tagline dưới tiêu đề Hero)
// 2) Dòng bổ trợ ngay dưới `sectionTitle` (VD: câu giải thích ngắn dưới tiêu đề mỗi section)
// Lý do dùng chung 1 size: độ "hoành tráng" khác nhau giữa 2 vị trí đã được
// chính `display`/`sectionTitle` phía trên tạo ra rồi, bodyLarge không cần to/nhỏ theo.
export const bodyLarge = " text-xl md:text-2xl "; // + mutedText để tách biệt màu

// BẬC 2 - SECTION TITLE: Tiêu đề của 1 khu vực NẰM TRONG 1 trang.
// Dùng cho: Tiêu đề "Kỹ năng", "Kinh nghiệm", "Dự án nổi bật"... khi các mục này
// nằm chung trong 1 trang lớn (VD trang Home có nhiều section).
export const sectionTitle = " text-3xl md:text-4xl font-bold";

// BẬC 3 - CARD TITLE: Tiêu đề của TỪNG ITEM riêng lẻ bên trong 1 danh sách/section.
// Dùng cho: Tên 1 dự án trong ProjectItem, tên 1 mốc trong TimelineItem,
// tên 1 thành tích trong AchievementItem...
export const cardTitle = " text-lg md:text-xl ";

// BẬC 4 - BODY: Đoạn văn nội dung thông thường, không mang vai trò tiêu đề.
// Dùng cho: Mô tả chi tiết trong ProjectItem, nội dung mô tả trong AchievementItem,
// đoạn văn bản dài ở trang AboutMe...
export const body = " text-sm lg:text-base ";

// BẬC 5 - META/LABEL: Chữ nhỏ nhất, mang tính chú thích/kỹ thuật.
// Dùng cho: Ngày tháng (TimelineItem), tech stack tag (TechTag), badge trạng thái...
// Luôn đi kèm font-mono vì đây là nơi baked-in font-mono theo quyết định trước đó.
export const metaLabel = " text-xs font-mono";
```

### 3.4 Font-weight — chỉ 3 mức

| Weight                | Dùng cho                                           |
| --------------------- | -------------------------------------------------- |
| `font-bold` (700)     | Heading các cấp                                    |
| `font-semibold` (600) | Nhấn nhẹ: card title, active nav, tên trong footer |
| `font-normal` (400)   | Body text mặc định                                 |

Tránh dùng thêm `font-medium` (500) rải rác (hiện đang có ở `.btn-primary`) — 3 mức là đủ phân biệt bằng mắt thường; thêm mức thứ 4 khó nhận ra khác biệt nhưng lại làm hệ thống khó nhớ khi maintain.

### 3.5 Line-height

`leading-relaxed` hiện chỉ áp cho 1 đoạn ở Footer — nên đưa vào `@layer base` làm mặc định cho mọi `<p>`:

```css
p {
  @apply leading-relaxed;
}
```

Đoạn mô tả dài (project description, achievement description) đọc sẽ dễ chịu hơn hẳn nếu có leading thoáng, thay vì phải nhớ thêm class này ở từng nơi.

---

## 4. Spacing & Layout (đã chốt — nhắc lại để tiện tra cứu)

- Thang spacing cho layout: chỉ dùng `4 · 6 · 8 · 12 · 16`.
- Ngoại lệ: padding nội bộ của wrapper nhỏ (icon container, badge) được dùng giá trị nhỏ hơn (`p-1`) — coi là styling, không phải layout spacing.
- Container: `max-w-7xl mx-auto`, padding ngang `px-4 md:px-8 lg:px-12` định nghĩa 1 lần ở `ClientLayout`.

---

## 5. Motion / Transition Scale

Hiện tại `baseTransition` chỉ định nghĩa `transition-all ease-linear` (thiếu duration), khiến mỗi nơi dùng tự đoán số duration khác nhau (200/300/500 rải rác) → nhịp chuyển động không đồng nhất trên toàn trang.

Đề xuất chốt 3 mức duration có ý nghĩa, định nghĩa thành hằng số riêng trong `style.js`:

| Mức              | Thời gian | Dùng cho                                   |
| ---------------- | --------- | ------------------------------------------ |
| `transitionFast` | 150–200ms | Vi tương tác: hover chữ, hover icon        |
| `transitionBase` | 300ms     | UI vừa: mở menu mobile, hiện/ẩn badge      |
| `transitionSlow` | 500ms     | Chuyển đổi lớn: light/dark mode toàn trang |

---
