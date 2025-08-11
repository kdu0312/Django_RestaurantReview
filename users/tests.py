from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.test_user = {
            "email": "test@example.com",
            "nickname": "testuser",
            "password": "password1234",
        }
        self.test_admin_user = {
            "email": "admin@example.com",
            "nickname": "adminuser",
            "password": "password1234",
        }

    def test_user_manager_create_user(self):
        user = User.objects.create_user(**self.test_user)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.email, self.test_user["email"])
        self.assertEqual(user.nickname, self.test_user["nickname"])
        self.assertTrue(user.check_password(self.test_user["password"]))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        # 스토리지/URL 의존성 줄이기: url 대신 name 비교
        self.assertEqual(user.profile_image.name, "users/blank_profile_image.png")

    def test_user_manager_create_superuser(self):
        admin_user = User.objects.create_superuser(**self.test_admin_user)

        self.assertEqual(
            User.objects.filter(is_superuser=True, is_staff=True).count(), 1
        )
        self.assertEqual(admin_user.email, self.test_admin_user["email"])
        self.assertEqual(admin_user.nickname, self.test_admin_user["nickname"])
        self.assertTrue(admin_user.check_password(self.test_admin_user["password"]))
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)
        self.assertEqual(admin_user.profile_image.name, "users/blank_profile_image.png")


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.data = {
            "nickname": "testuser",
            "email": "test@example.com",
            "password": "testpassword1234",
        }

    def test_user_signup(self):
        resp = self.client.post(reverse("user-signup"), self.data, format="json")

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(resp.data.get("nickname"), "testuser")
        self.assertEqual(resp.data.get("email"), "test@example.com")

    def test_user_login(self):
        user = User.objects.create_user(**self.data)
        payload = {"email": user.email, "password": "testpassword1234"}

        resp = self.client.post(reverse("user-login"), payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("message", resp.data)
        self.assertEqual(resp.data.get("message"), "login successful.")

    def test_user_login_invalid_credentials(self):
        payload = {"email": "test@example.com", "password": "wrongpassword"}
        resp = self.client.post(reverse("user-login"), payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_details(self):
        user = User.objects.create_user(**self.data)
        # API 테스트에서는 세션 로그인 대신 force_authenticate가 안전
        self.client.force_authenticate(user=user)

        resp = self.client.get(reverse("user-detail", kwargs={"pk": user.id}))

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get("nickname"), "testuser")
        self.assertEqual(resp.data.get("email"), "test@example.com")

    def test_update_user_details(self):
        user = User.objects.create_user(**self.data)
        self.client.force_authenticate(user=user)
        payload = {"nickname": "updateduser", "password": "updatepw1234"}

        resp = self.client.patch(
            reverse("user-detail", kwargs={"pk": user.id}), payload, format="json"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get("nickname"), "updateduser")
        user.refresh_from_db()
        self.assertTrue(check_password("updatepw1234", user.password))

    def test_delete_user(self):
        user = User.objects.create_user(**self.data)
        self.client.force_authenticate(user=user)

        resp = self.client.delete(reverse("user-detail", kwargs={"pk": user.id}))

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(email="test@example.com").exists())
