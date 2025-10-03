from sqlalchemy import Column,Integer,String , ForeignKey,DateTime
from database import Base,engine
from datetime import datetime
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ ='register'
    id = Column(Integer, primary_key=True,index=True)
    username= Column(String(50),unique=True, index=True)
    email=Column(String(50),unique=True,index=True)
    password=Column(String(300) ,index=True)
    role=Column(String(20),index=True)

class perticular_user_tasks(Base):
    __tablename__='taskassign'
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String(500))
    description=Column(String(2000))
    status=Column(String(300))
    created_at = Column(DateTime, default=datetime.now)
    created_by= Column(Integer,ForeignKey('register.id'))
    assigned_to= Column(Integer,ForeignKey('register.id'))
    
    creater= relationship('User',foreign_keys=[created_by],backref="task_created")
    assignee=relationship('User',foreign_keys=[assigned_to],backref="assigned")

Base.metadata.create_all(bind=engine)
