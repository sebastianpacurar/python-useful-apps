import json
import os
from datetime import datetime

from test_data_generators.book_generator import create_books_list, Book


def test_create_books_list():
    num_entries = 10
    books = create_books_list(num_entries)
    assert len(books) == num_entries
    for book in books:
        assert isinstance(book, Book)


def test_json_to_file():
    num_entries = 20
    time_stamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    books_dir_path = os.path.join('..', '..', 'data_sets', 'test_data', 'books')
    file_name = f'test_generated_books_{time_stamp}.json'
    file_path = os.path.join(books_dir_path, file_name)

    books = create_books_list(num_entries)
    json_data = [book.dict(by_alias=True) for book in books]

    with open(file_path, "w") as f:
        json.dump(json_data, f, indent=4)
    assert os.path.exists(file_path)

    with open(file_path, "r") as f:
        loaded_data = json.load(f)
    assert len(loaded_data) == num_entries

    for i, book in enumerate(loaded_data):
        print(f'\nbook {i + 1}: \n name: {book["Title"]} \n location: {file_path} \n')
