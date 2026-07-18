# Giáo Trình: React Hooks Nền Tảng
## useState — useEffect — useCallback

> **Đối tượng:** Người đã biết cú pháp React cơ bản (JSX, component, props) nhưng muốn hiểu **bản chất** hoạt động của 3 hook nền tảng, thay vì học vẹt cách dùng.
> **Yêu cầu trước khi học:** Nắm cơ bản JavaScript (function, scope, object, array). Không cần biết trước về React.
> **Mục tiêu sau khi học xong:** Đọc được bất kỳ đoạn code nào dùng 3 hook này và tự giải thích được "tại sao nó chạy như vậy", tự debug được lỗi vòng lặp vô hạn hoặc bug dữ liệu cũ (stale data).

---

# PHẦN 0 — NỀN TẢNG: COMPONENT LÀ GÌ?

## 0.1. Hai mô hình lập trình web: Imperative vs Declarative

Trước React, lập trình web (jQuery, vanilla JS) theo mô hình **imperative** (mệnh lệnh) — bạn tự tay ra lệnh từng bước "làm cái này, rồi làm cái kia":

```js
// Cách cũ (imperative): tự tay chỉ đạo từng bước thay đổi DOM
const btn = document.getElementById("btn");
const display = document.getElementById("display");
let count = 0;

btn.addEventListener("click", () => {
  count = count + 1;              // Bước 1: đổi dữ liệu
  display.innerText = count;      // Bước 2: TỰ TAY tìm đúng phần tử DOM để sửa
});
```

Nhược điểm: khi UI phức tạp (hàng chục phần tử phụ thuộc lẫn nhau), bạn phải tự nhớ **"khi dữ liệu X đổi thì cần sửa DOM ở chỗ A, B, C nào"** — rất dễ quên sót, dễ sai thứ tự, code phình to không kiểm soát nổi.

React theo mô hình **declarative** (khai báo) — bạn chỉ viết **"với dữ liệu này thì UI trông như thế nào"**, còn việc tính toán "cần sửa đúng chỗ nào trên DOM thật" thì giao hẳn cho React tự lo:

```jsx
function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

Bạn không hề viết dòng nào kiểu `display.innerText = ...` cả — bạn chỉ mô tả "UI = một button, hiển thị số `count`". React tự động lo phần "tìm đúng chỗ trong DOM thật để sửa".

## 0.2. Component thực chất là gì?

> **Component trong React KHÔNG PHẢI là "1 vùng UI sống mãi trên màn hình"**. Nó chỉ là **1 hàm JavaScript bình thường**. React **gọi lại hàm này liên tục** mỗi khi cần tính toán lại giao diện — hành động này gọi là **re-render**.

Để thấy rõ, so sánh với 1 hàm JS thuần không liên quan gì đến React:

```js
function counter() {
  let k = 0;
  k = k + 1;
  console.log(k);
}

counter(); // in ra: 1
counter(); // in ra: 1  (KHÔNG PHẢI 2!)
counter(); // in ra: 1  (mãi mãi vẫn là 1)
```

Mỗi lần gọi `counter()`, biến `k` được **tạo mới hoàn toàn**, tăng lên 1, rồi **bị hủy sạch** ngay khi hàm chạy xong. Lần gọi sau **không hề "biết"** lần gọi trước đã xảy ra chuyện gì — đây là hành vi mặc định 100% của **mọi hàm JS**, không có ngoại lệ.

Bây giờ nhìn lại component React:

```jsx
function Counter() {
  console.log("Hàm Counter() vừa được gọi!");
  let count = 0; // nếu dùng let bình thường, biến này sẽ CHẾT sau mỗi lần hàm chạy xong
  return <button>{count}</button>;
}
```

Nếu `Counter` chỉ được gọi đúng 1 lần lúc trang tải, UI sẽ **vĩnh viễn tĩnh** — không có cách nào bấm nút mà số tăng lên được. Nhưng thực tế UI web tương tác được, nghĩa là React **phải gọi lại hàm `Counter()` nhiều lần** trong suốt vòng đời trang, mỗi khi có gì đó cần cập nhật.

**→ Vấn đề nảy sinh:** Nếu dùng biến `let count = 0` như JS bình thường bên trong hàm, biến này sẽ **reset về 0 mỗi lần `Counter()` được gọi lại** — giống hệt ví dụ `counter()` ở trên. Vậy làm cách nào để "nhớ" được số đã tăng đến đâu, xuyên suốt qua nhiều lần gọi hàm?

**→ Đây chính là bài toán mà `useState` sinh ra để giải quyết.**

## 0.3. Quy trình render tổng quát (sẽ dùng xuyên suốt giáo trình)

```
┌─────────────────────────────────────────────────────────┐
│  1. Có sự kiện kích hoạt (click, gọi setState, mount...)  │
│         ↓                                                 │
│  2. React GỌI LẠI hàm component từ đầu đến return          │
│     (mọi dòng code trong thân hàm chạy lại — GIAI ĐOẠN     │
│      RENDER, phải thuần túy, không side-effect)            │
│         ↓                                                 │
│  3. Hàm trả về JSX (mô tả UI mong muốn dưới dạng cây)       │
│         ↓                                                 │
│  4. React so sánh cây JSX mới với cây JSX cũ ("diffing")   │
│         ↓                                                 │
│  5. React chỉ SỬA đúng phần DOM thật sự thay đổi           │
│     (không vẽ lại toàn trang — đây là lý do React nhanh)   │
│         ↓                                                 │
│  6. SAU KHI DOM đã cập nhật xong, các useEffect có deps    │
│     phù hợp mới được chạy — GIAI ĐOẠN EFFECT                │
└─────────────────────────────────────────────────────────┘
```

Ghi nhớ pipeline này — toàn bộ giáo trình sẽ liên tục quay lại tham chiếu đúng 6 bước trên.

---

# PHẦN 1 — `useState`: BỘ NHỚ SỐNG NGOÀI LẦN CHẠY HÀM

## 1.1. Định nghĩa

`useState` là hook cho phép 1 component "nhớ" 1 giá trị **xuyên suốt qua nhiều lần re-render**, dù bản thân hàm component mỗi lần chạy đều là 1 lượt hoàn toàn mới.

```jsx
const [state, setState] = useState(initialValue);
```

- `state`: giá trị hiện tại (chỉ đọc, không tự gán trực tiếp)
- `setState`: hàm dùng để yêu cầu đổi giá trị
- `initialValue`: giá trị khởi tạo, **chỉ được dùng ở lần đầu tiên** (lần mount)

## 1.2. Cơ chế "cuốn sổ" của React

Hình dung React có 1 cuốn sổ riêng, tách biệt hoàn toàn khỏi thân hàm component, dùng để ghi nhớ giá trị state qua các lần gọi hàm:

```
Sổ của React (nằm NGOÀI hàm Counter, do React tự quản lý):
┌───────────────────────────────┐
│ Component "Counter" — lần 1     │
│   slot 0: count = 0             │
└───────────────────────────────┘
```

**Quy trình đầy đủ khi bấm nút** (component sau):

```jsx
function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

```
1. User click button
2. onClick chạy → gọi setCount(1)
3. setCount KHÔNG sửa biến "count" ngay tại chỗ.
   Nó báo cho React: "Ghi 1 vào slot 0 của sổ, rồi gọi lại Counter() giúp tôi."
4. React cập nhật sổ:
   ┌───────────────────────────────┐
   │ Component "Counter" — lần 2     │
   │   slot 0: count = 1             │
   └───────────────────────────────┘
5. React gọi lại Counter() từ đầu.
   Dòng "useState(0)" chạy lại — nhưng lần này KHÔNG trả về 0 mặc định,
   mà "liếc vào sổ" thấy slot 0 đã có giá trị 1 → trả về 1.
6. Hàm chạy tiếp, return <button>{count}</button> → lần này render ra số 1.
```

> **Điểm mấu chốt:** biến `count` bạn thấy trong code chỉ là **1 "cửa sổ nhìn vào" giá trị đang nằm trong sổ của React**, không phải một biến tự thân tồn tại và sống sót bên trong thân hàm.

## 1.3. Vì sao không thể tự gán `count = count + 1`?

