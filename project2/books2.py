from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

class Book:
  id: int
  title: str
  author: str 
  description: str
  rating: int
  publish_date: int

  def __init__(self, id: int, title: str, author: str, description: str, rating: int, publish_date: int):
    self.id = id
    self.title = title
    self.author = author
    self.description = description
    self.rating = rating
    self.publish_date = publish_date


class BookRequest(BaseModel):
  id: Optional[int] = Field(title="id is not needed")
  title: str = Field(min_length=3, max_length=50)
  author: str = Field(min_length=1, max_length=50)
  description: str = Field(min_length=1, max_length=100)
  rating: int = Field(gt=0, lt=6)
  publish_date: int = Field(gt=1900, lt=2022)

  # defaults for the schema in the docs
  class Config:
    schema_extra = {
      'example': {
        'title': 'A new book',
        'author': 'John Doe',
        'description': 'A book about something',
        'rating': 5,
        'publish_date': 2021
      }
    }


BOOKS = [
  Book(1, "Computer Science Pro", "John Doe", "A book about computer science", 5, 2021),
  Book(2, "Be fast with FastAPI", "John Doe", "This is a great book", 5, 2000),
  Book(3, "Python Pro", "John Doe", "A book about python", 5, 2012),
  Book(4, "Java Pro", "John Doe", "A book about java", 3, 2021),
  Book(5, "C++ Pro", "John Doe", "A book about c++", 5, 2008),
  Book(6, "C# Pro", "John Doe", "A book about c#", 4, 2021),
  Book(7, "C Pro", "John Doe", "A book about c", 4, 1978),
  Book(8, "The Hobbit", "J.R.R. Tolkien", "A book about a hobbit", 5, 1985),
  Book(9, "The Lord of the Rings", "J.R.R. Tolkien", "A book about a ring", 5, 1979),
  Book(10, "The Silmarillion", "J.R.R. Tolkien", "A book about a silmarillion", 5, 1977),
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
  return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
  for book in BOOKS:
    if book.id == book_id:
      return book
  raise HTTPException(status_code=404, detail="Book id does not exist")


@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6)):
  return list(filter(lambda book: book.rating == book_rating, BOOKS))


@app.get("/books/publish_date/", status_code=status.HTTP_200_OK)
async def read_book_by_publish_date(publish_date: int = Query(gt=1900, lt=2022)):
  return list(filter(lambda book: book.publish_date == publish_date, BOOKS))


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
  new_book = Book(**book_request.dict())
  BOOKS.append(find_book_id(new_book))
  return "Book created successfully"


def find_book_id(book: Book):
  book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
  return book


@app.put("/books/update-book/", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
  book_changed = False
  for i in range(len(BOOKS)):
    if BOOKS[i].id == book.id:
      BOOKS[i] = book
      book_changed = True
  if not book_changed:
    raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
  book_changed = False
  for i in range(len(BOOKS)):
    if BOOKS[i].id == book_id:
      del BOOKS[i]
      book_changed = True
      return "Book deleted successfully"
  if not book_changed:
      raise HTTPException(status_code=404, detail="Book not found")