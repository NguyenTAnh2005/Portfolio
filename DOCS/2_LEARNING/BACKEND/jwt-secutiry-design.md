# Thiết kế nâng cấp bảo mật JWT — Access + Refresh Token

> Bối cảnh: Portfolio project, FE React (Vite) và BE FastAPI tách biệt domain hoàn toàn ở production.
> Mục tiêu: thay thế cơ chế chỉ-dùng-access-token lưu `localStorage` (dễ bị đánh cắp qua XSS) bằng
> access token ngắn hạn (memory) + refresh token dài hạn (httpOnly cookie) có rotation + reuse detection.

---

## 1. Vì sao đổi

- `localStorage` đọc được bởi bất kỳ JS nào chạy trong trang → XSS = mất token ngay lập tức.
- Access token cũ sống 3 ngày → nếu bị đánh cắp, thiệt hại kéo dài 3 ngày.
- Không có cách nào thu hồi (revoke) một access token đã phát hành trước khi nó tự hết hạn.

## 2. Nguyên lý cốt lõi của thiết kế mới

| Token         | Nơi lưu                                     | Thời hạn | JS đọc được?                                 | Mục đích                                             |
| ------------- | ------------------------------------------- | -------- | -------------------------------------------- | ---------------------------------------------------- |
| Access token  | Biến state trong React (`AuthContext`, RAM) | 15 phút  | Có (nhưng chỉ tồn tại trong tab, mất khi F5) | Gắn vào header `Authorization` cho mọi API call      |
| Refresh token | httpOnly cookie (BE set qua `Set-Cookie`)   | 3 ngày   | **Không** — kể cả XSS cũng không đọc được    | Chỉ dùng để xin access token mới qua `/auth/refresh` |

Access token ngắn hạn giới hạn thời gian thiệt hại nếu bị lộ. Refresh token là bí mật quan trọng hơn
(sống lâu hơn) nên được cách ly khỏi JS hoàn toàn bằng `httpOnly`.

---

## 3. Backend

### 3.1 Cấu hình (`config.py`)

```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
REFRESH_TOKEN_EXPIRE_DAYS: int = 3
FRONTEND_ORIGIN: str  # dùng cho CORS whitelist, đọc từ .env
```

### 3.2 Model DB mới — bảng `refresh_tokens`

| Cột          | Kiểu                   | Ghi chú                                                              |
| ------------ | ---------------------- | -------------------------------------------------------------------- |
| `id`         | PK                     |                                                                      |
| `user_id`    | FK → users.id          | index                                                                |
| `token_hash` | String                 | SHA-256 hash của refresh token thô, **không lưu plain text** — index |
| `expires_at` | DateTime               |                                                                      |
| `revoked`    | Boolean, default False |                                                                      |
| `created_at` | DateTime               |                                                                      |

Lý do hash (không cần bcrypt): refresh token là chuỗi random entropy cao do server tự sinh
(không phải password người dùng tự nghĩ), không cần thuật toán chậm chống brute-force —
SHA-256 là đủ, tương tự cách không ai brute-force nổi một UUID ngẫu nhiên.

### 3.3 Logic tạo token

- `create_access_token(user)` — giữ nguyên cơ chế JWT hiện tại, chỉ đổi thời hạn về 15 phút.
- `create_refresh_token(user, db)` — sinh chuỗi random (vd `secrets.token_urlsafe(32)`),
  hash lại, lưu row mới vào `refresh_tokens`, trả về chuỗi **thô** (chưa hash) để set vào cookie.

### 3.4 Luồng `POST /auth/login`

1. Verify email/password như hiện tại.
2. Tạo access token + refresh token (bước 3.3).
3. Response: access token trong JSON body; refresh token set qua `Set-Cookie`.

### 3.5 Luồng `POST /auth/refresh`

1. Đọc refresh token từ cookie request gửi lên (không phải từ body).
2. Hash chuỗi nhận được, tìm row khớp `token_hash` trong DB.
3. Không tìm thấy → 401, yêu cầu đăng nhập lại.
4. Tìm thấy nhưng `revoked = True` → **dấu hiệu reuse** (token đã bị dùng rồi mà vẫn có người gửi lên):
   - Revoke toàn bộ refresh token khác đang active của `user_id` đó (không chỉ riêng token này).
   - Trả 401, buộc đăng nhập lại từ đầu.
5. Tìm thấy, hợp lệ, chưa hết hạn, chưa revoked → **rotation**:
   - Đánh dấu row hiện tại `revoked = True`.
   - Tạo access token mới + refresh token mới (row mới trong DB).
   - Set cookie refresh token mới, trả access token mới trong JSON body.

