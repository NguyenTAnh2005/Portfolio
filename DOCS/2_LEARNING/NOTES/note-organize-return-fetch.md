```jsx
if (loading) {
  return (
    <div className="w-screen">
      <div className="w-[95%] mx-auto">Đang Tải</div>
    </div>
  );
}
if (error != null) {
  return <div>Lỗi: {error.message}</div>;
}
if (!data) {
  return <div> Không fetch được nội dung!</div>;
}
return (
  <div className="w-screen">
    <div className="w-[95%] mx-auto">
      {
        <pre className="text-green-400 text-xs">
          {JSON.stringify(data.contact, null, 2)}
        </pre>
      }
    </div>
  </div>
);
```

Mỗi trường hợp `return` một cục (`<div className="w-screen"><div className="w-[95%] mx-auto">...</div></div>`) sẽ bị lặp code layout. Có 2 hướng hay dùng để fix:

## Cách 1: Gom nội dung vào 1 biến, chỉ giữ 1 wrapper duy nhất

```jsx
export default function AboutMe(){
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(()=>{ ... }, []);

    let content;
    if (loading) {
        content = <div>Đang Tải</div>;
    } else if (error != null) {
        content = <div>Lỗi: {error.message}</div>;
    } else if (!data) {
        content = <div>Không fetch được nội dung!</div>;
    } else {
        content = (
            <pre className="text-green-400 text-xs">
                {JSON.stringify(data.contact, null, 2)}
            </pre>
        );
    }

    return (
        <div className="w-screen">
            <div className="w-[95%] mx-auto">
                {content}
            </div>
        </div>
    );
}
```

Đây là cách đơn giản nhất, ít thay đổi cấu trúc, chỉ cần "gom" phần logic if vào 1 biến `content` rồi render 1 lần.

## Cách 2: Tách hẳn 1 component Layout dùng chung

Nếu sau này có nhiều page khác cũng dùng chung layout `w-screen` + `w-[95%] mx-auto`, bạn có thể tách nó thành 1 component riêng:

```jsx
function PageWrapper({ children }) {
  return (
    <div className="w-screen">
      <div className="w-[95%] mx-auto">{children}</div>
    </div>
  );
}
```

Rồi trong `AboutMe`:

```jsx
export default function AboutMe() {
  // ...state, useEffect giữ nguyên

  if (loading) return <PageWrapper>Đang Tải</PageWrapper>;
  if (error != null) return <PageWrapper>Lỗi: {error.message}</PageWrapper>;
  if (!data) return <PageWrapper>Không fetch được nội dung!</PageWrapper>;

  return (
    <PageWrapper>
      <pre className="text-green-400 text-xs">
        {JSON.stringify(data.contact, null, 2)}
      </pre>
    </PageWrapper>
  );
}
```

Cách này vẫn giữ được nhiều `return` riêng (dễ đọc theo từng case) nhưng không lặp lại phần div layout — vì layout giờ nằm trong 1 component tái sử dụng được cho cả những page khác nữa.

**Gợi ý:** nếu layout `w-screen` / `w-[95%] mx-auto` này dùng ở nhiều trang (không chỉ AboutMe), nên chọn Cách 2 để tái sử dụng luôn. Nếu chỉ dùng ở đúng component này thôi thì Cách 1 gọn hơn, không cần tạo thêm file/component mới.
