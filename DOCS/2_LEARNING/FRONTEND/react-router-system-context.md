# `🎯 Note về liên hệ giữa Context và Router`

### Ví dụ đang áp dụng: Context system chứa các giá trị của system config.

## Phần 1 — React render mọi thứ như thế nào

**JSX không phải là "chạy code từ trên xuống dưới" như bạn viết. JSX chỉ là cú pháp để tạo ra một cây object (gọi là Element Tree).**

Khi bạn viết:

```jsx
<div>
  <Header />
  <Content />
</div>
```

React không "chạy" `<div>` rồi "chạy" `<Header/>` theo nghĩa thực thi tuần tự dòng lệnh. Nó tạo ra một **cây mô tả** (giống JSON):

```js
{
  type: "div",
  children: [
    { type: Header, props: {} },
    { type: Content, props: {} }
  ]
}
```

Sau đó React mới đi **duyệt cây này** và với mỗi node có `type` là component (chữ hoa, như `Header`), nó mới thực sự gọi function đó ra để lấy JSX con của nó, rồi lại duyệt tiếp — đệ quy xuống tới khi toàn bộ cây chỉ còn thẻ HTML thuần (`div`, `span`,...).

**Vì sao điều này quan trọng?** Vì nó giải thích tại sao vị trí bạn đặt component trong cây JSX quyết định _quan hệ cha-con thực sự_, và quan hệ cha-con này chính là thứ Context dựa vào để hoạt động (Phần 2), và cũng là thứ khiến `<Routes>` cư xử đặc biệt (Phần 3).

---

## Phần 2 — React Context:

### 2.1 Vấn đề Context giải quyết: Prop Drilling

Không có Context, muốn truyền dữ liệu (VD: thông tin user đã login) từ `App` xuống 1 component nằm sâu 5 tầng, bạn phải truyền qua props ở **từng tầng trung gian**, kể cả tầng đó không dùng dữ liệu này — chỉ "chuyển tiếp" hộ. Gọi là _prop drilling_, code rất bẩn khi cây sâu.

### 2.2 Context giải quyết bằng cách nào

Context tạo ra một "kênh truyền dữ liệu" đi tắt xuyên qua cây, không cần đi qua từng props trung gian. Có 3 mảnh ghép:

```js
const MyContext = createContext(defaultValue); // 1. Tạo "kênh"
```

```jsx
<MyContext.Provider value={someValue}>
  {" "}
  {/* 2. "Bơm" giá trị vào kênh, cho 1 nhánh cây */}
  {children}
</MyContext.Provider>
```

```js
const value = useContext(MyContext); // 3. Ở bất kỳ đâu bên trong nhánh đó, "hút" giá trị ra
```

### 2.3 Cơ chế

Khi 1 component gọi `useContext(MyContext)`, React làm việc sau:

> Từ vị trí của component đang gọi hook, **đi ngược lên cây cha (không phải lên toàn bộ app, mà lên đúng nhánh cha thực sự của nó)**, tìm component `<MyContext.Provider>` **gần nhất**. Nếu tìm thấy → lấy `value` của Provider đó. Nếu đi tới tận gốc cây mà không thấy Provider nào → trả về `defaultValue` lúc `createContext()` (mặc định là `undefined` nếu bạn không truyền).

Đây chính là lý do lỗi bạn gặp: `useSystemConfig()` trả về `undefined` — không phải vì code Context sai, mà vì **không tồn tại `<SystemConfigContext.Provider>` nào ở phía trên** component gọi nó, trong cây render thực tế lúc đó.

**Hệ quả thực dụng**: Context **không phải biến toàn cục**. Nó chỉ "nhìn thấy được" trong đúng nhánh JSX nằm bên trong cặp thẻ `<Provider>...</Provider>`. Component nằm ngoài nhánh đó — dù cùng file, cùng app — tuyệt đối không truy cập được.

### 2.4 Vì sao Provider có "điều kiện" (if loading/error) lại nguy hiểm

Nhìn lại code `SystemConfigProvider` của bạn:

```jsx
if (loading) {
  content = <StatusLoading />;
} else if (error) {
  content = <StatusError />;
} else {
  content = (
    <SystemConfigContext.Provider value={value}>
      {children}
    </SystemConfigContext.Provider>
  );
}
return content;
```

