from sqlalchemy import Column, Integer, String
from base_model import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}', email='{self.email}', password='{self.password}')"
