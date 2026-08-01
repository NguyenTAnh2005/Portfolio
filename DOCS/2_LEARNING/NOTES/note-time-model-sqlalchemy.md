Được, mình sẽ giải thích lại từ đầu, không giả định bạn biết gì cả. Đây là chủ đề mà rất nhiều người mới học đều bị rối, nên đừng ngại.

## 1. Vấn đề cốt lõi: Máy tính lưu thời gian thế nào?

Máy tính không lưu "8 giờ tối" — nó lưu thời gian dưới dạng một **mốc tuyệt đối** (thường tính từ 1/1/1970, gọi là Unix timestamp), rồi khi hiển thị mới "dịch" ra giờ địa phương.

Vấn đề là: "8 giờ tối" ở Việt Nam và "8 giờ tối" ở Mỹ là hai thời điểm khác nhau hoàn toàn. Nếu bạn chỉ lưu con số "20:00" mà không ghi rõ nó là giờ ở đâu, thì dữ liệu đó **vô nghĩa** khi hệ thống của bạn có người dùng/server ở nhiều nơi khác nhau.

→ Đó là lý do người ta luôn khuyên: **lưu thời gian theo UTC** (giờ chuẩn quốc tế, không lệch theo vùng), rồi khi hiển thị cho người dùng thì mới convert sang giờ địa phương của họ (VD: +7 cho VN).

## 2. "Naive" và "Aware" trong Python

Đây là khái niệm quan trọng nhất bạn cần nắm:

- **Naive datetime**: một `datetime` object _không biết_ nó thuộc timezone nào. VD: `datetime(2026, 7, 28, 20, 0)` — con số này có thể là giờ VN, giờ Mỹ, giờ UTC... không ai biết, vì nó không mang theo thông tin timezone.
- **Aware datetime**: một `datetime` object có gắn kèm thông tin timezone. VD: `2026-07-28T20:00:00+07:00` — rõ ràng đây là 8h tối giờ VN.

**Nguyên tắc**: luôn làm việc với **aware datetime**, tránh naive datetime bằng mọi giá. Naive datetime là nguồn gốc của 90% bug liên quan đến thời gian.

## 3. Cột `DateTime(timezone=True)` nghĩa là gì?

Trong SQLAlchemy, khi bạn khai báo:

