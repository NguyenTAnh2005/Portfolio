# 🪦 Nghỉ hưu — Legacy Seed Scripts

> "Không có mã nào chết thật sự, chúng chỉ chuyển sang trạng thái archive."

## Ai đang nằm ở đây?

- `seed_data.py` — điểm khởi đầu, chạy bằng `python seed_data.py`
- `seed/user.py`
- `seed/info.py`
- `seed/timeline.py`
- `seed/project.py`
- `seed/achievement.py`
- `seed/system_config.py`

## Vì sao nghỉ hưu?

Ngày 14/08/2026, dự án chuyển toàn bộ seed data sang quản lý bằng **Alembic data migration** (`sa.table()` + `op.bulk_insert()`), thay vì gọi script Python độc lập qua ORM (`db.add()` + `db.commit()`).

Lý do chuyển đổi:

- **Một nguồn sự thật duy nhất** — migration nằm chung lịch sử với schema, chạy tự động theo `alembic upgrade head`, không cần nhớ chạy thêm 1 bước tay riêng sau khi tạo bảng.
- **Nhất quán khi deploy** — môi trường mới (CI/CD, máy đồng đội, production) chỉ cần 1 lệnh duy nhất là có đủ schema + data khởi đầu, không sợ quên bước seed.
- **An toàn hơn với dữ liệu phụ thuộc ngoài** — seed cũ gọi thẳng GitHub API lúc seed project, rủi ro deploy fail nếu API lỗi/rate-limit. Bản migration mới seed data tĩnh trước, đồng bộ GitHub sau qua API riêng.

## Đóng góp của chúng

Không hề nhỏ. Đây là những dòng code đầu tiên giúp:

- Test thử models, thấy dữ liệu thật chạy được trên DB ngay từ những buổi đầu code backend
- Debug qua lại nhiều lần khi models đổi cấu trúc (`desc`, `contact` JSONB, `ARRAY` fields...)
- Là bản nháp gốc để chuyển thể sang `sa.table()` khi viết migration — không có bản này, viết migration từ đầu sẽ vất vả hơn nhiều

## Có còn dùng được không?

Không còn được gọi trong luồng chạy chính của app. Giữ lại thuần vì mục đích:

- Tài liệu tham khảo cú pháp ORM tạo data
- Nhắc lại lý do & quá trình đưa ra quyết định chuyển sang Alembic migration
- Kỷ niệm 🙂

---

_Archived on 2026-08-14, sau khi migration `d5a1c4c307c1_seed_data.py` chính thức thay thế toàn bộ._

---

# 😇🥲👍 CỔ ĐIỂN - TÔN TRỌNG