### "children" là gì, thực chất là 1 biến bình thường

```jsx
function Wrapper({ children }) {
  return <div>{children}</div>;
}
```

`children` chỉ là 1 prop bình thường như bao props khác — nó là **JSX mà người gọi `<Wrapper>` truyền vào ở giữa 2 thẻ**:

```jsx
<Wrapper>
  <SomeComponent />
</Wrapper>
```

Ở đây `children` chính là `<SomeComponent/>`. Nó không tự động "chui vào" đâu cả — **`Wrapper` phải tự tay đặt `{children}` vào chỗ nào trong JSX nó trả về, thì `SomeComponent` mới thực sự xuất hiện trên cây render.**

Nếu `Wrapper` viết thế này:

```jsx
function Wrapper({ children }) {
  return <div>Xin chào</div>; // không có {children} ở đây!
}
```

→ `SomeComponent` **biến mất hoàn toàn**, dù bạn có truyền nó vào `<Wrapper>`. Nó không lỗi, không crash — nó chỉ đơn giản là không tồn tại trên UI, và quan trọng hơn: **function `SomeComponent` không bao giờ được React gọi tới**.

### Ráp khái niệm "mount" vào

"Mount" = thời điểm 1 component **lần đầu xuất hiện** trong cây render và React bắt đầu gọi function của nó, chạy `useState`, `useEffect`, v.v.

Nếu 1 component chưa từng xuất hiện trong output JSX của cha nó → nó **chưa mount** → toàn bộ code bên trong nó (kể cả hook) chưa chạy 1 dòng nào.

### Áp vào `SystemConfigProvider` của bạn

```jsx
if (loading) {
  content = <StatusLoading />; // ← {children} KHÔNG xuất hiện ở đây
} else {
  content = (
    <SystemConfigContext.Provider value={value}>
      {children} // ← chỉ ở NHÁNH NÀY children mới được đặt vào JSX
    </SystemConfigContext.Provider>
  );
}
return content;
```

Giả sử bạn dùng đúng, gọi:

```jsx
<SystemConfigProvider>
  <ProtectedConfig />
</SystemConfigProvider>
```

thì `children` ở đây chính là `<ProtectedConfig/>`.

Bây giờ trace theo thời gian thực tế khi app chạy:

**Lúc `loading = true` (ngay khi vừa mount, trước khi fetch API xong):**

- `SystemConfigProvider` return `<StatusLoading/>`.
- `{children}` (tức `<ProtectedConfig/>`) **không nằm trong JSX được return** ở nhánh này.
- → `ProtectedConfig` **chưa từng mount**. Nó không tồn tại, không chạy, không có gì để lỗi cả — người dùng chỉ thấy chữ "Loading...".

**Lúc `fetch` xong, `setLoading(false)` → re-render, `loading = false`:**

- `SystemConfigProvider` giờ return nhánh `else` → `<SystemConfigContext.Provider value={value}>{children}</SystemConfigContext.Provider>`.
- Bây giờ `{children}` mới thực sự xuất hiện trong JSX → `ProtectedConfig` **mount lần đầu tiên** ngay lúc này.
- Vì nó mount **bên trong** `<SystemConfigContext.Provider>`, nên khi nó gọi `useContext(SystemConfigContext)`, đi ngược lên cây sẽ **tìm thấy** Provider này ngay → nhận đúng `value`.

## Vậy "nguy hiểm" ở đây nghĩa là gì?

Không phải nó gây lỗi — mà là **hệ quả dễ bị hiểu lầm** nếu bạn không nắm rõ: mọi component nằm trong `children` (ở đây là toàn bộ `ProtectedConfig` → `ClientRoutes` → tất cả trang con) sẽ **không mount, không chạy 1 dòng code nào** cho tới khi `loading` xong. Nếu sau này bạn debug mà thấy "ủa sao `console.log` trong component X không chạy lúc mới load trang", thì đây chính là nguyên nhân — không phải bug, mà là thiết kế cố ý chặn render sớm.

Bạn thử so sánh với cách viết **sai** sau để thấy rõ khác biệt:

```jsx
// Cách này thì children LUÔN mount, bất kể loading hay không
return (
  <SystemConfigContext.Provider value={value}>
    {loading ? <StatusLoading /> : children}
  </SystemConfigContext.Provider>
);
```

