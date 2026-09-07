# 🪦 Legacy Seed Scripts

## Ai đang nằm ở đây?

- `seed_data.py` — điểm khởi đầu, chạy bằng `python seed_data.py`
- `seed/user.py`
- `seed/info.py`
- `seed/timeline.py`
- `seed/project.py`
- `seed/achievement.py`
- `seed/system_config.py`

Ngày 14/08/2026, dự án chuyển toàn bộ seed data sang quản lý bằng **Alembic data migration** (`sa.table()` + `op.bulk_insert()`), thay vì gọi script Python độc lập qua ORM (`db.add()` + `db.commit()`).

Lý do chuyển đổi:

- **Một nguồn sự thật duy nhất** — migration nằm chung lịch sử với schema, chạy tự động theo `alembic upgrade head`, không cần nhớ chạy thêm 1 bước tay riêng sau khi tạo bảng.
- **Nhất quán khi deploy** — môi trường mới (CI/CD, máy đồng đội, production) chỉ cần 1 lệnh duy nhất là có đủ schema + data khởi đầu, không sợ quên bước seed.
- **An toàn hơn với dữ liệu phụ thuộc ngoài** — seed cũ gọi thẳng GitHub API lúc seed project, rủi ro deploy fail nếu API lỗi/rate-limit. Bản migration mới seed data tĩnh trước, đồng bộ GitHub sau qua API riêng.

---

# 😇🥲👍 CỔ ĐIỂN - TÔN TRỌNG
