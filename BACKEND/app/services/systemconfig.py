from sqlalchemy.orm import Session
from typing import Optional
from fastapi import status

from app.core.exception import AppException

from app.models.models import SystemConfig
from app.crud import systemconfig as crud_sys_config
from app.schemas import systemconfig as schemas_sys_config


# get by id
def get_config(db: Session, config_id: int):
    return crud_sys_config.get_by_id(db=db, config_id=config_id)

# get all
def get_all_config(db: Session, skip: int , limit: int):
    return crud_sys_config.get_all(db=db, skip=skip, limit=limit)

# Check Conflict 
def check_conflict(db: Session, name: str, exclude_id: Optional[int]= None):
    dict_check={
        "name": name
    }
    query = db.query(SystemConfig)
    if exclude_id is not None:
        query = query.filter(SystemConfig.id!= exclude_id)
    
    for key,value in dict_check.items():
        if value and value is not None:
            col_check = getattr(SystemConfig, key)
            db_conflict = query.filter(col_check == value).first()
            if db_conflict:
                raise AppException(
                    status_code=status.HTTP_409_CONFLICT,
                    error_code="CONFLICT_DATA",
                    message= f"❌ There is a System Config object that has this {key} value in the database. Please check and try again."
                )
# create
def create_config(db: Session, create_data: schemas_sys_config.Create):
    check_conflict(db=db, name=create_data.name, exclude_id=None)
    return crud_sys_config.create(db=db, create_data=create_data)

# update 
def update_config(db: Session, target_id: int, update_data: schemas_sys_config.Update):
    db_config = get_config(db=db, config_id=target_id)
    check_conflict(db=db, exclude_id=target_id, name = update_data.name)
    return crud_sys_config.update(db=db, db_sys_config=db_config, update_data=update_data)

# delete 
def delete_config(db: Session, target_id: int):
    db_config = get_config(db=db, config_id=target_id)
    return crud_sys_config.delete(db=db, db_sys_config=db_config)


