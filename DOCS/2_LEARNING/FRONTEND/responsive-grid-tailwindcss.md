# Responsive Grid với Tailwind CSS

Ghi chú nhanh để ôn lại cách làm responsive grid bằng Tailwind, áp dụng cho trang **About Me**.

## 1. Nguyên tắc cốt lõi: Mobile-first

Tailwind hoạt động theo hướng **mobile-first**. Class không có prefix áp dụng cho mọi màn hình, class có prefix (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`) chỉ áp dụng **từ breakpoint đó trở lên**.

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3"></div>
```

Đọc là: mobile 1 cột → từ `md` (768px) trở lên là 2 cột → từ `lg` (1024px) trở lên là 3 cột.

Bảng breakpoint mặc định:

| Prefix | Min-width |
| ------ | --------- |
| `sm`   | 640px     |
| `md`   | 768px     |
| `lg`   | 1024px    |
| `xl`   | 1280px    |
| `2xl`  | 1536px    |

## 2. Khai báo số cột: `grid-cols-*`

```html
<div class="grid grid-cols-2">
  <!-- 2 cột bằng nhau -->
  <div class="grid grid-cols-4">
    <!-- 4 cột bằng nhau -->
    <div class="grid grid-cols-12">
      <!-- hệ 12 cột, hay dùng cho layout phức tạp -->
    </div>
  </div>
</div>
```

Muốn 1 item chiếm nhiều cột hơn dùng `col-span-*`:

```html
<div class="grid grid-cols-3 gap-4">
  <div class="col-span-2">Chiếm 2/3 cột</div>
  <div>1 cột</div>
</div>
```

## 3. Khoảng cách: `gap-*`

```html
<div class="grid grid-cols-3 gap-4">
  <!-- gap đều 2 chiều -->
  <div class="grid grid-cols-3 gap-x-4 gap-y-8">
    <!-- gap riêng theo chiều -->
  </div>
</div>
```

## 4. Auto-fit / Auto-fill — không cần khai breakpoint thủ công

Đây là cách "lười nhưng hiệu quả": grid tự tính số cột dựa trên độ rộng tối thiểu của item, không cần viết `md:grid-cols-2 lg:grid-cols-3...` từng bậc.

Tailwind không có class dựng sẵn cho auto-fit, nên dùng arbitrary value:

```html
<div class="grid gap-4 grid-cols-[repeat(auto-fit,minmax(240px,1fr))]">
  <div>Card 1</div>
  <div>Card 2</div>
  <div>Card 3</div>
</div>
```

- `auto-fit`: co giãn lấp đầy hàng, item giãn ra nếu không đủ item.
- `auto-fill`: giữ nguyên slot trống nếu ít item (thường hợp cho gallery cố định).
- `minmax(240px, 1fr)`: mỗi item tối thiểu 240px, tối đa chiếm phần còn dư.

Cách này rất hợp cho phần **skill list / project list** trong trang About Me — không cần đoán breakpoint, cứ co màn hình là tự xuống dòng.

## 5. Pattern thường gặp cho trang About Me

### 5.1. Hero section (avatar + giới thiệu)

```html
<section class="grid grid-cols-1 md:grid-cols-[300px_1fr] gap-8 items-center">
  <img src="avatar.jpg" class="w-full rounded-full" />
  <div>
    <h1>Xin chào, mình là ...</h1>
    <p>Giới thiệu ngắn...</p>
  </div>
</section>
```

Mobile: avatar xếp trên, text xếp dưới (vì `grid-cols-1`).
Từ `md` trở lên: 2 cột, cột avatar cố định 300px, cột text chiếm phần còn lại.

### 5.2. Danh sách kỹ năng (skill grid)

```html
<div
  class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4"
>
  <div class="p-4 border rounded text-center">React</div>
  <div class="p-4 border rounded text-center">FastAPI</div>
  <!-- ... -->
</div>
```

Hoặc dùng auto-fit như mục 4 nếu không muốn khai từng breakpoint.

### 5.3. Timeline / Achievements (item xen kẽ trái phải)

```html
<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
  <div class="md:col-start-1">2022 - Bắt đầu học lập trình</div>
  <div class="md:col-start-2 md:mt-16">2023 - Dự án đầu tiên</div>
</div>
```

### 5.4. Card layout (project cards)

```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
  <article class="border rounded-lg p-4">Project A</article>
  <article class="border rounded-lg p-4">Project B</article>
  <article class="border rounded-lg p-4">Project C</article>
</div>
```

## 6. Thứ tự hiển thị khác nhau theo màn hình: `order-*`

```html
<div class="grid grid-cols-1 md:grid-cols-2">
  <div class="order-2 md:order-1">Text</div>
  <div class="order-1 md:order-2">Image</div>
</div>
```

Mobile: ảnh lên trước, text xuống sau. Desktop: đảo lại text trước ảnh sau.

## 7. Ẩn/hiện phần tử theo breakpoint

```html
<div class="hidden md:block">Chỉ hiện từ md trở lên</div>
<div class="block md:hidden">Chỉ hiện dưới md (mobile)</div>
```

Hữu ích khi mobile muốn gộp gọn layout khác hẳn desktop thay vì chỉ đổi số cột.

## 8. Mẹo debug nhanh

- Thêm tạm `outline outline-1 outline-red-500` vào từng item để nhìn rõ ranh giới grid khi layout bị lệch.
- Resize trình duyệt qua từng breakpoint (640 / 768 / 1024 / 1280px) để test thay vì chỉ nhìn ở 1 kích thước.
- Nếu item bị tràn, kiểm tra `min-w-0` trên item — grid item mặc định có `min-width: auto` nên text/img dài có thể đẩy vỡ layout, thêm `min-w-0` để cho phép co lại.

## 9. Tổng hợp nhanh (cheat sheet)

| Việc cần làm                       | Class                                          |
| ---------------------------------- | ---------------------------------------------- |
| Số cột                             | `grid-cols-{n}`                                |
| Số cột theo breakpoint             | `md:grid-cols-{n}`                             |
| Item chiếm nhiều cột               | `col-span-{n}`                                 |
| Khoảng cách                        | `gap-{n}`, `gap-x-{n}`, `gap-y-{n}`            |
| Tự động co giãn cột                | `grid-cols-[repeat(auto-fit,minmax(Npx,1fr))]` |
| Đổi thứ tự                         | `order-{n}`                                    |
| Ẩn/hiện theo màn hình              | `hidden md:block`                              |
| Cột có độ rộng cố định + linh hoạt | `grid-cols-[300px_1fr]`                        |

Bắt buộc phải có class grid thì các class grid-cols-... mới có tác dụng.
Tuy nhiên, một thẻ HTML không thể vừa là flex vừa là grid cùng một lúc trên cùng một kích thước màn hình vì chúng là hai chế độ hiển thị (display) độc lập. Bạn có thể thay đổi giữa flex và grid theo breakpoint, hoặc phân tách cấu trúc thẻ.

## Cách 1: Thay đổi display theo breakpoint (Khuyên dùng)

Nếu bạn muốn màn hình nhỏ dùng flex để sắp xếp các phần tử, còn màn hình lớn dùng grid để chia cột (hoặc ngược lại), bạn có thể ghi đè class display bằng tiền tố responsive.

```html
<!-- Màn nhỏ: dùng Flexbox | Màn lớn (md): chuyển sang Grid 6 cột -->
<div class="flex flex-col md:grid md:grid-cols-6 gap-4">
  <!-- Các item con -->
</div>
```

- Màn hình nhỏ: Nhận flex và flex-col, các item xếp chồng theo hàng dọc. Lúc này md:grid-cols-6 hoàn toàn bị bỏ qua.
- Màn hình lớn (md): md:grid sẽ ghi đè flex. Kèm theo md:grid-cols-6 để kích hoạt lưới 6 cột.

---

## Cách 2: Chia làm 2 cấp thẻ (Nếu "div" của bạn là item con)

Theo mô tả "màn nhỏ chiếm 12 cột, màn to chiếm 6 cột", có thể bạn đang nhầm lẫn: grid-cols là class đặt ở thẻ cha để định dạng tổng số cột, còn col-span mới là class đặt ở thẻ con để quyết định nó chiếm bao nhiêu cột.
Nếu bạn muốn cái div đó vừa nhận layout grid từ cha, vừa tự bản thân nó là một hộp flex để căn chỉnh các phần tử bên trong nó, hãy tổ chức như sau:

```html
<!-- THẺ CHA: Định nghĩa hệ thống lưới (luôn là 12 cột) -->
<div class="grid grid-cols-12 gap-4">
  <!-- THẺ CON (Div của bạn): Vừa định kích thước grid, vừa chứa thuộc tính flex -->
  <div class="col-span-12 md:col-span-6 flex items-center justify-between">
    <p>Nội dung bên trái</p>
    <button>Nút bên phải</button>
  </div>

  <div class="col-span-12 md:col-span-6 bg-gray-100">Box khác...</div>
</div>
```

Giải thích cách hoạt động:

- Về Grid: Thẻ con sử dụng col-span-12 (mặc định chiếm trọn 12 cột ở màn hình nhỏ) và md:col-span-6 (chiếm một nửa - 6/12 cột ở màn hình lớn).
- Về Flex: Thẻ con sở hữu class flex items-center justify-between để tự dàn trang các phần tử ruột bên trong nó theo trục ngang.

---

## ⚠️ Lưu ý quan trọng về Tailwind Grid

- Bạn luôn luôn phải ghi grid kèm theo grid-cols-.... Nếu chỉ viết grid-cols-12, trình duyệt sẽ không hiểu hệ thống lưới vì thiếu thuộc tính display: grid.
- Tương tự, nếu muốn dùng col-span, thẻ cha bắt buộc phải có class grid.
