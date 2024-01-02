import unittest
import requests
from app import app, db, User, Book

class TestFlaskAPI(unittest.TestCase):
    base_url = 'http://127.0.0.1:5000'  # Replace with the base URL of your running Flask app
    test_db_uri = 'postgresql://postgres:password@localhost:5433/test_db'  # Replace with your test database URI

    # Set up and tear down the tests
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = cls.test_db_uri
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()

    # Test the '/auth/login' endpoint
    def test_login(self):
        url = self.base_url + '/auth/login'
        data = {'username': 'test_user', 'password': 'test_password'}
        response = requests.post(url, json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json())

    # Test the '/users' endpoint
    def test_create_user(self):
        url = self.base_url + '/users'
        data = {
            'author_pseudonym': 'Test Author',
            'username': 'testuser',
            'password': 'test123'
        }
        response = requests.post(url, json=data)
        self.assertEqual(response.status_code, 201)

        user = User.query.filter_by(username=data['username']).first()
        self.assertIsNotNone(user)

    # Test other endpoints similarly (get_user, create_book, list_books, get_book, search_books, update_book, delete_book)

if __name__ == '__main__':
    unittest.main()