```python
created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

Bạn đang nói với Postgres: "cột này lưu kiểu `TIMESTAMPTZ`" (timestamp with time zone).

Điều thú vị (và hay gây hiểu lầm) là: **Postgres không thực sự lưu timezone kèm theo giá trị**. Nó luôn **quy đổi về UTC rồi lưu**, và khi bạn `SELECT`, nó tự convert sang timezone mà connection/session đang set (mặc định thường là UTC hoặc timezone của server). Cái `timezone=True` chỉ là nói cho Postgres biết: "hãy làm việc quy đổi này giúp tôi", còn nếu bạn dùng `DateTime(timezone=False)` (mặc định), Postgres sẽ **không quy đổi gì cả**, coi con số bạn đưa vào "là gì thì lưu y vậy" → dễ dính bug bạn không biết giờ đó là giờ gì.

→ Kết luận: luôn dùng `DateTime(timezone=True)` cho các cột thời gian quan trọng như `created_at`, `last_updated`.

## 4. `func.now()` là gì?

`func.now()` không phải là hàm Python — nó là cách SQLAlchemy nói với Postgres: "khi insert/update, hãy tự chạy hàm `NOW()` của chính Postgres để lấy giờ hiện tại". Nghĩa là **thời gian được tính bởi database server**, không phải bởi code Python của bạn.

Ưu điểm: dù bạn insert bằng Python, bằng SQL trực tiếp, hay bằng tool nào khác, DB vẫn tự set đúng giờ — nhất quán, không phụ thuộc giờ máy chạy code Python (có thể lệch giờ hệ thống).

## 5. Ba cơ chế set giá trị, khác nhau ở "ai" và "khi nào"

| Cơ chế               | Chạy ở đâu                           | Khi nào trigger                                                        |
| -------------------- | ------------------------------------ | ---------------------------------------------------------------------- |
| `default=...`        | Python, trước khi gửi câu SQL insert | Lúc insert (ORM tính giá trị)                                          |
| `server_default=...` | Database (Postgres)                  | Lúc insert, kể cả insert bằng raw SQL                                  |
| `onupdate=...`       | SQLAlchemy ORM (Python)              | Lúc update **qua ORM session** (không áp dụng nếu update bằng raw SQL) |

Với `created_at`/`last_updated`, cách chuẩn nhất (và code cũ của bạn gần đúng, chỉ thiếu 1 dòng) là:

```python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),   # DB tự set giờ lúc tạo record
    nullable=False,
)
last_updated: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),   # lúc tạo record, set giống created_at
    onupdate=func.now(),         # lúc update record (qua ORM), tự cập nhật lại
    nullable=False,
)
```

**Ghi nhớ đơn giản**: `created_at` chỉ set 1 lần → chỉ cần `server_default`. `last_updated` cần set lại mỗi lần sửa → cần thêm `onupdate`.

## 6. Alembic migration sẽ trông như thế nào?

Khi bạn chạy `alembic revision --autogenerate`, nó sẽ tạo ra đoạn tương tự:

```python
op.create_table(
    'project',
    ...
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
)
```

Bạn sẽ **không** thấy `onupdate` xuất hiện trong file migration — điều đó bình thường, vì `onupdate` không phải là cấu trúc của bảng (không phải là ràng buộc DB), nó chỉ là hành vi của SQLAlchemy khi update qua ORM. Đừng hoảng nếu không thấy nó trong migration file.

## 7. Ở phía backend (API trả về cho frontend) thì sao?

Khi FastAPI serialize `datetime` object (từ Postgres trả về) thành JSON để gửi cho frontend, Pydantic sẽ tự động chuyển thành chuỗi ISO 8601 kèm timezone, ví dụ:

```
"created_at": "2026-07-28T13:00:00+00:00"
```

Đây là UTC. **Việc convert sang giờ VN (+7) để hiển thị đẹp cho người dùng nên làm ở phía Frontend** (dùng `Intl.DateTimeFormat` hoặc thư viện như `dayjs`), không phải ở backend. Backend chỉ có nhiệm vụ trả về đúng giờ UTC, để bất kỳ client nào (web VN, app ở nước khác...) tự convert theo timezone của họ.

---

Tóm gọn quy tắc bạn cần nhớ khi làm việc với time trong dự án này:

1. Luôn lưu UTC trong DB (`DateTime(timezone=True)` + để Postgres tự tính bằng `func.now()`).
2. `created_at` = `server_default` thôi. `last_updated` = `server_default` + `onupdate`.
3. Đừng bao giờ tự parse/set datetime "naive" (không timezone) trong code Python nếu tránh được.
4. Convert sang giờ địa phương chỉ làm ở tầng hiển thị (frontend), không làm ở backend/DB.

## 5. Giải thích lại cái bảng (`default` / `server_default` / `onupdate`) — dễ hiểu hơn

Hãy tưởng tượng bạn có 1 quyển sổ (table `project`), mỗi khi bạn viết vào sổ (insert) hoặc sửa 1 dòng đã viết (update), bạn cần ghi ngày giờ vào 2 cột `created_at` và `last_updated`. Câu hỏi là: **ai cầm bút ghi ngày giờ đó, và ghi vào lúc nào?**

- **`default=...`**: Bạn (Python code) tự tính giờ trước, rồi gửi kèm theo lệnh "hãy viết dòng này vào sổ". Nghĩa là Python phải tự lấy giờ máy (`datetime.now()`) rồi nhét vào — nếu giờ máy Python bị sai (lệch timezone, sai đồng hồ hệ thống...) thì dữ liệu sai theo.

- **`server_default=...`**: Bạn nói với người giữ sổ (Postgres): "mỗi khi có ai viết dòng mới, anh tự ghi giờ hiện tại giúp tôi". Postgres tự làm, không cần Python tính toán gì cả → đáng tin cậy hơn vì giờ luôn lấy từ 1 nguồn duy nhất (server DB).

- **`onupdate=...`**: Đây là dặn dò riêng cho SQLAlchemy (không phải Postgres): "mỗi khi ai đó sửa 1 dòng **thông qua ORM Python** (gọi `session.commit()`), hãy tự cập nhật lại giờ ở cột này". Nó chỉ hoạt động nếu bạn sửa data bằng Python/ORM — nếu ai đó chạy lệnh SQL `UPDATE` trực tiếp trong pgAdmin thì cột này **sẽ không tự cập nhật**.

→ Tóm lại bảng đó chỉ đơn giản là: 3 cách khác nhau để trả lời câu hỏi "giá trị time này do ai tính, và tính vào lúc nào".

## 7. ISO 8601 là gì?

Đây là 1 **chuẩn quốc tế** để viết ngày giờ dưới dạng chữ, sao cho máy tính ở bất kỳ đâu cũng đọc và hiểu đúng, không bị nhầm lẫn (khác với kiểu viết ngày kiểu Mỹ `07/28/2026` hay kiểu VN `28/07/2026` dễ gây hiểu nhầm).

Format chuẩn: `YYYY-MM-DDTHH:MM:SS±HH:MM`

Ví dụ: `2026-07-28T13:00:00+00:00` nghĩa là ngày 28/7/2026, lúc 13:00, theo múi giờ UTC+0.

GitHub API trả về theo dạng: `2024-01-15T08:23:01Z` — chữ **`Z`** ở cuối là viết tắt của "Zulu time", tức là UTC+0 (giống hệt `+00:00`, chỉ viết gọn hơn).

## Điểm quan trọng nhất: mục đích của bạn khác với cơ chế `server_default`/`onupdate`

Đọc code fetch GitHub của bạn, mình thấy có 1 điều cần làm rõ ngay, vì nó ảnh hưởng đến cách bạn code model:

Bạn đang lấy:

```python
"created_at": repo_data.get("created_at"),   # ngày tạo REPO trên Github
"last_updated": repo_data.get("pushed_at"),   # lần push cuối cùng lên Github
```

Đây là **thời gian của cái repo trên GitHub**, hoàn toàn khác với "thời gian record này được tạo/sửa trong database của bạn".

Nếu bạn dùng `server_default=func.now()` + `onupdate=func.now()` như mình hướng dẫn ban đầu, thì Postgres sẽ tự set `created_at` = lúc bạn insert record vào DB (VD: hôm nay bạn thêm project này), và `last_updated` = lúc bạn sửa record trong DB (VD: 3 tháng sau bạn sửa mô tả project) — **chứ không phải** ngày tạo repo GitHub hay lần push cuối trên GitHub.

→ Hai ý nghĩa này **khác nhau hoàn toàn**, và theo mục đích ban đầu của bạn (lưu ngày tạo repo + lần push cuối từ GitHub), bạn **không nên** dùng `server_default`/`onupdate` cho 2 cột này. Thay vào đó, cột chỉ nên khai báo đơn giản, và bạn **tự set giá trị bằng tay** (lấy từ GitHub API) mỗi khi tạo hoặc cập nhật project:

```python
created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
```

Không có `server_default`, không có `onupdate` — vì giá trị không đến từ "thời điểm DB thao tác", mà đến từ dữ liệu bên ngoài (GitHub).

Khi tạo project mới, code của bạn (ở tầng CRUD/service) sẽ trông đại khái thế này:

```python
repo_info = await get_repo_info(url)  # gọi hàm bạn đã viết