Ở cách này, `<Provider>` luôn tồn tại → `children` (`ProtectedConfig`) **luôn mount ngay từ đầu**, chỉ là nó tạm thời bị `StatusLoading` che mất trên UI thôi (nếu bạn muốn hiện cả 2 cùng lúc theo kiểu overlay). Đây là hướng thiết kế khác — không sai, chỉ là trade-off khác: children mount sớm hơn nhưng có thể đọc `value` rỗng (`data = null`) trong khoảnh khắc đầu.

Cách bạn đang viết (return `StatusLoading` thay vì render `Provider` + overlay) là lựa chọn **trì hoãn mount hoàn toàn** — an toàn hơn vì children không bao giờ thấy `data = null`, nhưng đổi lại children "ra đời muộn hơn".

---

## Phần 3 — React Router: `<Routes>`

### 3.1 Điểm khác biệt cốt lõi

Component bình thường (như `SystemConfigProvider`) hoạt động đúng như Phần 1 mô tả: React gọi function, nhận JSX trả về, render.

**`<Routes>` thì khác.** Nó không đợi React "render" children của nó theo flow bình thường rồi mới quyết định hiện cái gì. Thay vào đó, `<Routes>` (thực chất bên trong nó) **tự đọc trực tiếp `props.children`** — tức là mảng các React Element bạn truyền vào — để tự dựng nên 1 bảng cấu hình `path → element` ngay tại thời điểm nó chạy, **trước khi** bất kỳ children nào được render theo nghĩa gọi function.

Nó làm vậy vì `<Routes>` cần biết **toàn bộ danh sách path có thể có** để so khớp với URL hiện tại rồi mới quyết định render đúng 1 nhánh — nó cần nhìn thấy cấu trúc, không chỉ nhìn thấy 1 JSX output cuối cùng.

### 3.2 Hệ quả: children trực tiếp của `<Routes>` BẮT BUỘC là `<Route>`

```jsx
// ✅ ĐÚNG — Routes đọc được, vì con trực tiếp là <Route>
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/about" element={<About />} />
</Routes>
```

```jsx
// ❌ SAI — Routes không biết "mở" SomeWrapper ra để tìm Route bên trong
<Routes>
  <SomeWrapper>
    <Route path="/" element={<Home />} />
  </SomeWrapper>
</Routes>
```

Ở ví dụ sai, `<Routes>` nhìn thấy 1 element có `type = SomeWrapper` — nó không biết (và không cố gắng tìm hiểu) bên trong `SomeWrapper` có `<Route>` hay không, vì việc "mở ra xem bên trong" đó chính là hành động _render_ — mà `<Routes>` cần biết cấu trúc _trước khi_ render. Kết quả: route bị bỏ qua, mất tích, hoặc React Router quăng warning.

**Đây chính xác là lỗi bạn viết ở tin nhắn trước**:

```jsx
<SystemConfigProvider>
  <Route element={<ProtectedConfig />}>...</Route>
</SystemConfigProvider>
```

`SystemConfigProvider` nằm chen giữa `<Routes>` và `<Route>` → phá vỡ quy tắc "con trực tiếp phải là Route".

### 3.3 Vậy `element={...}` thì sao? Vì sao chỗ đó lại "an toàn"?

```jsx
<Route element={
    <SystemConfigProvider>
        <ProtectedConfig/>
    </SystemConfigProvider>
}>
```

`<Routes>` chỉ cần biết **path** và **element** của mỗi `<Route>` để dựng bảng cấu hình. Nó **không quan tâm** bên trong `element` chứa gì — với nó, `element` chỉ là "1 cục JSX sẽ được render bình thường (theo Phần 1) khi path này khớp URL". Vì vậy, bạn muốn nhét bao nhiêu Provider/wrapper logic vào bên trong `element` cũng được — đó lại quay về thế giới render component bình thường, không còn là vùng đất đặc biệt của `<Routes>` nữa.

**Quy tắc nhớ**: `<Route>` là đơn vị cấu hình mà `<Routes>` hiểu. Mọi thứ khác (Provider, wrapper, logic) phải nằm **trong `element` của 1 `<Route>`**, không bao giờ được đứng làm cha của `<Route>` trong cây con trực tiếp của `<Routes>`.

---

## Phần 4 — Nested Routes & `<Outlet/>`

