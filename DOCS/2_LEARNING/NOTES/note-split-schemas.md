**1. Validate được cấu trúc từng phần tử, không chỉ kiểu list chung chung**

Nếu bạn khai báo thẳng trong schema chính:

```python
class InfoSchema(BaseModel):
    contact: list  # hoặc list[dict]
```

thì Pydantic chỉ biết đây là 1 list/list các dict, không biết bên trong mỗi phần tử phải có đúng 2 field `type` và `url`. Ai đó gửi lên `{"foo": "bar"}` vẫn pass tuốt.

Còn khi dùng:

```python
contact: list[ContactItem]
```

Pydantic sẽ tự động validate **từng phần tử** trong list theo đúng shape của `ContactItem` — thiếu field, sai kiểu, thừa field lạ (nếu bạn set `model_config = {"extra": "forbid"}`) đều bị bắt lỗi ngay.

**2. Lỗi trả về rõ ràng, chỉ đúng vị trí sai**

Ví dụ phần tử thứ 2 trong list thiếu `url`, FastAPI sẽ trả lỗi kiểu:

```json
{ "loc": ["body", "contact", 1, "url"], "msg": "Field required" }
```

Biết ngay lỗi ở index 1, field `url` — thay vì lỗi mơ hồ "contact không hợp lệ".

**3. Tái sử dụng được**

`ContactItem` có thể dùng lại ở nhiều chỗ: schema tạo mới (Create), schema cập nhật (Update), schema trả về (Response) — không phải viết lại cấu trúc dict mỗi lần.

**4. Swagger/OpenAPI docs tự sinh đẹp hơn**

FastAPI đọc được `ContactItem` là 1 model rõ ràng nên trang `/docs` sẽ hiển thị đúng schema lồng nhau (nested schema), người dùng API biết chính xác cần gửi field gì, thay vì thấy `contact: array of objects` chung chung.

Nói ngắn gọn: nếu bạn chỉ cần "list bất kỳ" thì không cần tách; nhưng vì bạn muốn ép cấu trúc cố định (`type`, `url`) cho từng phần tử, thì tách model riêng là cách chuẩn để Pydantic validate giúp bạn thay vì tự check tay.
