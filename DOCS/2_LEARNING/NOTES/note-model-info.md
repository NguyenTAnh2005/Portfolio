**Model:**

```python
from sqlalchemy.dialects.postgresql import JSONB

contact: Mapped[list] = mapped_column(JSONB, default=list)
```

**Cấu trúc từng phần tử trong list**, chỉ cần tối thiểu:

```json
[
  { "type": "facebook", "url": "https://facebook.com/..." },
  { "type": "github", "url": "https://github.com/..." },
  { "type": "email", "url": "mailto:you@example.com" }
]
```

`type` ở đây đóng vai trò là key để frontend lookup icon (kiểu `iconMap[item.type]`), nên cứ chuẩn hóa nó thành slug cố định (lowercase, không dấu, không khoảng trắng) để tránh lệch giữa BE và FE.

**Một lưu ý nhỏ:** nếu sau này bạn có field `visible` (ẩn/hiện 1 mạng xã hội mà không xóa data) thì thêm luôn từ bây giờ cho đỡ phải migrate sau:

```json
{ "type": "facebook", "url": "https://facebook.com/...", "visible": true }
```

Còn nếu chắc chắn không cần tính năng ẩn/hiện thì bỏ qua, giữ 2 field `type`/`url` cho gọn cũng được — tùy vào việc trang admin (Chặng 4) sau này có cho phép toggle từng contact hay không.

Pydantic schema cho FastAPI thì validate kiểu:

```python
from pydantic import BaseModel, HttpUrl

class ContactItem(BaseModel):
    type: str
    url: str  # hoặc HttpUrl nếu muốn validate link, nhưng "mailto:"/"tel:" sẽ fail HttpUrl
```
