from urllib.parse import urlparse

#github API
import httpx
from app.core.security import AppException
from fastapi import status
from app.core.config import settings
from app.schemas.response import ResponseModel

from datetime import datetime


# Xử lý chuỗi URL Github
def parse_github_url(url:str) -> tuple[str, str]:
    """
    Funct xử lý chuỗi link github. 
    - Phân tách link thành các phần như: scheme, domain, path, query,.... sau đó lấy phần path
    - Tiến hành cắt bỏ / ở 2 đầu path và split / để biến path thành 1 mảng chứa các giá trị quan trọng
    - Lấy 2 phần tử đầu của path return về owner, repo để bên github gọi API.
    """
    # urlparse() tách URL thành từng phần: scheme, domain, path, query,...
    # Ví dụ: "https://github.com/NguyenTAnh2005/Habit_Tracker?tab=readme"
    #   .path -> "/NguyenTAnh2005/Habit_Tracker"  (chỉ lấy phần path, bỏ domain + query)
    path = urlparse(url).path

    # .strip("/") bỏ dấu "/" ở đầu và cuối chuỗi -> "NguyenTAnh2005/Habit_Tracker"
        # Tách chuỗi path theo dấu "/" thành list
    # "NguyenTAnh2005/Habit_Tracker" -> ["NguyenTAnh2005", "Habit_Tracker"]
    # Nếu url có thêm path phía sau (vd .../Habit_Tracker/tree/main)
    # -> ["NguyenTAnh2005", "Habit_Tracker", "tree", "main"] (dư phần tử, không sao vì mình chỉ lấy 2 cái đầu)
    parts = path.strip("/").split("/")

    if len(parts)<2: 
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_URL",
            message=f"😓 URL is invalid."
        )

    # Lấy đúng 2 phần tử đầu tiên: owner (phần tử 0) và repo (phần tử 1)
    owner, repo = parts[0], parts[1]

    # removesuffix() chỉ xoá ".git" nếu chuỗi thực sự kết thúc bằng ".git"
    # phòng trường hợp user copy URL dạng clone: ".../Habit_Tracker.git"
    repo = repo.removesuffix(".git")

    # Trả về 1 tuple gồm 2 giá trị: (owner, repo)
    return owner, repo

# Xử lý chuỗi thời gian 
# GitHub trả về chuỗi dạng "2024-01-15T08:23:01Z" — đây là str, không phải Python datetime object. 
# Cột DB khai Mapped[datetime], nên cần convert chuỗi này thành datetime 
# trước khi gán vào model:
def parse_github_datetime(value: str)-> datetime:
    """
    Func xử lý chuyển đổi time fetch từ Repo Github sang Python datetime Object.
    vd: "2024-01-15T08:23:01Z"
    """
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


# Fetch Repo infomation
async def get_repo_info(url:str):
    """
        Funct nhận vào là chuỗi url sau đó lấy 2 thông tin owner và repo + API Key để get thông tin repo.
    """
    owner, repo = parse_github_url(url=url)
    headers ={
        "Authorization":f"token {settings.GITHUB_API_KEY}",
        "Accept": "application/vnd.github.v3+json"
    }

    base_repo_url = f"https://api.github.com/repos/{owner}/{repo}" 
    lang_repo_url = f"{base_repo_url}/languages"

    async with httpx.AsyncClient() as client:
        try:
            repo_response = await client.get(base_repo_url, headers=headers)
            if repo_response.status_code == 404:
                raise AppException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    error_code="REPOSITY_NOT_FOUND",
                    message=f"😓 Reposity not found. Check your url and try again."
                )
            if repo_response.status_code!= 200:
                raise AppException(
                    status_code=repo_response.status_code,
                    error_code="BAD_REQUEST",
                    message=f"😓 There are someething went wrong with your connection."
                )
            lang_response = await client.get(lang_repo_url, headers=headers)
            
            repo_data = repo_response.json()
            lang_data = lang_response.json()

            return ResponseModel(
                message="Fetching Github Reposity Info was successful.",
                data = {
                    "desc": repo_data.get("description"),
                    "created_at": repo_data.get("created_at"),
                    "last_updated":repo_data.get("pushed_at"),
                    "list_lang": list(lang_data.keys())
                }
            )
        
        except Exception as e:
            raise AppException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                error_code="SERVICE_UNAVAILABLE",
                message= f"😓 Cannot connect to Github Service: {str(e)}"
            )

    