Vì `setState` không chỉ "gán giá trị" — nó còn kiêm nhiệm vụ **"báo hiệu cho React biết cần render lại"**. Nếu tự ý gán biến trực tiếp (`count = count + 1`), React **hoàn toàn không hay biết** gì cả, nên sẽ không có lý do gì để gọi lại hàm và vẽ lại UI — dữ liệu có đổi trong bộ nhớ, màn hình vẫn đứng yên.

### Thí nghiệm minh chứng

```jsx
let count = 0; // biến toàn cục ngoài hàm

function Counter() {
  return (
    <button onClick={() => { count = count + 1; }}>
      {count}
    </button>
  );
}
```

Bấm nút → `count` **thực sự tăng lên 1** trong bộ nhớ máy. Nhưng số hiển thị trên màn hình **không hề đổi**, vẫn đứng yên ở `0`. Lý do: không ai gọi `setState`, nên bước 2 trong pipeline (React gọi lại hàm) **không bao giờ xảy ra**.

Ngoài ra, cách này còn phạm lỗi thứ hai: nếu trang có `<Counter /> <Counter />` (2 lần dùng), **cả 2 sẽ dùng chung 1 biến `count` toàn cục** — bấm cái này (giả sử ép được UI vẽ lại) sẽ khiến cả 2 ô số cùng nhảy, vì thực chất chúng đang đọc chung 1 giá trị. Trong khi đó, với `useState`, **mỗi lần dùng `<Counter />` có "sổ" riêng biệt hoàn toàn**.

| | Biến ngoài hàm (`let x`) | `useState` |
|---|---|---|
| Có báo cho React vẽ lại UI khi đổi? | ❌ Không | ✅ Có, qua `setState` |
| Có tách biệt riêng cho từng component instance? | ❌ Không, dùng chung | ✅ Có, mỗi instance 1 sổ riêng |

## 1.4. Cập nhật state dựa trên giá trị cũ — Functional Update

Có 2 cách gọi `setState`:

```jsx
// Cách 1: truyền thẳng giá trị mới
setCount(count + 1);

// Cách 2: truyền 1 hàm nhận giá trị cũ, trả về giá trị mới
setCount(prev => prev + 1);
```

**Vì sao cần cách 2?** Vì các lệnh `setState` gọi liên tiếp trong cùng 1 sự kiện có thể bị **gộp lại (batching)** — React không xử lý ngay từng cái một, mà đợi gom hết rồi mới render lại 1 lần cho tối ưu hiệu năng. Điều này gây ra bug tinh vi:

```jsx
function handleClick() {
  setCount(count + 1); // count đang là 0 → set thành 1
  setCount(count + 1); // count VẪN LÀ 0 (vì chưa render lại) → set thành 1 (không phải 2!)
  setCount(count + 1); // tương tự → set thành 1
}
// Kết quả: count chỉ tăng lên 1, dù gọi setCount 3 lần!
```

Vì cả 3 lần gọi `setCount(count + 1)` đều đọc `count` từ **cùng 1 lần render** (giá trị cũ là 0), nên cả 3 đều tính ra kết quả `1`, ghi đè lên nhau.

```jsx
function handleClick() {
  setCount(prev => prev + 1); // prev=0 → 1
  setCount(prev => prev + 1); // prev=1 (giá trị VỪA được tính ở dòng trên) → 2
  setCount(prev => prev + 1); // prev=2 → 3
}
// Kết quả: count tăng đúng 3, vì mỗi hàm nhận giá trị MỚI NHẤT do dòng trước tính ra
```

> **Quy tắc thực dụng:** nếu giá trị mới **phụ thuộc vào giá trị cũ**, luôn dùng dạng hàm `setState(prev => ...)`. Nếu giá trị mới **độc lập, không liên quan giá trị cũ** (ví dụ set thẳng 1 object mới lấy từ input), dùng dạng trực tiếp `setState(newValue)` cũng được.

## 1.5. State là object hay array — lỗi "mutate trực tiếp"

Khi state là object/array, một lỗi rất phổ biến là **sửa trực tiếp** nội dung bên trong thay vì tạo bản sao mới:

```jsx
const [user, setUser] = useState({ name: "An", age: 20 });

// ❌ SAI — sửa trực tiếp object cũ
function updateAge() {
  user.age = 21;       // sửa "hộp" object cũ tại chỗ
  setUser(user);        // truyền lại CHÍNH hộp cũ đó
}
```

Lỗi này liên quan trực tiếp đến kiến thức "so sánh bằng địa chỉ hộp" (sẽ học kỹ ở Phần 3) — React (và nhiều cơ chế tối ưu bên trong) thường kiểm tra xem state mới có phải "hộp khác" với state cũ hay không để quyết định có cần render lại. Nếu bạn sửa trực tiếp rồi truyền lại **chính hộp cũ**, về mặt tham chiếu `user === user` (cùng 1 địa chỉ) — trong nhiều trường hợp React vẫn nhận diện đổi (vì `setState` luôn trigger check), nhưng đây vẫn là **thói quen nguy hiểm**, dễ gây bug khó lường khi kết hợp với các tối ưu khác (như `React.memo`, hoặc dùng thư viện quản lý state ngoài).

**Cách đúng — luôn tạo object/array MỚI:**

```jsx
// ✅ ĐÚNG — spread operator tạo object mới, giữ nguyên field cũ, ghi đè field cần đổi
function updateAge() {
  setUser(prev => ({ ...prev, age: 21 }));
}

// ✅ ĐÚNG — với array, dùng map/filter/spread thay vì push/splice trực tiếp
const [items, setItems] = useState([1, 2, 3]);
function addItem(newItem) {
  setItems(prev => [...prev, newItem]); // tạo array mới, không push vào array cũ
}
```

## 1.6. Nhiều `useState` hay 1 `useState` chứa object?

```jsx
// Cách A: nhiều state riêng lẻ
const [name, setName] = useState("");
const [age, setAge] = useState(0);
const [email, setEmail] = useState("");

// Cách B: 1 state gộp thành object
const [form, setForm] = useState({ name: "", age: 0, email: "" });
```

| Tiêu chí | Cách A (tách riêng) | Cách B (gộp object) |
|---|---|---|
| Các field độc lập, không liên quan nhau | ✅ Nên dùng | Không cần thiết |
| Các field luôn cập nhật cùng lúc (VD: 1 form) | Rườm rà | ✅ Nên dùng |
| Cần cập nhật 1 field | Gọi trực tiếp `setAge(21)` | Phải spread: `setForm(prev => ({...prev, age: 21}))` |

Không có đáp án tuyệt đối đúng-sai, tùy ngữ cảnh — nguyên tắc chung: nếu các giá trị **luôn đổi cùng lúc và liên quan chặt chẽ** (như 1 object `queryParam` gồm `title`, `skip`, `limit` để gọi API), gộp thành 1 state hợp lý hơn.

## 1.7. Vì sao mất state khi F5 (Refresh)? — Liên hệ RAM/Process

Đây là câu hỏi nối trực tiếp với kiến thức lập trình hệ thống (C/C++) — rất đáng hiểu kỹ vì nó giải thích **tại sao** state biến mất, không chỉ "biết là nó biến mất".

### Ôn lại: RAM của 1 chương trình C++

Khi chạy `./a.out`, hệ điều hành (OS) cấp cho chương trình đó **1 vùng RAM riêng** (gọi là *process memory*). Mọi biến, object chương trình tạo ra nằm trong vùng RAM này. Khi chương trình kết thúc (hoặc bị tắt), OS **thu hồi lại toàn bộ vùng RAM đó** — mọi dữ liệu biến mất sạch.

### Trình duyệt hoạt động tương tự

Mỗi **tab trình duyệt đang mở 1 trang = 1 tiến trình (process) đang chạy**, y hệt việc chạy `./a.out`. Bên trong trình duyệt có 1 **JS Engine** (Chrome dùng V8) đóng vai trò như CPU thực thi code JavaScript. Mọi biến JS (kể cả "sổ" state của React) được cấp phát trong **vùng RAM (cụ thể là Heap) của tiến trình tab đó**.

```
Mở tab trình duyệt vào trang web
    → OS cấp phát vùng RAM cho tiến trình (tab) này
    → JS Engine chạy code, tạo object trong Heap
        [ "Sổ" state của React, cây DOM, mọi biến JS khác... ]
```

### F5 tương đương gì bên C++?

