# 📝 [Note] Tại sao API Login không dùng cấu trúc ResponseModel?

**Tóm tắt:** Tài liệu này giải thích lý do tại sao API cấp phát Token (Login) phải trả về JSON phẳng theo chuẩn thay vì dùng class `ResponseModel` chung của dự án. (được tóm tắt bởi Gemini Pro)

---

## 1. Vấn đề gặp phải

Trong dự án, chúng ta sử dụng `ResponseModel` làm khuôn chuẩn cho toàn bộ API nhằm đảm bảo tính đồng nhất:

```json
{
  "data": { ... },
  "message": "Thành công!"
}

```

Tuy nhiên, khi áp dụng cấu trúc này cho API `/login`, mặc dù Postman hay React gọi API vẫn nhận được dữ liệu, nhưng **nút Authorize (Ổ khóa xanh) trên Swagger UI lại bị vô hiệu hóa**. Hậu quả là khi test các API yêu cầu xác thực (như lấy Info, đổi Password), hệ thống luôn báo lỗi: _"Phiên đăng nhập đã kết thúc" (401 Unauthorized)_.

## 2. Bản chất của vấn đề

### A. Sự khắt khe của chuẩn OAuth2 quốc tế

Swagger UI được xây dựng dựa trên giao thức bảo mật **OAuth2** (RFC 6749). Giao thức này quy định "cứng" rằng API cấp phát Token (Token Endpoint) **bắt buộc** phải trả về một JSON phẳng (Flat JSON) với định dạng chính xác như sau:

```json
{
  "access_token": "chuỗi_jwt_dài_ngoằng",
  "token_type": "bearer"
}
```

### B. Cơ chế "mù" của Swagger UI

Khi API Login được bọc bởi `ResponseModel`, cục JSON thực tế trả về sẽ là:

```json
{
  "data": {
    "access_token": "chuỗi_jwt",
    "token_type": "bearer"
  },
  "message": "Đăng nhập thành công"
}
```

Khi đó, Javascript nội bộ của Swagger UI sẽ nhảy vào tìm key `"access_token"` ở cấp độ ngoài cùng (root). Vì không thấy (do nó bị giấu trong key `"data"`), Swagger UI tự kết luận là **không có Token**. Nó liền lưu giá trị `undefined` vào bộ nhớ.

### C. Lỗi dây chuyền (Domino Effect)

Khi test một API khác (ví dụ `/get-me`), thằng `oauth2_scheme` của FastAPI sẽ trích xuất Header từ request do Swagger UI gửi lên:
`Authorization: Bearer undefined`

Chuỗi `"undefined"` bị ném vào hàm giải mã của thư viện `jose`, gây ra lỗi `JWTError`, dẫn đến việc Backend từ chối request.

## 3. Cách giải quyết & Bài học rút ra (Best Practice)

**Cách giải quyết:**
Gỡ bỏ lớp bọc `ResponseModel` tại API `/login` và trả về trực tiếp dict chứa token. Các API khác trong hệ thống vẫn dùng `ResponseModel` bình thường.

```python
# CODE CHUẨN CHO API LOGIN
@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(connect_db)):
    jwt_sig = logic_login(...)
    # Phải trả về JSON phẳng, không có vỏ bọc
    return {
        "access_token": jwt_sig,
        "token_type": "bearer"
    }

```

**🔥 Bài học (Best Practice trong ngành):**

1. **API Login là một ngoại lệ:** Trong thiết kế RESTful API, Endpoint cấp phát Token được coi là một điểm giao tiếp với các hệ thống ngoài (OAuth2, OpenID Connect). Phải tuân thủ chuẩn quốc tế (RFC) thay vì chuẩn nội bộ.
2. **Không cố gắng sửa mã nguồn của công cụ:** Không thể ép Swagger UI hay các thư viện Frontend tiêu chuẩn (như NextAuth) phải hiểu cấu trúc `.data.access_token` tự chế. Thay đổi Backend để đáp ứng chuẩn chung là con đường tối ưu và chuyên nghiệp nhất.
