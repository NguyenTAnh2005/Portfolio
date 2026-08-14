from fastapi import status
from sqlalchemy.orm import Session

from app.core.exception import AppException

from app.models.models import SystemConfig
from app.schemas import systemconfig as schemas_sys_config

# get
def get_by_id(db: Session, config_id: int):
    db_config = db.query(SystemConfig).filter(SystemConfig.id == config_id).first()
    if not db_config:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="CONFIG_NOT_FOUND",
            message=f"❌ The system-config does not exist in system. Please verify the ID and try again."
        )
    return db_config

# list
def get_all(db: Session, skip: int , limit: int):
    query = db.query(SystemConfig)
    list_data = query.offset(skip).limit(limit).all()
    return list_data

# create
def create(db: Session, create_data: schemas_sys_config.Create):
    # new_config = SystemConfig(name = create_data.name, value = create_data.value)
    new_config = SystemConfig(**create_data.model_dump())
    db.add(new_config)
    db.commit()
    db.refresh(new_config)

    return new_config

# update
def update(db: Session, db_sys_config: SystemConfig, update_data: schemas_sys_config.Update):
    dict_update = update_data.model_dump(exclude_unset=True)
    for key,value in dict_update.items():
        setattr(db_sys_config, key, value)
    db.add(db_sys_config)
    db.commit()
    db.refresh(db_sys_config)

    return db_sys_config
    
# delete
def delete(db: Session, db_sys_config: SystemConfig):
    db.delete(db_sys_config)
    db.commit()
    
    return