**F5 = đóng chương trình cũ, chạy lại chương trình mới từ đầu** — tương đương `Ctrl+C` tắt `./a.out` đang chạy, rồi gõ `./a.out` chạy lại lần nữa.

```
F5 (refresh)
    → Trình duyệt HỦY toàn bộ tiến trình JS đang chạy trong tab
      (mọi biến/object trong Heap bị OS thu hồi — y hệt tắt ./a.out)
    → Trình duyệt tải lại HTML/JS từ đầu
    → JS Engine thực thi lại từ dòng code đầu tiên
      → tạo ra "sổ" React HOÀN TOÀN MỚI, rỗng trơn
      → useState(0) chạy lần đầu → trả về 0 (không nhớ gì về "kiếp trước")
```

### Bảng đối chiếu

| C++ (`./a.out`) | React trong trình duyệt |
|---|---|
| Chạy chương trình → OS cấp RAM cho tiến trình | Mở tab web → OS cấp RAM cho tiến trình tab |
| Biến nằm trong Stack/Heap của tiến trình | State React nằm trong Heap của tiến trình tab |
| Tắt/kill chương trình → RAM bị thu hồi | F5/đóng tab → JS engine bị hủy, RAM bị thu hồi |
| Chạy lại `./a.out` → biến khởi tạo lại từ đầu | F5 → mọi component/state khởi tạo lại từ đầu |
| Muốn dữ liệu sống qua nhiều lần chạy → ghi ra file (`fstream`) | Muốn dữ liệu sống qua F5 → ghi vào `localStorage` (vùng lưu trữ **ngoài** tiến trình JS, do trình duyệt quản lý riêng, KHÔNG bị xóa khi F5) |

> **Ứng dụng thực tế:** đây là lý do các hệ thống đăng nhập lưu JWT token cả trong `useState` (để React re-render UI theo trạng thái đăng nhập) **và** `localStorage` (để token sống sót qua F5, không bắt người dùng đăng nhập lại mỗi lần load trang).

## 1.8. Tóm tắt Phần 1

> Component không phải "1 vùng UI sống", nó là **1 công thức tính UI**, được React gọi đi gọi lại. `useState` giúp công thức đó "nhớ" được số liệu qua nhiều lần tính toán, dù mỗi lần hàm chạy đều là 1 lượt hoàn toàn mới, sạch từ đầu — và "sổ nhớ" đó nằm trong RAM của tiến trình tab, nên sẽ mất sạch khi F5.

## 1.9. Bài tập tự kiểm tra Phần 1

1. Cho đoạn code sau, dự đoán số lần "Component chạy" được in ra sau khi bấm nút 3 lần:
```jsx
function Box() {
  console.log("Component chạy");
  const [n, setN] = useState(0);
  return <button onClick={() => setN(n + 1)}>{n}</button>;
}
```
2. Viết lại đoạn `updateAge` ở mục 1.5 theo đúng cách "không mutate trực tiếp".
3. Giải thích bằng lời của bạn: tại sao `setCount(count + 1)` gọi 3 lần liên tiếp trong `handleClick` chỉ tăng đúng 1 đơn vị, trong khi `setCount(prev => prev + 1)` gọi 3 lần lại tăng đúng 3 đơn vị?
4. Nếu bạn lưu 1 giá trị chỉ cần tồn tại trong lúc người dùng đang thao tác trên 1 trang, không cần sống sót qua F5 — bạn dùng `useState` hay `localStorage`? Vì sao?

---

# PHẦN 2 — `useEffect`: LÀM VIỆC "NGOÀI LUỒNG" SAU KHI UI ĐÃ VẼ XONG

## 2.1. Side-effect là gì?

> **Thuần túy (pure)** = hàm chỉ nhận input, trả về output, **không đụng chạm gì ra bên ngoài chính nó**, và cùng 1 input luôn cho ra cùng 1 output.
> **Side-effect** (tác dụng phụ) = bất kỳ hành động nào **thò tay ra ngoài phạm vi hàm**, ảnh hưởng thế giới bên ngoài, hoặc phụ thuộc vào thứ có thể đổi bất cứ lúc nào.

| Việc làm | Thuần túy hay Side-effect? | Vì sao |
|---|---|---|
| `const total = a + b` | ✅ Thuần túy | Chỉ tính từ input, không đụng gì bên ngoài |
| `return <div>{count}</div>` | ✅ Thuần túy | Chỉ mô tả UI dựa trên input |
| `fetch('/api/data')` | ❌ Side-effect | Gọi ra mạng, kết quả phụ thuộc server, không đoán trước được |
| `localStorage.setItem(...)` | ❌ Side-effect | Ghi vào bộ nhớ trình duyệt, tồn tại ngoài vòng đời component |
| `document.title = "..."` | ❌ Side-effect | Sửa DOM trực tiếp, ngoài phạm vi React quản lý |
| `setInterval(...)` | ❌ Side-effect | Tạo tiến trình chạy nền, sống độc lập với hàm |
| `console.log(...)` | ❌ Side-effect (nhẹ) | Vẫn là "thò ra ngoài" (ghi vào console) |
| `Math.random()` | ❌ Side-effect | Cùng input nhưng ra kết quả khác nhau mỗi lần gọi |

## 2.2. Vì sao không được đặt side-effect thẳng trong thân hàm component

Nhớ lại pipeline render ở Phần 0: giai đoạn RENDER (bước 2) được thiết kế để chạy đi chạy lại **rất nhiều lần**, càng nhanh càng tốt, và **phải thuần túy** — cùng input thì luôn ra cùng UI. Nếu nhét side-effect vào giữa giai đoạn này, hậu quả rất đa dạng:

### Ví dụ A — Vòng lặp vô hạn khi gọi API trong thân hàm

```jsx
function Timelines() {
  const [data, setData] = useState(null);

  timelineService.get().then(result => setData(result)); // ❌ ĐỪNG LÀM VẬY

  return <div>{data?.length}</div>;
}
```

```
Render 1: data=null → gọi API → API xong → setData(result)
Render 2 (do setData kích hoạt): data=[...] → dòng gọi API LẠI CHẠY (nằm trong thân hàm,
          luôn chạy mỗi lần render) → gọi API LẦN NỮA → setData
Render 3: → lại gọi API → lại setData → ...
          → KHÔNG BAO GIỜ DỪNG, spam server liên tục
```

### Ví dụ B — `Math.random()` khiến UI "nhấp nháy" vô lý

```jsx
function Card() {
  const color = Math.random() > 0.5 ? "red" : "blue"; // ❌ side-effect kiểu ngẫu nhiên
  return <div style={{ color }}>Hello</div>;
}
```

Mỗi lần component này re-render vì **lý do khác** (ví dụ component cha đổi state), màu lại đổi ngẫu nhiên — dù không ai yêu cầu đổi màu. Rất khó debug vì "tự nhiên đổi" không rõ nguyên nhân.

### Ví dụ C — Sửa DOM tay trong thân hàm gây xung đột

```jsx
function Title({ text }) {
  document.title = text; // ❌ nằm trong thân hàm, chạy mỗi lần render
  return <h1>{text}</h1>;
}
```

React được phép render 1 component nhiều lần liên tiếp trong nội bộ (tối ưu riêng của React, gọi là "render nhưng chỉ commit 1 lần") — nếu `document.title = text` nằm trong thân hàm, nó có thể bị gọi thừa thãi nhiều lần không cần thiết, tốn hiệu năng, thậm chí gây nhấp nháy tiêu đề tab.

**Cách sửa cho cả 3 ví dụ giống hệt nhau: đưa vào `useEffect`.**

## 2.3. `useEffect` — tách 2 giai đoạn Render và Effect

```
Giai đoạn 1 (RENDER):  Tính toán UI trông ra sao — phải thuần túy, nhanh, không side-effect
                                    ↓
                        React vẽ UI đó lên màn hình (DOM)
                                    ↓
Giai đoạn 2 (EFFECT):   SAU KHI đã vẽ xong, mới cho phép chạy các việc "bẩn"
                        (gọi API, sửa localStorage, đăng ký sự kiện...)
```

```jsx
function Timelines() {
  const [data, setData] = useState(null);

  useEffect(() => {
    timelineService.get().then(result => setData(result));
  }, []); // mảng rỗng: chỉ chạy 1 lần, sau lần vẽ đầu tiên

  return <div>{data?.length}</div>;
}
```

