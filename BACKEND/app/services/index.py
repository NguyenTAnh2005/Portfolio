from sqlalchemy.orm import Session

from app.crud import info as crud_info
from app.crud import project as crud_project
from app.crud import timeline as crud_timeline
from app.crud import achievement as crud_achieve

from app.schemas import info as schemas_info
from app.schemas import index as schemas_index

INDEX_QUERY_CONFIG = {
    "project": {"skip": 0, "limit": 3, "sort_by": "id", "order": "desc"},
    "timeline": {"skip": 0, "limit": 10, "sort_by": "id", "order": "asc"},
    "achievement": {"skip": 0, "limit": 3, "sort_by": "id", "order": "desc"},
}

def get_index_list(
    db: Session
):
    db_info = crud_info.get_by_id(db= db, info_id=1)
    list_timelines = crud_timeline.get_list(db=db, **INDEX_QUERY_CONFIG["timeline"])
    list_projects = crud_project.get_list(db=db, **INDEX_QUERY_CONFIG["project"])
    list_achievements = crud_achieve.get_list(db=db, **INDEX_QUERY_CONFIG["achievement"])

    return schemas_index.Response(
        my_info=db_info,
        list_timelines=list_timelines,
        list_projects=list_projects,
        list_achievements=list_achievements
    )

    