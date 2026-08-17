from sqlalchemy.orm import Session

from app.schemas import info as schemas_info
from app.crud import info as crud_info


def get_info(db: Session, info_id: int):
    return crud_info.get_by_id(db=db, info_id=info_id)

def update_info(db: Session, target_id: int, update_data:schemas_info.Update):
    db_info = crud_info.get_by_id(db=db, info_id=target_id)
    return crud_info.update(db=db, db_info=db_info, update_data=update_data)


    