Vòng lặp không còn nữa: `setData` bên trong `useEffect` khiến React render lại UI (giai đoạn 1), nhưng effect có chạy lại hay không **phụ thuộc hoàn toàn vào mảng dependency** — mảng `[]` nghĩa là "không phụ thuộc gì, chỉ chạy đúng 1 lần".

## 2.4. Cú pháp và 3 kiểu mảng dependency

```jsx
useEffect(callbackFunction, dependencyArray);
```

| Cú pháp | Khi nào effect chạy | Ví dụ dùng cho |
|---|---|---|
| `useEffect(fn)` — không có mảng | Chạy lại **mỗi lần** component render | Hiếm khi cần, thường là bug nếu vô tình quên mảng |
| `useEffect(fn, [])` | Chạy **đúng 1 lần**, ngay sau lần render đầu tiên (mount) | Fetch data 1 lần khi vào trang, đăng ký event listener 1 lần |
| `useEffect(fn, [a, b])` | Chạy lại **mỗi khi `a` hoặc `b` đổi** so với lần render trước | Fetch lại API khi tham số tìm kiếm đổi |

## 2.5. Cơ chế so sánh mảng dependency — "React so sánh cái gì, như thế nào?"

Đây là phần hay bị hiểu nhầm là "phép màu". Thực chất: **React KHÔNG so sánh cả mảng như 1 khối duy nhất** — nó **tháo mảng ra, so sánh TỪNG PHẦN TỬ** với phần tử tương ứng ở cùng vị trí của lần render trước:

```
useEffect(fn, [a, b, c])

React thực chất làm:
  so phần tử [0]: a (lần này) vs a (lần trước) → giống hay khác?
  so phần tử [1]: b (lần này) vs b (lần trước) → giống hay khác?
  so phần tử [2]: c (lần này) vs c (lần trước) → giống hay khác?

Chỉ cần 1 phần tử KHÁC  → coi như "deps đổi" → effect CHẠY LẠI
Cả 3 phần tử đều GIỐNG  → "deps không đổi" → effect KHÔNG CHẠY
```

**Vì sao React không so cả mảng làm 1 khối?** Vì bản thân `[]` hay `[a, b]` là 1 **array literal** — mỗi lần component render, dòng `useEffect(fn, [a, b])` tạo ra **1 mảng MỚI trong bộ nhớ** (sẽ học kỹ tại sao ở Phần 3). Nếu so sánh cả mảng bằng `===`, kết quả sẽ **luôn luôn là "khác nhau"** (vì luôn là 2 hộp mảng khác nhau), khiến toàn bộ cơ chế dependency trở nên vô dụng. Vì vậy React buộc phải "mở mảng ra", so từng phần tử bên trong theo đúng kiểu dữ liệu của nó.

### Quy tắc so sánh theo kiểu dữ liệu

| Kiểu dữ liệu | Cách so sánh |
|---|---|
| Nguyên thủy: number, string, boolean | So theo **giá trị** — `"An" === "An"` → `true` |
| Object, Array, Function | So theo **địa chỉ hộp trong bộ nhớ** — `{} === {}` → `false`, dù cả 2 đều rỗng |

### Trường hợp đặc biệt: mảng rỗng `[]`

Với `[]`, không có phần tử nào bên trong để so sánh. Đây là trường hợp **"rỗng logic"** (tương tự khái niệm *vacuously true* trong toán học): không có gì để khác nhau, nên React mặc định coi là "giống hệt nhau" ở mọi lần render → effect chỉ chạy đúng 1 lần lúc mount, không bao giờ chạy lại nữa (trừ khi component unmount rồi mount lại).

## 2.6. Bug thực tế: đọc state ngay sau khi gọi effect, chưa đợi data về

```jsx
function AdminNavBar() {
  const [currentInfo, setCurrentInfo] = useState(null);

  useEffect(() => {
    const fetchInfo = async () => {
      const response = await authService.getMe(); // bất đồng bộ (async)
      setCurrentInfo(response.data);
    };
    fetchInfo();
  }, []);

  console.log(currentInfo.email); // 💥 Uncaught TypeError: Cannot read properties of null
}
```

**Phân tích nguyên nhân — thứ tự thực tế xảy ra:**

```
1. Component render lần 1 → currentInfo = null (giá trị khởi tạo)
2. Dòng console.log(currentInfo.email) NẰM NGOÀI useEffect
   → thuộc GIAI ĐOẠN RENDER → chạy NGAY LẬP TỨC
   → currentInfo vẫn đang null → 💥 CRASH ngay tại đây
3. (Nếu không crash) useEffect mới chạy SAU KHI render xong
   → gọi API (bất đồng bộ, mất thời gian) → có data → setCurrentInfo(data)
   → trigger render lần 2 → lúc này currentInfo mới thực sự có giá trị
```

Đây là bằng chứng sống cho thấy **Giai đoạn Render và Giai đoạn Effect tách biệt hoàn toàn về mặt thời điểm**, không xảy ra đồng thời — dù bạn debug bằng cách đặt breakpoint bên trong `fetchInfo` và thấy data đúng, dòng crash lại nằm ở 1 thời điểm hoàn toàn khác (sớm hơn), thuộc giai đoạn render.

**Cách khắc phục — luôn kiểm tra tồn tại (guard) trước khi dùng state có thể null:**

```jsx
function AdminNavBar() {
  const [loading, setLoading] = useState(true);
  const [currentInfo, setCurrentInfo] = useState(null);

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        setLoading(true);
        const response = await authService.getMe();
        setCurrentInfo(response.data);
      } catch (error) {
        console.error("Lỗi:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchInfo();
  }, []);

  if (loading) return <div>Đang tải...</div>;
  if (!currentInfo) return null;

  return <div>{currentInfo.email}</div>; // an toàn, chắc chắn currentInfo tồn tại ở đây
}
```

> **Nguyên tắc chung:** bất cứ state nào khởi tạo `null`/`undefined` và sẽ được điền dữ liệu từ 1 side-effect (fetch API), **mọi chỗ dùng state đó trong JSX/render đều phải kiểm tra tồn tại trước** — bằng `if (!data) return null`, optional chaining (`data?.field`), hoặc dùng cờ `loading` để chặn hẳn việc render nội dung phụ thuộc data khi chưa sẵn sàng.

## 2.7. Cleanup function — dọn dẹp trước khi effect chạy lại hoặc component unmount

Một phần quan trọng của `useEffect` chưa nhắc tới: hàm callback truyền vào `useEffect` **có thể return ra 1 hàm khác**, gọi là **cleanup function**:

```jsx
useEffect(() => {
  // ... code effect chính ...

  return () => {
    // cleanup: chạy TRƯỚC khi effect chạy lại lần sau, hoặc khi component unmount
  };
}, [deps]);
```

**Vì sao cần cleanup?** Nhiều side-effect tạo ra "tài nguyên sống" cần được giải phóng đúng lúc — nếu không, sẽ rò rỉ bộ nhớ hoặc hành vi lạ.

### Ví dụ: đăng ký sự kiện resize window

```jsx
function WindowWidth() {
  const [width, setWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWidth(window.innerWidth);
    window.addEventListener("resize", handleResize);

    // Cleanup: gỡ event listener khi component unmount
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return <div>Width: {width}</div>;
}
```

Nếu **thiếu** dòng cleanup, mỗi lần component này mount lại (ví dụ chuyển route đi rồi quay lại), 1 listener mới lại được đăng ký chồng lên listener cũ chưa được gỡ — dẫn đến hàm `handleResize` bị gọi nhiều lần trùng lặp mỗi khi resize, gây bug khó phát hiện.

### Ví dụ: hủy request cũ khi tham số fetch đổi quá nhanh (chống race condition)

```jsx
useEffect(() => {
  let cancelled = false;

  const fetchData = async () => {
    const result = await api.get(queryParam);
    if (!cancelled) {          // chỉ set state nếu effect này CHƯA bị "hủy"
      setData(result);
    }
  };
  fetchData();

  return () => {
    cancelled = true;          // đánh dấu hủy khi effect chạy lại (queryParam đổi) hoặc unmount
  };
}, [queryParam]);
```

