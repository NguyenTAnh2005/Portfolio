# info : giữ nguyên 
# project: list_project (ko cần total, limit, skip)
# timeline: list_timeline
# achievement: list_achievement
from pydantic import BaseModel

from app.schemas import achievement as achieve
from app.schemas import project
from app.schemas import timeline
from app.schemas import info

class Response(BaseModel):
    my_info: info.Response
    list_projects: list[project.Response]
    list_timelines: list[timeline.Response]
    list_achievements: list[achieve.Response]
