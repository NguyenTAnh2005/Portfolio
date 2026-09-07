# `🎯 Note về thuộc tính Datetime trong Model (SQLAlchemy)`

<blockquote>

### Máy tính lưu thời gian thế nào?

Máy tính không lưu "8 giờ tối" — nó lưu thời gian dưới dạng một **mốc tuyệt đối** (thường tính từ 1/1/1970, gọi là Unix timestamp), rồi khi hiển thị mới "dịch" ra giờ địa phương.

Vấn đề là: "8 giờ tối" ở Việt Nam và "8 giờ tối" ở Mỹ là hai thời điểm khác nhau hoàn toàn. Nếu bạn chỉ lưu con số "20:00" mà không ghi rõ nó là giờ ở đâu, thì dữ liệu đó **vô nghĩa** khi hệ thống của bạn có người dùng/server ở nhiều nơi khác nhau.

→ Đó là lý do người ta luôn khuyên: **lưu thời gian theo UTC** (giờ chuẩn quốc tế, không lệch theo vùng), rồi khi hiển thị cho người dùng thì mới convert sang giờ địa phương của họ (VD: +7 cho VN).

### "Naive" và "Aware" trong Python

- **Naive datetime**: một `datetime` object _không biết_ nó thuộc timezone nào. VD: `datetime(2026, 7, 28, 20, 0)` — con số này có thể là giờ VN, giờ Mỹ, giờ UTC... không ai biết, vì nó không mang theo thông tin timezone.
- **Aware datetime**: một `datetime` object có gắn kèm thông tin timezone. VD: `2026-07-28T20:00:00+07:00` — rõ ràng đây là 8h tối giờ VN.

**Nguyên tắc**: luôn làm việc với **aware datetime**, tránh naive datetime bằng mọi giá. Naive datetime là nguồn gốc của 90% bug liên quan đến thời gian.

</blockquote>

## Cột `DateTime(timezone=True)` nghĩa là gì?

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

Hãy tưởng tượng bạn có 1 quyển sổ (table `project`), mỗi khi bạn viết vào sổ (insert) hoặc sửa 1 dòng đã viết (update), bạn cần ghi ngày giờ vào 2 cột `created_at` và `last_updated`. Câu hỏi là: **ai cầm bút ghi ngày giờ đó, và ghi vào lúc nào?**

- **`default=...`**: Bạn (Python code) tự tính giờ trước, rồi gửi kèm theo lệnh "hãy viết dòng này vào sổ". Nghĩa là Python phải tự lấy giờ máy (`datetime.now()`) rồi nhét vào — nếu giờ máy Python bị sai (lệch timezone, sai đồng hồ hệ thống...) thì dữ liệu sai theo.

- **`server_default=...`**: Bạn nói với người giữ sổ (Postgres): "mỗi khi có ai viết dòng mới, anh tự ghi giờ hiện tại giúp tôi". Postgres tự làm, không cần Python tính toán gì cả → đáng tin cậy hơn vì giờ luôn lấy từ 1 nguồn duy nhất (server DB).

- **`onupdate=...`**: Đây là dặn dò riêng cho SQLAlchemy (không phải Postgres): "mỗi khi ai đó sửa 1 dòng **thông qua ORM Python** (gọi `session.commit()`), hãy tự cập nhật lại giờ ở cột này". Nó chỉ hoạt động nếu bạn sửa data bằng Python/ORM — nếu ai đó chạy lệnh SQL `UPDATE` trực tiếp trong pgAdmin thì cột này **sẽ không tự cập nhật**.

→ Tóm lại bảng đó chỉ đơn giản là: 3 cách khác nhau để trả lời câu hỏi "giá trị time này do ai tính, và tính vào lúc nào".

**Ghi nhớ đơn giản**: `created_at` chỉ set 1 lần → chỉ cần `server_default`. `last_updated` cần set lại mỗi lần sửa → cần thêm `onupdate`.

## 6. Ở phía backend (API trả về cho frontend) thì sao?

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

## 7. ISO 8601 là gì?

Đây là 1 **chuẩn quốc tế** để viết ngày giờ dưới dạng chữ, sao cho máy tính ở bất kỳ đâu cũng đọc và hiểu đúng, không bị nhầm lẫn (khác với kiểu viết ngày kiểu Mỹ `07/28/2026` hay kiểu VN `28/07/2026` dễ gây hiểu nhầm).

Format chuẩn: `YYYY-MM-DDTHH:MM:SS±HH:MM`

Ví dụ: `2026-07-28T13:00:00+00:00` nghĩa là ngày 28/7/2026, lúc 13:00, theo múi giờ UTC+0.

GitHub API trả về theo dạng: `2024-01-15T08:23:01Z` — chữ **`Z`** ở cuối là viết tắt của "Zulu time", tức là UTC+0 (giống hệt `+00:00`, chỉ viết gọn hơn).

GitHub trả về chuỗi dạng `"2024-01-15T08:23:01Z"` — đây là `str`, không phải Python `datetime` object. Cột DB của bạn khai `Mapped[datetime]`, nên bạn cần convert chuỗi này thành `datetime` trước khi gán vào model:

```python
from datetime import datetime

def parse_github_datetime(value: str) -> datetime:
    # Python < 3.11 không hiểu chữ "Z" trong fromisoformat, cần đổi thành "+00:00"
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
```

(Nếu bạn dùng Python 3.11+ thì `fromisoformat` đã tự hiểu được `Z` luôn, không cần `.replace()`, nhưng viết vậy cho chắc và dễ đọc.)

---
