# `🎯 Note về Pagination`

### Lưu ý:

`count_page = Math.floor(total/limit) + 1` sai khi `total` chia hết cho `limit`. Ví dụ `total=10, limit=5` → ra 3 trang, đúng ra chỉ có 2. Phải dùng `Math.ceil(total/limit)`.

## Về việc tổ chức prop/callback

Vấn đề gốc: **`Pagination` đang biết quá nhiều về cách cha tính `skip`** (`skip + (page_num - current_page) * limit`). Component con lẽ ra không cần biết `skip` là gì cả — nó chỉ cần báo "người dùng muốn qua trang số mấy", còn việc tính `skip` là việc của cha (người sở hữu state).

Quy tắc chung nên theo:

- **State (dữ liệu) ở đâu thì logic cập nhật state ở đó** — `queryParam` sống ở `Project.jsx` thì hàm tính `skip` mới cũng nên nằm ở `Project.jsx`, không đẩy xuống con.
- **Đặt tên prop kiểu callback:** khi _truyền xuống con_, đặt tên theo dạng `on + Sự kiện` (`onPageChange`, `onSearchChange`) — vì con chỉ "phát tín hiệu sự kiện xảy ra", không quan tâm cha xử lý ra sao.
- **Đặt tên hàm xử lý ở cha:** dùng `handle + Sự kiện` (`handlePageChange`). Đây là convention rất phổ biến trong React, giúp nhìn tên là biết ngay đâu là "định nghĩa xử lý" (`handle...`) và đâu là "hợp đồng giao tiếp với con" (`on...`).
- **Prop dữ liệu thuần** (không phải callback) thì đặt tên là danh từ bình thường: `skip`, `limit`, `total`, `currentPage`.

Áp dụng vào đây, sửa lại `Pagination` để nó chỉ làm việc với khái niệm "số trang", không đụng đến `skip`:

```jsx
// components/Pagination.jsx
import clsx from "clsx";

export const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  const pages = Array.from({ length: totalPages }, (_, i) => i + 1);

  return (
    <div className="flex gap-2">
      {pages.map((pageNum) => (
        <PageIndex
          key={`page-num-${pageNum}`}
          pageNum={pageNum}
          isActive={pageNum === currentPage}
          onPageChange={onPageChange}
        />
      ))}
    </div>
  );
};

const PageIndex = ({ pageNum, isActive, onPageChange }) => {
  return (
    <span
      className={clsx(
        "flex justify-center items-center bg-primary/15 px-4 py-2 border-2",
        isActive && "text-primary border-primary/40",
      )}
      onClick={() => onPageChange(pageNum)}
    >
      {pageNum}
    </span>
  );
};
```

Và ở `Project.jsx`, logic tính `skip` từ `pageNum` được giữ ở cha, chỗ nó thuộc về:

```jsx
const currentPage = Math.floor(queryParam.skip / queryParam.limit) + 1;
const totalPages = data ? Math.ceil(data.total / queryParam.limit) : 1;

const handlePageChange = (pageNum) => {
  setQueryParam((prev) => ({
    ...prev,
    skip: (pageNum - 1) * prev.limit,
  }));
};
```

```jsx
<Pagination
  currentPage={currentPage}
  totalPages={totalPages}
  onPageChange={handlePageChange}
/>
```

So với bản cũ, cái lợi là:

1. `Pagination` giờ là component "câm" hoàn toàn — không tự tính toán skip, chỉ báo sự kiện. Sau này tái sử dụng cho trang Blog/Achievement khác cũng không cần sửa gì bên trong nó.
2. Không còn phép tính `(page_num - current_page) * limit` rối rắm trong component con nữa — nguồn gây `NaN` biến mất luôn vì cách tiếp cận đổi hẳn, không chỉ vá lỗi gõ nhầm tên.
3. Dễ debug hơn: nếu sau này lại có `NaN`, bạn chỉ cần nhìn 1 chỗ (`handlePageChange` ở cha) thay vì lần theo props qua 2 tầng component.