Tình huống cần cleanup này: người dùng gõ ô tìm kiếm rất nhanh, mỗi ký tự gõ ra kích hoạt effect chạy lại (do `queryParam` đổi). Nếu request cũ (cho ký tự gõ trước) **trả về sau** request mới (cho ký tự gõ sau), dữ liệu hiển thị sẽ bị "lùi" về kết quả cũ, sai lệch với ô tìm kiếm hiện tại. Cờ `cancelled` đảm bảo chỉ request **mới nhất** mới được phép cập nhật state.

### Khi nào cleanup chạy — timeline đầy đủ

```
Component mount → effect chạy (lần 1, không có cleanup nào trước đó để chạy)
     ↓
deps đổi → React CHẠY CLEANUP CỦA LẦN TRƯỚC trước tiên → rồi mới chạy effect mới (lần 2)
     ↓
deps đổi lần nữa → CHẠY CLEANUP CỦA LẦN 2 → rồi chạy effect mới (lần 3)
     ↓
Component unmount (bị gỡ khỏi màn hình, VD do chuyển route) → CHẠY CLEANUP CUỐI CÙNG
```

## 2.8. Refresh trang (F5) có chạy lại `useEffect([])` không?

**Có — nhưng lý do khác hẳn với "dependency đổi".** Cần phân biệt rõ 2 khái niệm dễ nhầm lẫn:

| | Re-render | Refresh trang (F5) |
|---|---|---|
| Là gì | React gọi lại hàm component | Trình duyệt xóa sạch, tải lại toàn bộ trang từ đầu |
| "Sổ" state của React | **Được giữ nguyên**, chỉ update theo `setState` | **Bị xóa sạch hoàn toàn**, mất trắng |
| `useEffect` có chạy lại? | Tùy theo mảng deps có đổi hay không | **Luôn chạy lại**, không cần xét deps |
| Bản chất | Component vẫn "sống", chỉ tính toán lại UI | Component cũ **chết hẳn**, 1 component **hoàn toàn mới** được tạo ra |

`useEffect(fn, [])` không có nghĩa là *"chạy 1 lần duy nhất trong toàn bộ lịch sử tồn tại của app"*, mà chính xác hơn là **"chạy 1 lần mỗi khi component này được mount (sinh ra) mới"**. F5 xóa sạch tiến trình cũ, tạo lại từ đầu — tính là 1 lượt "mount mới toanh" → effect tự nhiên chạy lại, không phải vì dependency đổi, mà vì **toàn bộ vòng đời component bắt đầu lại từ số 0**.

Điều này cũng áp dụng khi component bị **unmount rồi mount lại** vì lý do khác F5 — ví dụ chuyển route đi trang khác rồi quay lại trang cũ (trong React Router), component đó unmount lúc rời đi và mount lại (như mới) lúc quay về, `useEffect([])` cũng sẽ chạy lại, dù không hề có F5 nào xảy ra.

## 2.9. Tóm tắt Phần 2

> `useEffect` là cách khai báo: *"việc này không phải để tính UI, hãy đợi UI vẽ xong rồi mới làm, và chỉ làm lại khi những giá trị tôi liệt kê trong mảng thực sự đổi khác so với lần trước — và nếu cần dọn dẹp trước khi làm lại (hoặc trước khi component biến mất), hãy return ra 1 hàm cleanup."*

## 2.10. Bài tập tự kiểm tra Phần 2

1. Liệt kê 3 việc là side-effect và 2 việc là thuần túy, không được trùng với ví dụ trong bài.
2. Cho đoạn code:
```jsx
useEffect(() => {
  console.log("chạy!");
}, [a, b, c]);
```
Nếu ở lần render trước `a=1, b="x", c={}` (object rỗng), lần render này `a=1, b="x", c={}` (1 object rỗng khác được tạo mới) — effect có chạy lại không? Vì sao?

3. Sửa lỗi trong đoạn code sau (đang bị vòng lặp vô hạn):
```jsx
function UserList() {
  const [users, setUsers] = useState([]);
  userService.getAll().then(res => setUsers(res.data));
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

4. Viết 1 `useEffect` có cleanup dùng `setInterval` để tăng biến đếm mỗi giây, đảm bảo không bị rò rỉ interval khi component unmount.

5. Giải thích: tại sao khi bấm F5, `useEffect([])` chạy lại, dù mảng deps `[]` "không đổi gì cả" so với trước đó?

---

# PHẦN 3 — `useCallback`: GIỮ "HỘP FUNCTION" ỔN ĐỊNH QUA NHIỀU LẦN RENDER

## 3.1. Vấn đề gốc: `===` với function/object/array "khó tính" hơn tưởng

```js
// Với giá trị nguyên thủy — so sánh theo GIÁ TRỊ
console.log(1 === 1);            // true
console.log("hi" === "hi");      // true

// Với object/array/function — so sánh theo ĐỊA CHỈ TRONG BỘ NHỚ, không phải nội dung
console.log({} === {});                   // false! (2 object khác nhau, dù đều rỗng)
console.log([1, 2] === [1, 2]);            // false!
console.log((() => {}) === (() => {}));    // false! (2 function khác nhau, dù code y hệt)
```

Mỗi lần bạn viết `{}`, `[]`, hoặc `() => {}` trong code, JS **tạo ra 1 "hộp" mới trong bộ nhớ**, dù nội dung bên trong giống hệt lần trước. Toán tử `===` khi so sánh 2 object/array/function chỉ kiểm tra: **"2 biến này có đang trỏ vào CÙNG MỘT hộp vật lý hay không?"** — nó hoàn toàn không quan tâm nội dung bên trong 2 hộp có giống nhau đến đâu.

## 3.2. Hệ quả: function bị coi là "luôn mới" mỗi lần re-render

```jsx
function Demo() {
  const [count, setCount] = useState(0);

  const greet = () => { console.log("Xin chào!"); }; // tạo hộp MỚI mỗi lần Demo() chạy

  useEffect(() => {
    console.log("Effect chạy vì greet đổi hộp!");
  }, [greet]);

  return <button onClick={() => setCount(count + 1)}>Count: {count}</button>;
}
```

### Diễn biến chi tiết từng bước

**Render 1 (component vừa mount):**

Dòng `const greet = () => {...}` chạy → JS tạo **Hộp A** trong bộ nhớ. Biến `greet` trỏ vào Hộp A.

```
Bộ nhớ:  [Hộp A: function greet]
Biến greet (render 1)  ───────► Hộp A
```

`useEffect(fn, [greet])` — đây là lần đầu, chưa có gì để so sánh → **chắc chắn chạy** (đúng quy tắc "mount đầu luôn chạy"). Console in: `"Effect chạy vì greet đổi hộp!"`. React ghi vào sổ: *"deps của effect này ở lần render vừa rồi là `[Hộp A]"`.*

**Bấm nút, render 2 (`setCount(1)` được gọi):**

React gọi lại toàn bộ `Demo()` từ đầu. Dòng `const greet = () => {...}` **chạy lại**, vì nó nằm trong thân hàm — thân hàm luôn chạy lại toàn bộ mỗi lần render. JS **lại tạo ra 1 hộp function mới**, gọi là **Hộp B** — dù nội dung logic bên trong (`console.log("Xin chào!")`) giống Hộp A y hệt, nhưng đây là **2 hộp khác nhau, nằm ở 2 địa chỉ khác nhau trong RAM**.

```
Bộ nhớ:  [Hộp A: (cũ, không ai trỏ tới)]  [Hộp B: function greet (mới)]
Biến greet (render 2)  ─────────────────────────────────────► Hộp B
```

React lấy deps đã lưu (`[Hộp A]`) so với deps lần này (`[Hộp B]`):

```
Hộp A === Hộp B  →  FALSE (2 địa chỉ khác nhau)
```

→ React kết luận *"deps đã đổi"* (dù về mặt logic, người viết code không hề có ý định đổi gì) → **effect chạy lại**, in thêm 1 dòng nữa.

**Bấm nút thêm lần nữa (render 3):** lại tạo **Hộp C** mới → so với **Hộp B** đã lưu → khác nhau → effect lại chạy lại.

### Kết quả thực tế

Nếu bạn bấm nút 5 lần, console sẽ in ra dòng "Effect chạy..." **5 lần** — dù về mặt logic, `greet` **chẳng có gì thay đổi cả**, code bên trong nó y hệt nhau tuyệt đối qua mọi lần render. Vấn đề hoàn toàn nằm ở việc **JS tạo hộp function mới mỗi lần thân hàm chạy lại**, không phải logic sai.

