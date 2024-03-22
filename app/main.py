from fastapi import Depends, FastAPI, HTTPException, status, Response
import psycopg2
from psycopg2.extras import RealDictCursor
from .database import SessionLocal, engine, get_db
from . import database, models, schema
from sqlalchemy.orm import Session
from typing import List

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.get("/")
async def get_data():
    return {"data": "hello world"}

try:
    conn = psycopg2.connect(host='localhost', database='company', user='postgres', password='root', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("database connection established")
except Exception as error:
    print("Database connection error",  error)
    
    
    

@app.get("/posts", response_model=List[schema.Post])
async def get_post(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts
    


@app.post("/createpost", status_code=status.HTTP_201_CREATED, response_model=schema.Post)
async def create_post(post : schema.PostCreate ,db : Session = Depends(get_db)):
    new_posts = models.Post(**post.dict())
    db.add(new_posts)
    db.commit()
    db.refresh(new_posts)
    return new_posts



@app.get('/posts/{id}', response_model=schema.Post)
async def get_one_post(id: int, db : Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found with id : {id} ")
    return post



@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db : Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found with id : {id} ")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@app.put("/posts/{id}", response_model=schema.Post)
async def update_post(id: int, updated_post : schema.PostCreate, db : Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    post = post_query.first()
    if not post:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found with id : {id} ")
    
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()