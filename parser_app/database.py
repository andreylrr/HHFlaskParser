from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import configparser as cfg

config_db = cfg.ConfigParser()
config_db.read("../web_app/hh_config.ini")
engine = create_engine(config_db["SQLite"]["path"])
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = Session()
Base = declarative_base()
Base.metadata.create_all(bind=engine)