## 3.3. `useCallback` — cơ chế "tái dùng hộp cũ" khi deps không đổi

```jsx
const greet = useCallback(() => {
  console.log("Xin chào!");
}, []); // deps rỗng: hàm này không đọc biến nào từ ngoài
```

**Render 1:** Chạy tới `useCallback(fn, [])`. Đây là lần đầu, sổ của React chưa có gì để so → React tạo **Hộp A**, đồng thời **tự lưu vào sổ riêng của nó**: *"Đây là hộp function tôi đang giữ cho `greet`, deps lúc tạo ra nó là `[]"`.* Biến `greet` = Hộp A.

**Bấm nút, render 2:** Chạy tới `useCallback(fn, [])` lần nữa. Lần này, `useCallback` **không vội tạo hộp mới** — nó làm 1 bước trung gian trước: so sánh **deps hiện tại** (`[]`) với **deps đã lưu trong sổ** (`[]`).

```
So sánh:  [] (lần này) với [] (đã lưu)
→ không có phần tử nào để so → coi là GIỐNG NHAU
```

Vì giống nhau, `useCallback` quyết định: *"Không cần tạo hộp mới, trả về nguyên Hộp A đã lưu trong sổ."* Dòng `() => {...}` bên trong `useCallback` về mặt cú pháp JS vẫn "được viết ra", nhưng `useCallback` **âm thầm vứt bỏ kết quả mới tạo ra (nếu có), trả về hộp cũ thay vào**.

```
Biến greet (render 2)  ───────────────────────────────► Hộp A (CHÍNH LÀ hộp cũ)
```

`useEffect` kiểm tra deps: `Hộp A (đã lưu) === Hộp A (lần này)` → cùng địa chỉ → `TRUE` → **effect không chạy lại**. Console im lặng, không in gì thêm.

Bấm nút bao nhiêu lần nữa cũng vậy — vì deps của `useCallback` luôn là `[]` (không đổi), nó luôn trả về đúng Hộp A từ đầu đến cuối, `useEffect` luôn thấy "giống hệt", không bao giờ chạy lại nữa.

### So sánh trực quan 2 kịch bản

```
KHÔNG useCallback:
Render 1 → Hộp A
Render 2 → Hộp B (mới)  →  A ≠ B  → effect chạy lại
Render 3 → Hộp C (mới)  →  B ≠ C  → effect chạy lại
Render 4 → Hộp D (mới)  →  C ≠ D  → effect chạy lại
                                     (không hồi kết, dù logic không đổi gì)

CÓ useCallback (deps = []):
Render 1 → Hộp A (tạo mới, deps=[] chưa có gì so)
Render 2 → so [] với [] → giống → TRẢ VỀ LẠI Hộp A (không tạo mới) → effect KHÔNG chạy
Render 3 → so [] với [] → giống → TRẢ VỀ LẠI Hộp A                  → effect KHÔNG chạy
Render 4 → so [] với [] → giống → TRẢ VỀ LẠI Hộp A                  → effect KHÔNG chạy
```

## 3.4. Ví dụ deps có giá trị thực (không rỗng)

```jsx
function Demo() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState("An");

  const greet = useCallback(() => {
    console.log(`Xin chào, ${name}!`);
  }, [name]); // deps có 1 phần tử: name

  useEffect(() => {
    console.log("Effect chạy vì greet đổi hộp!");
  }, [greet]);

  return <button onClick={() => setCount(count + 1)}>Count: {count}</button>;
}
```

**Render 1:** `name = "An"`. `useCallback` tạo Hộp A, lưu vào sổ kèm: *"deps lúc tạo Hộp A là `["An"]"`.*

**Bấm nút tăng `count` (không đụng `name`), render 2:**
```
deps hiện tại: [name] = ["An"]  (vì name chưa đổi)
So phần tử [0]: "An" (lần này) vs "An" (đã lưu)
→ string, so theo GIÁ TRỊ → "An" === "An" → TRUE, giống nhau
→ useCallback KHÔNG tạo hộp mới, trả về lại Hộp A
```

`useEffect` thấy `greet` vẫn là Hộp A như cũ → không chạy lại. Hợp lý: bấm nút tăng count không liên quan gì đến `name`/`greet`.

**Gọi `setName("Bình")`, render 3:**
```
deps hiện tại: [name] = ["Bình"]
So phần tử [0]: "Bình" (lần này) vs "An" (đã lưu)
→ "Bình" === "An" → FALSE, khác nhau!
→ useCallback TẠO HỘP MỚI (Hộp B), vì nội dung hàm giờ cần dùng "Bình" chứ không phải "An"
```

`useEffect` thấy `greet` giờ là Hộp B ≠ Hộp A → **chạy lại effect**. Hợp lý: vì `name` đổi, hàm `greet` cần "làm mới" nội dung, hợp lý coi đây là function "khác" về mặt logic.

> ⚠️ **Lỗi kinh điển — Stale Closure:** nếu quên khai báo `name` vào deps (`useCallback(fn, [])` thay vì `useCallback(fn, [name])`), hàm `greet` sẽ **"đóng băng" mãi mãi với giá trị `name` của lần tạo đầu tiên** ("An"). Dù sau đó `name` đổi thành "Bình", hàm cũ (không được tạo lại vì deps rỗng không bao giờ đổi) vẫn cứ in ra `"Xin chào, An!"` — vì bên trong hộp function cũ đó, nó đã "chụp" (closure) lấy giá trị `name` tại thời điểm nó được tạo ra, không "nhìn thấy" giá trị `name` mới sau này.

## 3.5. Phân biệt: cơ chế so sánh vs mục đích của `useCallback` và `useEffect`

Đây là điểm **hay nhầm nhất** khi mới học 2 hook này cùng lúc.

**Cơ chế so sánh deps: HOÀN TOÀN GIỐNG NHAU** giữa `useCallback` và `useEffect` (và cả `useMemo`, sẽ nhắc ở mục 3.8) — đều tháo mảng deps ra, so từng phần tử theo đúng quy tắc (nguyên thủy: theo giá trị / object-array-function: theo địa chỉ hộp).

**Mục đích: KHÁC NHAU HOÀN TOÀN** — khác biệt nằm ở **"React làm gì SAU KHI so sánh xong"**:

| | `useEffect(fn, deps)` | `useCallback(fn, deps)` |
|---|---|---|
| Câu hỏi nó trả lời | "Có nên **chạy (execute)** hàm `fn` lúc này không?" | "Có nên **tạo hộp function mới**, hay đưa lại hộp cũ?" |
| Deps giống lần trước | **Không chạy** hàm `fn` (bỏ qua side-effect) | **Không tạo hộp mới** — trả về hộp cũ (nhưng hàm bên trong hoàn toàn KHÔNG được gọi/chạy) |
| Deps khác lần trước | **Chạy** hàm `fn` (thực thi side-effect: gọi API, sửa DOM...) | **Tạo hộp mới**, lưu hộp mới này thay cho hộp cũ trong sổ |
| Bản chất `fn` truyền vào | 1 hành động cần **thực thi** (do something) | 1 **giá trị** (function object) cần **giữ nguyên hoặc thay mới** — bản thân nó KHÔNG được tự động gọi ra chạy |

> **Điểm mấu chốt:** `useCallback` **không bao giờ tự động "gọi ra chạy"** cái hàm bạn đưa vào — nó chỉ đơn thuần trả về "hộp chứa hàm đó" để bạn tự gọi (`greet()`) ở đâu đó khác. Còn `useEffect` thì ngược lại: khi deps đổi, nó **tự động thực thi ngay** hàm bên trong.

**Loại suy dễ nhớ ("Kho hàng"):**

- `useCallback` giống 1 **người quản kho function**: *"Deps không đổi thì tôi đưa lại đúng cái hộp cũ, đỡ phải đóng gói hộp mới làm gì cho tốn công."* — Nó chỉ lo việc **có nên tạo/giữ hộp**, không quan tâm hộp đó có được ai mở ra dùng hay không.
- `useEffect` giống 1 **người thực thi lệnh**: *"Deps đổi thì tôi làm việc ngay (gọi API, sửa DOM...), deps không đổi thì tôi đứng yên không làm gì."* — Nó lo việc **có nên hành động**, không tạo ra hộp gì cả.

## 3.6. Deps của mảng — làm rõ lại 1 hiểu lầm phổ biến

