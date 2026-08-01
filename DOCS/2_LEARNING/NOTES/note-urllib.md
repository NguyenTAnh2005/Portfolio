```python
from urllib.parse import urlparse

def parse_github_url(url: str) -> tuple[str, str]:
    # urlparse() tách URL thành từng phần: scheme, domain, path, query,...
    # Ví dụ: "https://github.com/NguyenTAnh2005/Habit_Tracker?tab=readme"
    #   .path -> "/NguyenTAnh2005/Habit_Tracker"  (chỉ lấy phần path, bỏ domain + query)
    # .strip("/") bỏ dấu "/" ở đầu và cuối chuỗi -> "NguyenTAnh2005/Habit_Tracker"
    path = urlparse(url).path.strip("/")

    # Tách chuỗi path theo dấu "/" thành list
    # "NguyenTAnh2005/Habit_Tracker" -> ["NguyenTAnh2005", "Habit_Tracker"]
    # Nếu url có thêm path phía sau (vd .../Habit_Tracker/tree/main)
    # -> ["NguyenTAnh2005", "Habit_Tracker", "tree", "main"] (dư phần tử, không sao vì mình chỉ lấy 2 cái đầu)
    parts = path.split("/")

    if len(parts) < 2:
        raise ValueError("URL không hợp lệ")

    # Lấy đúng 2 phần tử đầu tiên: owner (phần tử 0) và repo (phần tử 1)
    owner, repo = parts[0], parts[1]

    # removesuffix() chỉ xoá ".git" nếu chuỗi thực sự kết thúc bằng ".git"
    # phòng trường hợp user copy URL dạng clone: ".../Habit_Tracker.git"
    repo = repo.removesuffix(".git")

    # Trả về 1 tuple gồm 2 giá trị: (owner, repo)
    return owner, repo
```

`tuple` giống như `list`, nhưng **không thể thay đổi sau khi tạo** (immutable) — dùng khi bạn muốn gom một nhóm giá trị cố định lại với nhau, ví dụ ở đây là "1 cặp owner-repo luôn đi kèm nhau".

`tuple[str, str]` trong khai báo kiểu (type hint) nghĩa là: "hàm này trả về 1 tuple gồm đúng 2 phần tử, cả 2 đều là string".

Có 2 cách để lấy giá trị ra khi gọi hàm bên `github_service.py`:

**Cách 1 — unpack trực tiếp (khuyến khích, ngắn gọn nhất):**

```python
owner, repo = parse_github_url(url)
# giờ owner = "NguyenTAnh2005", repo = "Habit_Tracker"
# dùng y hệt như 2 biến bình thường
owner_repo = f"{owner}/{repo}"
```

**Cách 2 — nhận về nguyên tuple rồi truy cập theo index (giống list):**

```python
result = parse_github_url(url)
owner = result[0]
repo = result[1]
```

Cách 1 là cách người ta hay dùng nhất vì Python cho phép "unpack" (giải nén) tuple ngay lúc gán biến — miễn số biến bên trái khớp đúng số phần tử của tuple bên phải.

## Ghép vào `github_service.py` của bạn

Đoạn gọi hàm cũ:

```python
parts = url.rstrip("/").split("/")
if len(parts) < 2:
    raise HTTPException(...)
owner_repo = f"{parts[-2]}/{parts[-1]}"
```

Thay bằng:

```python
from app.utils.github_utils import parse_github_url  # import hàm mới

async def get_reposity_info(url: str):
    try:
        owner, repo = parse_github_url(url)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="🤡 Github URL is not valid! Try Again!"
        )
    owner_repo = f"{owner}/{repo}"
    # phần code phía dưới giữ nguyên...
```

Lưu ý: `parse_github_url` raise `ValueError` (lỗi Python thuần), còn service của bạn cần raise `HTTPException` (lỗi FastAPI hiểu được để trả về client) — nên phải bắt bằng `try/except` để "chuyển đổi" loại lỗi như trên.
