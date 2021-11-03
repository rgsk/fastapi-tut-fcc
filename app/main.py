from typing import Optional
from fastapi import FastAPI, Body, Response, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


while True:
    try:
        conn = psycopg2.connect(
            host='localhost', database='fastapi', user='postgres', password='password', cursor_factory=RealDictCursor)
        # without cursor_factory we will only get values
        # so we add cursor_factory to return column names too
        cursor = conn.cursor()
        print('Database connection successfull')
        break
    except Exception as error:
        print('Connecting to Database failed')
        print('Error: ', error)
        time.sleep(2)


@app.get('/')
async def root():
    return {
        'message': 'welcome to my api 123'
    }


@app.get('/posts')
def get_posts():
    cursor.execute('''
        SELECT * FROM posts
    ''')
    posts = cursor.fetchall()
    return {
        'data': posts
    }


@app.post('/posts', status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute('''
        INSERT INTO posts (title, content, published) VALUES (%s, %s, %s)
        RETURNING *
    ''', (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {
        'data': new_post
    }


@app.get('/posts/latest')
def get_latest():

    cursor.execute('''SELECT * FROM posts ORDER BY created_at DESC LIMIT 1''')
    latest_post = cursor.fetchone()
    return {
        'data': latest_post
    }


@app.get('/posts/{id}')
def get_post(id: int):
    cursor.execute('''SELECT * FROM posts WHERE id = %s''', (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {id} not found')

    return {
        'data': post
    }


@app.put('/posts/{id}')
def update_post(id: int, post: Post):
    cursor.execute("""
        UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s
        RETURNING *
    """, (post.title, post.content, post.published, str(id))
    )
    updated_post = cursor.fetchone()
    conn.commit()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {id} not found')

    return {
        'data': updated_post
    }


@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(
        '''DELETE FROM posts WHERE id = %s returning  *''', (str(id))
    )
    deleted_post = cursor.fetchone()
    conn.commit()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {id} not found')
    return Response(status_code=status.HTTP_204_NO_CONTENT)