### 3.6 Luồng `POST /auth/logout`

1. Đọc refresh token từ cookie, hash, tìm đúng row, set `revoked = True`.
2. Xóa cookie: gọi `response.delete_cookie()` với **cùng** `key`, `path`, `httponly`, `secure`, `samesite`
   như lúc set — sai một thuộc tính là trình duyệt coi là cookie khác, không xóa được.

### 3.7 Cookie attributes (cho refresh token)

```python
response.set_cookie(
    key="refresh_token",
    value=raw_refresh_token,
    httponly=True,      # JS không đọc được — chặn XSS lấy token
    secure=True,         # chỉ gửi qua HTTPS tới domain BE — bắt buộc BE chạy HTTPS
    samesite="none",     # bắt buộc vì FE/BE khác domain hoàn toàn — LÀM MẤT phòng thủ CSRF mặc định
    path="/auth",        # thu hẹp phạm vi cookie chỉ gửi tới các route /auth/*
    max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
)
```

### 3.8 Bù đắp CSRF (do `SameSite=None` không tự chống được)

`SameSite=None` cho phép cookie gửi cả trong request cross-site — tức bỏ đi lớp chặn CSRF mặc định.
Bù lại bằng cách kiểm tra `Origin` header ở các endpoint thay đổi trạng thái (`/auth/refresh`,
`/auth/logout`): chỉ chấp nhận nếu `Origin` khớp đúng `FRONTEND_ORIGIN` trong whitelist.

### 3.9 CORS

```python
allow_origins=[settings.FRONTEND_ORIGIN],  # KHÔNG dùng "*" khi allow_credentials=True
allow_credentials=True,
```

---

## 4. Frontend

### 4.1 `AuthContext`

- State: `accessToken` (useState, **không** đọc/ghi `localStorage`).
- `useEffect` lúc app mount: gọi `POST /auth/refresh` một lần để "phục hồi phiên" —
  vì access token mất khi F5, nhưng cookie refresh vẫn còn nên có thể lấy access token mới ngay
  mà không cần đăng nhập lại.
- `login(accessToken)` — chỉ set state, không còn `localStorage.setItem`.
- `logout()` — gọi `POST /auth/logout` (để revoke ở BE + xóa cookie), rồi clear state.

### 4.2 `axiosInstance`

- Bật `withCredentials: true` (global hoặc per-request) — bắt buộc để trình duyệt gửi kèm cookie
  cross-origin.
- Request interceptor: gắn `Authorization: Bearer <accessToken>` từ state/context — **không** đọc
  từ `localStorage` nữa.
- Response interceptor (không phải request interceptor): bắt lỗi `401` → gọi `/auth/refresh` →
  nếu thành công, cập nhật access token mới, retry lại request gốc; nếu thất bại, clear state,
  điều hướng `/log-in`.

### Note thêm về Axios

<blockquote>

**Cách Axios lưu trữ thông tin request cũ**

[`Xem code xử lý tại đây`](../../../FRONTEND/src/services/instance/manualConfig.js)

Khi một request thất bại (ví dụ lỗi 401 Unauthorized hoặc 500), Axios sẽ trả về một đối tượng error. Trong đối tượng này có:

- error.`config`: Lưu lại nguyên bản cấu hình của request vừa gọi (gồm url, method, headers, data, params, baseURL,...).
- error.`response`: Chứa thông tin phản hồi từ server (status code, data lỗi,...).

</blockquote>

## 5. Việc cần dọn khi refactor

- Bỏ toàn bộ `localStorage.getItem/setItem/removeItem('jwt-token')` ở FE.
- `ACCESS_TOKEN_EXPIRE_MINUTES` default trong `config.py` hiện là 10 — đồng bộ về 15 và xóa giá trị
  3 ngày cũ trong `.env`.
- `UserLogin` schema trong `schemas/auth.py` không dùng (đang dùng `OAuth2PasswordRequestForm`) — xóa
  hoặc note lại lý do giữ.
- `/auth/login` hiện trả JSON thô — cân nhắc bọc lại theo `ResponseModel`/`TokenResponse` khi sửa.

## 6. Việc cố tình để dành sau (out of scope đợt này)

- Multi-device / xem danh sách phiên đăng nhập / logout từ xa thiết bị khác — cần thêm cột
  `device_info`/`user_agent` vào `refresh_tokens`, không phá vỡ schema hiện tại nên thêm sau được.
- Job dọn dẹp định kỳ các row hết hạn/revoked trong `refresh_tokens` (tối ưu, không phải yêu cầu
  bảo mật — token hết hạn/revoked vẫn bị từ chối khi verify dù row còn nằm trong DB).
