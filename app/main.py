from typing import Optional
from fastapi import FastAPI, Body, Response, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
app = FastAPI()
my_posts = []


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


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
    return {
        'data': my_posts
    }


@app.post('/posts', status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    saved_post = post.dict()
    saved_post['id'] = len(my_posts) + 1
    my_posts.append(saved_post)
    return {
        'data': saved_post
    }


def find_post(id: int):
    for post in my_posts:
        if post['id'] == id:
            return post


def find_post_index(id: int):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i
    return -1


@app.get('/posts/latest')
def get_latest():

    post = my_posts[-1] if my_posts else None
    return {
        'data': post
    }


@app.get('/posts/{id}')
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {id} not found')

    return {
        'data': post
    }


@app.put('/posts/{id}')
def update_post(id: int, post: Post):
    idx = find_post_index(id)
    if idx == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {id} not found')
    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[idx] = post_dict
    return {
        'data': post_dict
    }


@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    idx = find_post_index(id)
    if idx == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {id} not found')
    my_posts.pop(idx)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
