# đang tìm việc available_for_work
# đang bảo trì web maintenance_mode
# link cv pdf resume_url

from app.models.models import SystemConfig
from sqlalchemy.orm import Session

def seed_config(db: Session):
    config_seed_data = [
        { "name": "resume_url","value": "have-not-done-yet"}
        ,
        { "name": "available_for_work", "value": True}
        ,
        { "name": "web_maintenance_mode","value": False}
    ]

    for config in config_seed_data:
        db_config = SystemConfig(name = config["name"], value = config["value"])
        db.add(db_config)
        
    print(f"⚠️  Added System Config seed data ....... waiting commit .............")

