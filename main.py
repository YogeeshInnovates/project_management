from fastapi import FastAPI ,Depends,HTTPException,Response,Cookie
from sqlalchemy.orm import Session
from database import get_db 
from sqlalchemy import text,or_

from schemas import UserCreate,perticular_user_tasks
from models import User ,perticular_user_tasks as TaskModel
from passlib.context import CryptContext
from datetime import timedelta,datetime
import jwt
from fastapi.security import OAuth2PasswordBearer

app=FastAPI()

pwd_context=CryptContext(schemes=['bcrypt'],deprecated="auto")
def hashpassword(password:str):
    return pwd_context.hash(password)


SECRET_KEY = "mysecretkey2"
ALGORITHM = "HS256"

     
def get_current_user(token: str=  Cookie(None, alias="access_token"),db : Session=Depends(get_db)):
    try:
        payload = jwt.decode(token,SECRET_KEY ,algorithms=[ALGORITHM])
        user_id=payload.get('user_id')
        user= db.query(User).filter(User.id== user_id).first()
        if not user:
            raise HTTPException(status_code=401,detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401,detail="Token Expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')



@app.get('/')
def test_connect(db:Session = Depends(get_db)):
        try:
        # ✅ must wrap in text()
            result = db.execute(text("SELECT 1")).scalar()
            return {"status": "connected", "result": result}
        except Exception as e:
            return {"status": "error", "detail": str(e)}

@app.post('/register')
def register(user: UserCreate,db:Session=Depends(get_db)):
    existing_user= db.query(User).filter(User.email==user.email).first()
    if existing_user:
          return HTTPException(status_code=400 ,detail="already account is there with this email")
    
    if user.role=="admin" and user.admin_code=="2468":
        newuser=User(
                    username= user.username,
                    email=user.email,
                    password=hashpassword(user.password),
                    role='admin'
          )
    elif user.role=="admin" and user.admin_code !="2468":
        raise HTTPException(status_code=401,detail="you entered wrong admin code")

    else:

        newuser=User(
                        username= user.username,
                        email=user.email,
                        password=hashpassword(user.password),
                        role='user'
            )
    db.add(newuser)
    db.commit()
    db.refresh(newuser)
    return {"message":"successfully entered"}
    

@app.post('/login')
def login(email:str,password:str,response: Response, db : Session=Depends(get_db)):
    user=db.query(User).filter(User.email==email).first()
    if not user or not pwd_context.verify(password,user.password):
        raise HTTPException("User not  available")
    payload={
        'user_id':user.id,
       "exp": datetime.utcnow() + timedelta(hours=12)
        
            }
    token = jwt.encode(payload,SECRET_KEY ,algorithm=ALGORITHM)
    response.set_cookie(
        key="access_token",
        value= token,
        httponly=True,
        max_age=12*3600  #12 hours
    )
    return {"access_token":token}



@app.post('/create_task_perticular_user')
def create_task_perticular_user(task:perticular_user_tasks, db:Session=Depends(get_db),current_user: User=Depends(get_current_user)):
    assignee= db.query(User).filter(User.email== task.assigned_to_email).first()
    if not assignee:
        raise HTTPException(404,"User not found")
    new_task=TaskModel(
    title=task.title,
    description=task.description,
    status=task.status,
    created_by= current_user.id,
    assigned_to= assignee.id,
    
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"message":"task created and asign successfully"}

   
@app.get('/view_all_task')
def  view_all_task(db:Session=Depends(get_db),current_user : User=Depends(get_current_user)):
    if current_user.role =="admin":
        all_tasks=db.query(TaskModel).all()
    elif current_user.role =="user":
        all_tasks= db.query(TaskModel).filter (or_(
            TaskModel.assigned_to == current_user.id,
            TaskModel.created_by == current_user.id
        )).all()
    return all_tasks


@app.put("/update_task/{task_id}")
def update_task(task_id:int,task:perticular_user_tasks , db:Session=Depends(get_db),current_user : User=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update tasks")
    
    existing_task=db.query(TaskModel).filter(task_id == TaskModel.id).first()

    if task.title:
        existing_task.title=task.title
    elif task.description:
        existing_task.description=task.description
    elif task.status:
        existing_task.status=task.status
    elif task.assigned_to_email:
        existing_task.assigned_to_email=task.assigned_to_email
    db.commit()
    db.refresh(existing_task)
    return {"message":"successfully updated"}


@app.delete("/delete_task/{task_id}")
def delete_task(task_id:int, db:Session=Depends(get_db),current_user: User=Depends(get_current_user)):
    if current_user.role !="admin":
        raise HTTPException(status_code=403, detail="Only admin can delete tasks")
    perticular_task= db.query(TaskModel).filter(TaskModel.id==task_id).first()

    if not perticular_task:
        raise HTTPException(statuscode=401,details="No task present")
    db.delete(perticular_task)
    db.commit()
    return {"message":"deleted successfully"}  

@app.put("/update_status/{task_id}")
def update_status(task_id:int, status:str , db:Session=Depends(get_db)):
    tasks=db.query(TaskModel).filter(TaskModel.id==task_id).first()
    if not tasks:
        raise HTTPException(status_code=401,details="no task available")
    tasks.status=status
    db.commit()
    db.refresh(tasks)
    
    return {"message": "Status updated", "task": tasks}

@app.get("/pending_task/{status}")
def pending_task(status:str , db:Session=Depends(get_db),current_user : User=Depends(get_current_user)):
    if current_user.role=="user":
        peding_tasks=db.query(TaskModel).filter(TaskModel.assigned_to==current_user.id, TaskModel.status == status).all()

    elif current_user.role=="admin":
        peding_tasks=db.query(TaskModel).filter(TaskModel.status == status).all()
    return peding_tasks
    


@app.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}


