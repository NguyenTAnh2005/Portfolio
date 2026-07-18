# Vấn đề là gì?

Khi component `AboutMe` được render, `useEffect` chạy và bắt đầu gọi API (`infoService.getInfo(1)`). Việc gọi API này mất thời gian (vài trăm ms, có khi vài giây). Trong lúc đang đợi kết quả trả về, nếu người dùng bấm chuyển sang trang khác (route khác) — thì component `AboutMe` đã bị **unmount** (React gỡ nó khỏi màn hình, xoá luôn).

Nhưng cái Promise fetch API vẫn đang chạy nền, nó không tự biết là component đã bị gỡ. Khi fetch xong, code vẫn cố gọi:

```js
setData(response); // hoặc setError(err)
```

Mà `setData` này là để cập nhật state của 1 component **không còn tồn tại nữa**. React sẽ in ra warning kiểu:

> "Can't perform a React state update on an unmounted component"

Nó không làm crash app, nhưng là dấu hiệu của memory leak nhỏ (giữ tham chiếu tới component đã chết) và là code không "sạch".

**Ví dụ cụ thể để dễ hình dung:**

1. User vào trang `/about` → `AboutMe` mount → `useEffect` chạy → gọi API, đang đợi.
2. API chậm (giả sử 3 giây).
3. Sau 1 giây, user bấm sang trang `/contact` → React unmount `AboutMe`.
4. Sau 3 giây, API trả kết quả về → code chạy `setData(response)` → nhưng component đã bị unmount → warning.

**Cách sửa bằng cờ `isMounted` (dễ hiểu nhất với người mới):**

Ý tưởng: tạo 1 biến cờ, ban đầu là `true`. Khi component unmount thì đặt nó về `false`. Trước khi gọi `setData`/`setError`, kiểm tra cờ này trước.

```jsx
useEffect(() => {
  let isMounted = true; // cờ báo "component còn sống"

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await infoService.getInfo(1);
      if (isMounted) setData(response); // chỉ set khi còn "sống"
    } catch (err) {
      if (isMounted) setError(err);
    } finally {
      if (isMounted) setLoading(false);
    }
  };

  fetchData();

  // đây là "cleanup function" - React tự động gọi hàm này khi component unmount
  return () => {
    isMounted = false;
  };
}, []);
```

Chú ý phần `return () => { isMounted = false; }` ở cuối `useEffect` — đây gọi là **cleanup function**. React tự động gọi nó ngay trước khi component bị unmount (hoặc trước khi effect chạy lại, nếu có dependency thay đổi). Đó là cơ chế chuẩn để "dọn dẹp" trước khi component biến mất.

Còn `AbortController` là cách "xịn" hơn — nó thực sự **huỷ request HTTP đang bay** (tiết kiệm băng thông, server cũng ngừng xử lý), thay vì chỉ chặn không cho `setState` chạy. Nhưng nó phức tạp hơn một chút, nên với dự án nhỏ hiện tại của bạn, cách `isMounted` ở trên là đủ dùng và dễ hiểu hơn nhiều.

# `Cần tách bạch hai thứ: **cái gì khiến component unmount** và **cleanup function hoạt động ra sao**.`

## Unmount không phải là "bấm gì đó" — mà là "React quyết định không render component này nữa"

React chỉ unmount một component khi nó **biến mất khỏi cây component (component tree)** mà React đang render ra. Điều này chỉ xảy ra trong 3 trường hợp:

1. **Component cha ngừng render nó** — ví dụ conditional rendering: `{showAbout && <AboutMe />}`, khi `showAbout` chuyển từ `true` sang `false`.
2. **Route thay đổi** (nếu dùng React Router) — khi URL không còn match với route chứa `AboutMe` nữa, router sẽ gỡ nó ra và render component khác vào.
3. **`key` thay đổi** — React coi đó là một instance hoàn toàn mới, unmount cái cũ và mount cái mới.

Ngoài 3 trường hợp này ra, **không có hành động nào khác khiến component unmount** — kể cả click, gõ phím, resize, scroll... Bản thân sự kiện click không unmount gì cả; nó chỉ unmount nếu logic xử lý sự kiện đó _dẫn đến_ một trong 3 trường hợp trên (ví dụ: `onClick` gọi `navigate('/contact')` → route đổi → unmount).

## Trả lời trực tiếp các ví dụ của bạn

- **Bấm vào thanh tìm kiếm** (nếu thanh tìm kiếm nằm bên trong `AboutMe`, hoặc ở component khác không ảnh hưởng đến việc `AboutMe` có được render hay không) → **không unmount**. Component vẫn còn nguyên trên cây, chỉ là bạn tương tác với 1 phần tử DOM bên trong nó.
- **Bấm lung tung trong div khi đang loading** → **không unmount**, miễn là những cú click đó không kích hoạt điều hướng trang hoặc thay đổi state ở component cha làm nó ngừng render `AboutMe`.
- **Duy nhất unmount thật sự** trong ví dụ ban đầu của bạn là do **chuyển route** (`/about` → `/contact`), tức rơi vào trường hợp 2 ở trên.

Nói cách khác: unmount là kết quả của _thay đổi trong cây render_, không phải kết quả trực tiếp của thao tác chuột/bàn phím.

## Vậy `return () => { isMounted = false; }` "biết" khi nào để chạy như thế nào?

Đây là cơ chế của React, không phải magic tự dò tìm hành động người dùng. Cụ thể:

- Mỗi lần `useEffect` chạy, React "nhớ" hàm cleanup mà bạn return ra.
- Ngay **trước khi** React thực sự gỡ component đó khỏi DOM (tức unmount xảy ra do 1 trong 3 lý do ở trên), React tự động gọi hàm cleanup đó.
- `isMounted` chỉ là 1 biến local sống trong **closure** của lần chạy effect đó — không liên quan gì đến DOM hay sự kiện chuột. Khi cleanup chạy, nó set `isMounted = false`, và vì hàm `fetchData` bên trong cũng đang tham chiếu tới đúng biến `isMounted` này (qua closure), nên khi Promise resolve sau đó, `if (isMounted)` sẽ là `false` → không gọi `setData` nữa.

Tóm gọn: bạn không cần lo về việc "hành động nào" gây unmount — chỉ cần nhớ unmount = component biến mất khỏi cây render (do cha ngừng render, đổi route, hoặc đổi key). Còn `isMounted` chỉ đơn giản là 1 cái cờ đóng trong bộ nhớ của closure, được React tự "bật/tắt" đúng lúc unmount xảy ra.