Câu hỏi hay gặp: *"Deps `[a, b, c]` được so sánh như 1 khối, hay từng phần tử riêng?"*

**Trả lời: React KHÔNG so sánh cả mảng như 1 khối.** Bản thân mảng `[a, b, c]` mỗi lần viết ra cũng là 1 "hộp mới" (đúng quy tắc ở mục 3.1) — nếu so cả mảng theo `===`, kết quả sẽ luôn là "khác nhau" vô nghĩa. React **luôn mở mảng deps ra, so từng phần tử ở đúng vị trí index** với phần tử tương ứng của lần render trước, và mỗi phần tử áp dụng đúng quy tắc so sánh theo kiểu dữ liệu của chính nó (string/number/boolean: theo giá trị — object/array/function: theo địa chỉ hộp).

## 3.7. Khi nào THỰC SỰ cần `useCallback`?

> **Chỉ cần khi function đó được dùng làm dependency của cái khác** (`useEffect`, `useMemo`, hoặc truyền xuống 1 component con có tối ưu bằng `React.memo`).

```jsx
// ❌ Không cần useCallback — không ai đem handleClick ra so === cả
const handleClick = useCallback(() => {
  console.log("clicked");
}, []); // dư thừa, chỉ tổ code dài hơn, không thay đổi hành vi chạy

// ✅ Viết bình thường là đủ
const handleClick = () => {
  console.log("clicked");
};
```

Nếu 1 function đứng 1 mình, không có "người tiêu thụ" nào (effect/memo/component con) so sánh `===` với nó → `useCallback` **hoàn toàn không có tác dụng thực tế nào cả**, chỉ tốn thêm chút hiệu năng để React tự quản lý việc so sánh, đổi lại không thu được lợi ích gì.

**Quy tắc thực dụng để tự hỏi:** *"Function này có đang nằm trong mảng deps của `useEffect`/`useMemo` nào không, hoặc có đang được truyền xuống component con dùng `React.memo` không?"* — Có thì nên dùng `useCallback`. Không thì bỏ qua, viết function bình thường.

## 3.8. Sơ lược `useMemo` — người anh em gần của `useCallback`

Không đi sâu (nằm ngoài phạm vi giáo trình này), nhưng nên biết để tránh nhầm lẫn: `useMemo` hoạt động **hoàn toàn tương tự** `useCallback` về cơ chế so sánh deps, chỉ khác ở chỗ nó dùng để "ghi nhớ 1 **giá trị** được tính toán tốn kém" (thay vì ghi nhớ 1 **function**):

```jsx
// useCallback: ghi nhớ 1 HỘP FUNCTION
const greet = useCallback(() => { ... }, [deps]);

// useMemo: ghi nhớ 1 GIÁ TRỊ đã tính toán (kết quả trả về từ 1 hàm được gọi NGAY LẬP TỨC)
const total = useMemo(() => computeExpensiveTotal(items), [items]);
```

Thực chất, `useCallback(fn, deps)` tương đương về mặt logic với `useMemo(() => fn, deps)` — cả 2 đều dùng chung 1 cơ chế "sổ ghi nhớ + so sánh deps", chỉ khác nhau ở chỗ giữ lại cái gì (hộp function nguyên vẹn, hay kết quả đã tính ra).

## 3.9. Tóm tắt Phần 3

> `useCallback` giống 1 người thư ký: mỗi lần bạn đưa cho họ 1 function mới soạn ra, họ **không vội đưa luôn cho khách**. Họ hỏi trước: *"Deps lần này có gì khác lần trước không?"* — Nếu không khác gì, họ **giấu function mới vừa soạn đi, lấy bản cũ trong tủ ra đưa cho khách thay thế**. Khách (ở đây là `useEffect`) nhận được đúng y hộp cũ, nên nó nghĩ "không có gì đổi cả", yên tâm không làm gì thêm.

## 3.10. Bài tập tự kiểm tra Phần 3

1. Giải thích vì sao `{} === {}` cho ra `false`, nhưng `"a" === "a"` cho ra `true`.
2. Cho đoạn code, component `Demo` re-render 4 lần liên tiếp (do bấm nút đổi `count`, không đổi gì khác). Hỏi: `greet` được tạo bao nhiêu "hộp" mới tổng cộng, nếu (a) không dùng `useCallback`, (b) có dùng `useCallback` với deps `[]`?
3. Function nào trong 2 function sau **cần** `useCallback`, function nào **không cần**? Giải thích.
```jsx
function Parent() {
  const [count, setCount] = useState(0);

  const logSomething = () => console.log("log"); // (A) — không truyền đi đâu cả

  const fetchData = () => api.get("/data");        // (B)

  useEffect(() => {
    fetchData();
  }, [fetchData]); // (B) được dùng làm dep ở đây

  return <button onClick={logSomething}>Click</button>;
}
```
4. Điều gì xảy ra nếu bạn viết `useCallback(fn, [name])` nhưng bên trong `fn` lại dùng biến `age` (không có trong deps)? Đây gọi là lỗi gì?
5. Phân biệt bằng lời của bạn: `useCallback` và `useEffect` dùng chung cơ chế so sánh deps, nhưng mục đích cuối cùng của chúng khác nhau ở điểm nào?

---

# PHẦN 4 — KẾT HỢP CẢ 3 HOOK: PATTERN "CUSTOM HOOK FETCH DATA"

Đây là ứng dụng thực tế phổ biến nhất kết hợp cả 3 hook — dùng để xây 1 hook tái sử dụng, gọi API và trả về trạng thái `loading`/`data`/`error`.

## 4.1. Bài toán

Nhiều trang trong 1 ứng dụng đều cần lặp lại cùng 1 logic: gọi API, quản lý trạng thái đang tải, xử lý lỗi, lưu dữ liệu trả về. Thay vì viết lặp lại logic này ở mỗi trang, ta đóng gói thành **1 custom hook** dùng chung.

## 4.2. Xây dựng từng bước (gợi ý tự làm trước khi xem đáp án)

**Bước 1** — Xác định trạng thái cần "nhớ" qua các lần render: quá trình fetch API luôn trải qua 3 trạng thái — đang tải, tải xong có data, hoặc tải lỗi. → Ứng viên cho `useState`.

**Bước 2** — Việc gọi API có phải "tính toán UI" không? → Không, đây là side-effect → phải đặt trong `useEffect`, không đặt thẳng trong thân hàm.

**Bước 3** — Hàm gọi API có cần chạy lại theo điều kiện gì? → Tùy nhu cầu: chỉ 1 lần lúc mount (`[]`), hoặc chạy lại khi tham số tìm kiếm đổi (`[queryParam]`).

**Bước 4** — Function gọi API có bị "tạo hộp mới" mỗi lần render, gây `useEffect` hiểu nhầm deps đổi liên tục không? → Nếu hàm gọi API được **truyền vào từ bên ngoài** làm tham số của custom hook, và hàm đó lại nằm trong deps của `useEffect` bên trong hook → cần `useCallback` ở phía người dùng hook, để giữ tham chiếu ổn định.

## 4.3. Đáp án tham khảo

```jsx
// hooks/useFetch.jsx
import { useState, useEffect, useCallback } from "react";

function useFetch(apiFunction) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const execute = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiFunction();
      setData(result);
    } catch (err) {
      setError(err.response?.data?.detail || "Lỗi: " + err.message);
    } finally {
      setLoading(false);
    }
  }, [apiFunction]); // execute chỉ tạo hộp mới khi apiFunction (từ bên ngoài) đổi hộp

  useEffect(() => {
    execute();
  }, [execute]); // effect chỉ chạy lại khi execute thực sự đổi hộp

  return { loading, data, error, refetch: execute };
}

export default useFetch;
```

```jsx
// pages/Timelines.jsx
import { useCallback, useState } from "react";
import useFetch from "../hooks/useFetch";
import { timelineService } from "../services/timelineService";

function Timelines() {
  const [queryParam, setQueryParam] = useState({ title: "", skip: 0, limit: 10 });

  // Bọc bằng useCallback vì hàm này được TRUYỀN VÀO useFetch,
  // nơi nó sẽ nằm trong deps của 1 useEffect khác
  const fetchFunction = useCallback(() => {
    return timelineService.get(queryParam);
  }, [queryParam]);

  const { loading, data, error, refetch } = useFetch(fetchFunction);

  if (loading) return <div>Đang tải...</div>;
  if (error) return <div>Lỗi: {error}</div>;

  return (
    <div>
      {data.map(item => <div key={item.id}>{item.title}</div>)}
    </div>
  );
}
```