Route có thể lồng nhau:

```jsx
<Route path="/admin" element={<AdminLayout />}>
  <Route path="dashboard" element={<Dashboard />} />
  <Route path="users" element={<Users />} />
</Route>
```

`AdminLayout` là "khung" chung (sidebar, header...). Nhưng làm sao `Dashboard` hay `Users` biết "chèn" vào đâu bên trong `AdminLayout`? Trả lời: `AdminLayout` phải tự đặt `<Outlet/>` ở vị trí muốn hiện route con:

```jsx
function AdminLayout() {
  return (
    <div>
      <Sidebar />
      <Outlet /> {/* route con (Dashboard/Users) sẽ render vào đây */}
    </div>
  );
}
```

`<Outlet/>` chính là cơ chế React Router dùng để "tiêm" route con vào đúng chỗ trong route cha — nó hoạt động dựa trên Context nội bộ của React Router (chính là ý tưởng Phần 2, React Router tự dùng Context của chính nó để làm việc này).

`ProtectedConfig` của bạn cũng theo đúng pattern này:

```jsx
export default function ProtectedConfig() {
  const { isMaintenance } = useSystemConfig();
  if (isMaintenance) return <p>Web đang bảo trì...</p>;
  return <Outlet />; // Cho phép route con (ClientRoutes) render tiếp
}
```

---

## Phần 5 — Pattern "Protected Route" là gì, bản chất chỉ là 1 `if`

Không có phép màu nào cả. `ProtectedRoute` (guard theo login) hay `ProtectedConfig` (guard theo maintenance) đều theo đúng 1 công thức:

```jsx
function ProtectedX() {
  const dieuKienChan = useSomeContext(); // đọc điều kiện từ Context

  if (dieuKienChan) {
    return <Navigate to="/somewhere" />; // hoặc render UI chặn tại chỗ
  }

  return <Outlet />; // Không bị chặn -> cho route con render tiếp
}
```

`<Navigate to="..."/>` là 1 component đặc biệt của React Router: khi được render, nó tự động điều hướng URL sang path khác (giống `history.push` nhưng viết bằng JSX). `ProtectedConfig` của bạn không dùng `Navigate` mà render thẳng UI báo bảo trì tại chỗ — đây là lựa chọn hợp lý vì bạn không có "trang khác" để điều hướng tới, chỉ cần chặn UI hiện tại.

**Vì sao Guard phải là 1 `<Route element={<Guard/>}>` bọc ngoài, không phải if trong từng page?**
Vì bạn có N trang con (`ClientRoutes` chứa rất nhiều page), viết check ở 1 chỗ (Guard) rồi để mọi page con thừa hưởng qua `<Outlet/>` tuân thủ đúng nguyên tắc DRY — giống hệt cách bạn đã áp dụng cho spacing/container ở `ClientLayout`.

---

## Phần 6 — Ráp lại toàn bộ: cây thực tế của app bạn nên trông như thế nào

```jsx
<AuthProvider>
  {" "}
  ← Context: thông tin login (toàn app cần, kể cả login page check redirect)
  <BrowserRouter>
    <Routes>
      <Route path="log-in" element={<Login />} />

      <Route
        element={
          <SystemConfigProvider>
            {" "}
            ← Context: config, CHỈ nhánh Client cần
            <ProtectedConfig /> ← Guard: đọc Context trên, quyết định chặn hay{" "}
            <Outlet />
          </SystemConfigProvider>
        }
      >
        <Route path="/*" element={<ClientRoutes />} /> ← Route con, render vào{" "}
        <Outlet /> của ProtectedConfig
      </Route>

      <Route element={<ProtectedRoute />}>
        {" "}
        ← Guard: đọc AuthContext, KHÔNG cần SystemConfig
        <Route path="/admin/*" element={<AdminRoutes />} />
      </Route>
    </Routes>
  </BrowserRouter>
</AuthProvider>
```

1. Con trực tiếp của `<Routes>` toàn bộ là `<Route>` (Phần 3.2) — không có Provider nào chen giữa.
2. Provider/Guard cần bọc quanh nhánh nào thì nhét vào `element` của `<Route>` bao ngoài nhánh đó (Phần 3.3) — và Context chỉ "nhìn thấy" được trong đúng nhánh mà nó bọc (Phần 2.3).

---
