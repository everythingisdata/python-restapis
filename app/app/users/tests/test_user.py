from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("users:create")
TOKEN_URL = reverse("users:token")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test Create users with valid payload is successful"""
        payload = {
            'email': 'test@everythingisdata.com',
            'password': 'test123',
            'name': 'Test  User',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        users = get_user_model().objects.get(**res.data)
        self.assertTrue(users.check_password(payload['password']))

        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test create user that already exist fail"""
        payload = {
            'email': 'testuserexist@everythingisdata.com',
            'password': 'testp',
            'name': 'testuserexist'
        }
        create_user(**payload)

        resp = self.client.post(CREATE_USER_URL, **payload)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_too_short(self):
        """Test that password must not be less the 5 character"""

        payload = {
            'email': 'testuserexist@everythingisdata.com',
            'password': 'tes',
            'name': 'testuserexist'
        }

        resp = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        user_exist = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """Test token is created for the user"""
        payload = {
            'email': 'testuserexist@everythingisdata.com',
            'password': 'tesytr',
            'name': 'testuserexist'
        }
        create_user(**payload)
        resp = self.client.post(TOKEN_URL, payload)
        print(resp.data)

        self.assertIn('token', resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test Token is not get created if invalid credentials provided. """
        create_user(email="bharat@test.com", password="testpass1231")
        payload = {'email': "bharat@test.com", "password": "wrong1231"}
        resp = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', resp.data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_if_no_user(self):
        """Test Token is not created if user is not present"""
        payload = {'email': 'test@email.com', 'password': "passswordqwe"}
        resp = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', resp.data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_fields(self):
        """Test email and password required for token"""
        payload = {'email': 'test', 'password': ""}
        resp = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', resp.data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