## 4.4. Truy vết chuỗi domino khi `queryParam` đổi

```
1. setQueryParam(newValue) → Timelines re-render
2. useCallback thấy queryParam (dep) đổi → tạo fetchFunction MỚI (hộp B)
3. Bên trong useFetch: useCallback thấy apiFunction (chính là fetchFunction) đổi (hộp B ≠ hộp A cũ)
   → tạo execute MỚI (hộp mới)
4. useEffect thấy execute đổi hộp → CHẠY LẠI → gọi API mới với queryParam mới
5. setData(result) → re-render → hiển thị data mới lên UI
```

→ Đây chính là cách 1 hệ thống "search/filter tự động gọi API lại khi query đổi" hoạt động — hoàn toàn không cần tự viết logic "khi nào nên fetch lại", chuỗi dependency tự lo hết, miễn là bạn khai báo `useCallback` đúng chỗ.

## 4.5. Nếu bỏ `useCallback` ở `fetchFunction` thì sao?

```jsx
// ❌ Bỏ useCallback
const fetchFunction = () => {
  return timelineService.get(queryParam);
};
```

Mỗi lần `Timelines` re-render (kể cả vì lý do hoàn toàn không liên quan đến `queryParam`), `fetchFunction` sẽ là **hộp mới** → `execute` bên trong `useFetch` cũng thành hộp mới → `useEffect` thấy đổi → gọi lại API → `setData`/`setLoading` → re-render → lại tạo hộp mới → **vòng lặp vô hạn gọi API liên tục**, y hệt bug đã phân tích ở Phần 3.

## 4.6. Giới hạn của pattern tự viết này (để biết, không cần khắc phục ngay)

1. **Không chống race condition** — nếu `queryParam` đổi rất nhanh liên tục (gõ tìm kiếm), request cũ có thể trả về sau request mới, hiển thị sai. Khắc phục bằng cleanup function (`cancelled` flag) như học ở mục 2.7.
2. **Không cache** — mỗi lần component mount lại, gọi API lại từ đầu dù data cũ vẫn còn hợp lệ.
3. Các thư viện chuyên dụng như **React Query / SWR** giải quyết đúng 2 vấn đề trên (và nhiều vấn đề khác: retry tự động, đồng bộ data giữa nhiều nơi dùng chung...) — nhưng nên **tự tay viết được pattern này trước**, hiểu rõ nó đang giải quyết bài toán gì, rồi mới học thư viện chuyên dụng sẽ hiệu quả hơn nhiều so với dùng ngay từ đầu như 1 "hộp đen".

---

# PHẦN 5 — TỔNG KẾT & TRA CỨU NHANH (CHEAT SHEET)

## 5.1. Bảng liên kết logic cả 3 hook

| Hook | Vấn đề nó giải quyết | Nếu không dùng thì sao |
|---|---|---|
| `useState` | Hàm component chạy lại nhiều lần nhưng cần "nhớ" dữ liệu xuyên suốt | Dữ liệu reset về ban đầu mỗi lần render, không lưu trạng thái gì được |
| `useEffect` | Có việc (side-effect) không nên chạy giữa lúc tính UI, cần chạy sau khi vẽ xong, và chỉ chạy lại khi cần | Side-effect chạy loạn xạ mỗi lần render → vòng lặp vô hạn, spam server |
| `useCallback` | Function bị coi là "luôn mới" mỗi lần render (do `===` so theo địa chỉ bộ nhớ), gây `useEffect` hiểu nhầm deps đổi liên tục | `useEffect` phụ thuộc function đó sẽ chạy lại vô tội vạ, dù logic bên trong không hề đổi |

## 5.2. Câu hỏi tự hỏi khi viết code (quy tắc thực dụng)

- **Đang cần lưu 1 giá trị mà UI phải vẽ lại theo?** → `useState`
- **Đang làm 1 việc "thò ra ngoài" (gọi API, sửa DOM tay, đăng ký sự kiện)?** → đặt trong `useEffect`, không đặt thẳng trong thân hàm
- **Effect có tạo ra tài nguyên cần dọn (event listener, interval, request đang chạy)?** → nhớ return cleanup function
- **Function có đang nằm trong deps của `useEffect`/`useMemo` khác, hoặc truyền cho component con dùng `React.memo`?** → cân nhắc `useCallback`. Nếu không, bỏ qua.

## 5.3. Lỗi thường gặp và cách nhận diện

| Triệu chứng | Nguyên nhân thường gặp |
|---|---|
| Component gọi API liên tục không dừng (xem tab Network thấy spam request) | Gọi API thẳng trong thân hàm, hoặc quên `useCallback` cho function truyền vào `useEffect`/custom hook |
| `Cannot read properties of null/undefined` ngay khi component vừa mount | Đọc state (được set trong `useEffect` bất đồng bộ) ở ngoài `useEffect`, tại giai đoạn render — chưa kịp có data |
| Function trong `useEffect`/`useCallback` cứ in ra giá trị "cũ", dù state đã đổi | Thiếu khai báo dependency (stale closure) — hàm bị "đóng băng" với giá trị tại lúc nó được tạo |
| UI không cập nhật dù chắc chắn dữ liệu đã đổi trong bộ nhớ | Sửa biến trực tiếp (`obj.field = x`) thay vì gọi `setState`, khiến React không hề "biết" mà render lại |
| Bấm nhiều lần liên tiếp trong 1 sự kiện, giá trị chỉ tăng đúng 1 lần thay vì N lần | Dùng `setState(value)` thay vì `setState(prev => ...)` khi giá trị mới phụ thuộc giá trị cũ |
| Sau khi rời trang rồi quay lại, có nhiều event listener/interval chạy trùng lặp | Thiếu cleanup function trong `useEffect` |

## 5.4. Thuật ngữ tra cứu nhanh

| Thuật ngữ | Ý nghĩa |
|---|---|
| **Re-render** | React gọi lại hàm component để tính toán UI mới |
| **Mount** | Lần đầu tiên 1 component được tạo ra và đưa vào DOM |
| **Unmount** | Component bị gỡ khỏi DOM (VD: đổi route, component cha không còn render nó nữa) |
| **Side-effect** | Hành động "thò ra ngoài" phạm vi hàm thuần túy (gọi API, sửa DOM tay, timer...) |
| **Dependency array (deps)** | Mảng liệt kê các giá trị mà hook cần theo dõi để quyết định có chạy lại/tạo lại hay không |
| **Stale closure** | Lỗi khi 1 function "đóng băng" với giá trị biến tại thời điểm nó được tạo, do thiếu khai báo dependency đúng |
| **Cleanup function** | Hàm trả về từ bên trong `useEffect`, chạy trước khi effect chạy lại lần sau hoặc khi component unmount |
| **Race condition** | Tình huống 2 thao tác bất đồng bộ (VD: 2 request API) hoàn thành không theo đúng thứ tự mong muốn, gây dữ liệu sai lệch |
| **Batching** | React gộp nhiều lệnh `setState` liên tiếp trong cùng 1 sự kiện lại, chỉ render 1 lần cho tối ưu |

---

# PHỤ LỤC — GHI CHÚ VỀ NGUỒN GỐC TÀI LIỆU

Giáo trình này được biên soạn dựa trên 1 buổi trao đổi hỏi-đáp sâu về bản chất 3 hook, mở rộng thêm các phần chưa được đào sâu trong buổi trao đổi gốc (functional update, mutate trực tiếp, cleanup function, race condition, `useMemo`) để hoàn chỉnh thành tài liệu tự học độc lập.

**Gợi ý cách dùng lại tài liệu này về sau:**
1. Đọc lại phần **Tóm tắt** cuối mỗi Phần trước, thử tự giải thích lại bằng lời của mình.
2. Làm **Bài tập tự kiểm tra** cuối mỗi Phần mà không xem lại nội dung.
3. Nếu vướng, quay lại đúng mục con liên quan (không cần đọc lại từ đầu).
4. Dùng **Phần 5 (Cheat Sheet)** để tra cứu nhanh khi đang code, không cần đọc lại toàn bộ lý thuyết.
