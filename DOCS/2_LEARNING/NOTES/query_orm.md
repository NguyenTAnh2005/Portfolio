# `🎯 Note về query ORM`

## 1. `Query` là gì trước khi gọi `.all()`

Khi bạn viết:

```python
query = db.query(RefreshToken).filter(RefreshToken.user_id == user_id)
```

Dòng này **chưa chạm vào DB**. `query` chỉ là một object Python đại diện cho câu SQL _sắp_ được sinh ra — kiểu như bạn đang viết nháp câu SQL bằng Python, chưa gửi đi. SQLAlchemy gọi đây là "lazy" — nó trì hoãn việc thực thi tới khi bạn gọi một trong các hàm "kích hoạt" (execute):

- `.all()` → chạy `SELECT ...`, trả về **list** các object.
- `.first()` → chạy `SELECT ... LIMIT 1`, trả về **1 object hoặc `None`**.
- `.one()` → chạy `SELECT ...`, đòi hỏi đúng 1 kết quả, không thì raise lỗi.
- `.delete()` → chạy `DELETE FROM ...`, trả về **số lượng row bị xoá** (int), không trả object nào.
- `.update({...})` → chạy `UPDATE ... SET ...`, trả về **số lượng row bị sửa** (int).

Điểm mấu chốt bạn đang hỏi: **`.all()` chỉ dùng khi bạn muốn lấy dữ liệu về Python để đọc/thao tác**. Còn `.update()`/`.delete()` là lệnh sai khiến DB tự làm việc hàng loạt ngay tại chỗ, bạn không cần (và không nên) gọi `.all()` trước đó.

## 2. Vì sao code của bạn KHÔNG cần `.all()` trước `.update()`/`.delete()`

So sánh 2 cách làm việc với nhiều row:

**Cách sai (chậm, dễ mắc lỗi) — "kiểu vòng lặp":**

```python
tokens = db.query(RefreshToken).filter(RefreshToken.user_id == user_id).all()  # lấy hết về Python
for token in tokens:
    token.revoked = True   # sửa từng object trong Python
db.commit()  # SQLAlchemy tự sinh N câu UPDATE riêng lẻ, mỗi row 1 câu
```

Cách này: nếu user có 50 refresh token, DB nhận **50 câu UPDATE** riêng biệt. Chậm, tốn round-trip mạng DB nhiều lần.

**Cách đúng bạn đang dùng — "kiểu bulk":**

```python
query = db.query(RefreshToken).filter(RefreshToken.user_id == user_id)
query.update({RefreshToken.revoked: True}, synchronize_session='fetch')
db.commit()
```

Cách này sinh **đúng 1 câu SQL** duy nhất:

```sql
UPDATE refresh_token SET revoked = true WHERE user_id = ?;
```

DB tự xử lý tất cả row khớp điều kiện trong 1 lệnh — nhanh hơn nhiều, đây chính là lý do bạn không cần (và không nên) gọi `.all()` ở đây. Bạn không cần đưa dữ liệu về Python vì bạn không cần _đọc_ nó, chỉ cần _ra lệnh sửa hàng loạt_.

Tương tự với `delete`:

```python
query = db.query(RefreshToken).filter(RefreshToken.expires_at < datetime.now(timezone.utc))
deleted_count = query.delete(synchronize_session='fetch')
```

→ 1 câu `DELETE FROM refresh_token WHERE expires_at < ?;` — xoá thẳng, không cần load object nào lên trước.

## 3. Vậy `synchronize_session` giải quyết vấn đề gì phát sinh từ cách bulk này?

Đây là cái giá phải trả khi làm bulk update/delete: DB đã đổi dữ liệu, nhưng **session Python của bạn không tự biết** — vì lệnh này không đi qua từng object như cách thường lệ (`obj.revoked = True` rồi `db.add(obj)`).

Ví dụ minh hoạ vấn đề thực tế, giả sử trong cùng 1 request bạn có đoạn code:

```python
token = db.query(RefreshToken).filter(RefreshToken.id == 5).first()  # (1) load lên, revoked=False
print(token.revoked)  # False

db.query(RefreshToken).filter(RefreshToken.user_id == token.user_id)\
    .update({RefreshToken.revoked: True})  # (2) bulk update thẳng xuống DB

print(token.revoked)  # <-- vẫn in ra False nếu không đồng bộ! Vì object Python (1) chưa hay biết gì
```

`synchronize_session='fetch'` giải quyết đúng chỗ này: sau khi chạy `UPDATE`, SQLAlchemy chạy thêm 1 `SELECT` để biết chính xác những row nào vừa bị đổi, rồi cập nhật lại các object Python tương ứng đang nằm trong session — để `token.revoked` ở trên in ra đúng `True`.

Với 2 hàm của bạn (`update_by_user_id`, `delete`), trong luồng thực tế bạn thường gọi chúng rồi `db.commit()` và kết thúc request luôn (không có object nào khác trong cùng session cần đọc lại) — nên rủi ro "lệch dữ liệu" gần như không xảy ra. Nhưng để `'fetch'` như bạn đang làm vẫn là lựa chọn an toàn mặc định, tốn thêm đúng 1 query nhỏ, đổi lại tránh được bug ẩn khó debug về sau. Không cần đổi.
