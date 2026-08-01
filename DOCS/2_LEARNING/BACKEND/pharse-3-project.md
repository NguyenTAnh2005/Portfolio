### Ghi chú: Timeline vs Project — khác pattern update ảnh

- Timeline (Chặng 3.3): gộp chung text + ảnh trong 1 endpoint (multipart).
- Project (Chặng 3.4): tách API JSON (text) và API riêng (ảnh).
  Lý do: gặp bug thật khi filter None cho field list (list_tech),
  JSON + exclude_unset xử lý sạch hơn multipart form.
- Quyết định: giữ nguyên Timeline, không refactor lại — vì không có
  field list optional nên không gặp vấn đề tương tự, và ưu tiên thời
  gian cho các module còn lại.

Về bản chất tải (CPU, DB query, băng thông) thì **gần như không đổi**, chỉ là chia lại cách gói:

- 1 request gộp: 1 lần parse multipart (cả text lẫn ảnh) → 1 lần update DB (text) → 1 lần upload Cloudinary → 1 lần update DB (ảnh) → có thể 1 lần destroy ảnh cũ.
- 2 request tách: request 1 làm phần text (1 lần update DB), request 2 làm phần ảnh (1 lần upload Cloudinary → 1 lần update DB → 1 lần destroy ảnh cũ).

Tổng công việc server phải làm **y hệt nhau**, chỉ là tách thành 2 cuộc gọi HTTP thay vì 1. Cái tăng lên duy nhất là:

- Overhead network: thêm 1 lần round-trip HTTP (bắt tay TCP/TLS nếu không giữ kết nối, thêm 1 lần queue xử lý request). Với 1 project cá nhân/đồ án, traffic thấp, độ trễ thêm này là **không đáng kể** (vài chục ms), không phải kiểu "khổ server" đến mức lo lắng.
- Nếu ảnh không đổi thường xuyên, phần lớn các lần "sửa project" sẽ **chỉ cần gọi 1 request** (PATCH text) — tức là còn nhẹ hơn cách gộp hiện tại (vì hiện tại kể cả chỉ sửa `title` thôi, request vẫn phải đi qua toàn bộ logic xử lý multipart/form kể cả khi không có file).

Cái thật sự tốn là **độ phức tạp cho FE** (phải quản lý gọi 2 API, xử lý khi 1 trong 2 fail), chứ không phải server. Với dự án học tập solo thì cái giá này khá nhỏ, và bạn học thêm được cách xử lý "eventual consistency" — cũng là kiến thức hay.

## Đề xuất cụ thể cho Project

```
PATCH /project/{id}          → JSON body, đổi title/list_tech/project_url
PATCH /project/{id}/image    → chỉ nhận UploadFile, đổi + xóa ảnh cũ
```

- `PATCH /project/{id}`: dùng `ProjectUpdate(BaseModel)` hiện có, gọi `.model_dump(exclude_unset=True)` — xóa được hết đống code check `isinstance(value, str) and value == ""` đang có. `list_tech: []` gửi lên nghĩa là xóa hết, không gửi field nghĩa là giữ nguyên. Sạch, không cần sentinel gì cả.
- `PATCH /project/{id}/image`: chỉ nhận `img_file: UploadFile = File(...)`, gọi `upload_image` → `update` cột `img_url`/`img_public_id` → `destroy_image(old_public_id)`. Đây cũng chính là nơi fix bug gõ nhầm biến ở lần trước.
- FE: nếu form Project edit cho sửa cả text lẫn ảnh cùng lúc, chỉ cần gọi tuần tự 2 API khi Save (nếu có file mới thì gọi thêm request ảnh) — không cần Promise.all song song, làm tuần tự để tránh race về old_public_id.

Vậy là bạn được cả 2: giữ Timeline cổ điển (đã yên vị, không đụng), còn Project — module đang code dở, đang gặp đúng bug này — thì áp dụng pattern mới luôn, đỡ phải sửa đi sửa lại 2 lần.