new_project = Project(
    title=...,
    project_url=...,
    list_tech=...,  # tự nhập tay
    list_lang=repo_info.data["languages"],
    created_at=parse_github_datetime(repo_info.data["created_at"]),
    last_updated=parse_github_datetime(repo_info.data["last_updated"]),
)
```

Và khi user **update** project (VD: bấm nút "đồng bộ lại" để lấy pushed_at mới nhất), bạn tự gán lại `project.last_updated = parse_github_datetime(new_pushed_at)` trong code, chứ không dựa vào `onupdate` tự động của SQLAlchemy nữa.

### Vì sao cần hàm `parse_github_datetime`?

GitHub trả về chuỗi dạng `"2024-01-15T08:23:01Z"` — đây là `str`, không phải Python `datetime` object. Cột DB của bạn khai `Mapped[datetime]`, nên bạn cần convert chuỗi này thành `datetime` trước khi gán vào model:

```python
from datetime import datetime

def parse_github_datetime(value: str) -> datetime:
    # Python < 3.11 không hiểu chữ "Z" trong fromisoformat, cần đổi thành "+00:00"
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
```

(Nếu bạn dùng Python 3.11+ thì `fromisoformat` đã tự hiểu được `Z` luôn, không cần `.replace()`, nhưng viết vậy cho chắc và dễ đọc.)

---

**Tóm lại thay đổi so với ban đầu**: bỏ `server_default`/`onupdate` khỏi 2 cột này (vì giá trị không do DB tự sinh ra), thay vào đó bạn tự parse chuỗi ISO 8601 từ GitHub thành `datetime` và gán tay mỗi khi tạo/cập nhật project.
