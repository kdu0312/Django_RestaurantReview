# users/tests.py
import unittest
from tempfile import TemporaryDirectory

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.test import TestCase, override_settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

TEST_MEDIA_DIR = TemporaryDirectory()


@override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
    MEDIA_ROOT=TEST_MEDIA_DIR.name,
)
class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = {
            "email": "test@example.com",
            "nickname": "testuser",
            "password": "password1234",
        }
        cls.test_admin_user = {
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
        # 스토리지 의존성 줄이기: url 대신 파일 name 비교
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


@override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
    MEDIA_ROOT=TEST_MEDIA_DIR.name,
)
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
        # 응답에 비밀번호 노출 금지
        self.assertNotIn("password", resp.data)

    def test_signup_duplicate_email_rejected(self):
        self.client.post(reverse("user-signup"), self.data, format="json")
        resp = self.client.post(reverse("user-signup"), self.data, format="json")
        self.assertIn(resp.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT))

    def test_user_login(self):
        user = User.objects.create_user(**self.data)
        payload = {"email": user.email, "password": "testpassword1234"}

        resp = self.client.post(reverse("user-login"), payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("message", resp.data)
        self.assertEqual(resp.data.get("message"), "login successful.")
        self.assertNotIn("password", resp.data)

    def test_user_login_invalid_credentials(self):
        payload = {"email": "test@example.com", "password": "wrongpassword"}
        resp = self.client.post(reverse("user-login"), payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_details_requires_auth(self):
        user = User.objects.create_user(**self.data)
        # 인증 없이 접근
        resp = self.client.get(reverse("user-detail", kwargs={"pk": user.id}))
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_get_user_details(self):
        user = User.objects.create_user(**self.data)
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

        # 삭제 후 재조회 시 404
        resp2 = self.client.get(reverse("user-detail", kwargs={"pk": user.id}))
        self.assertEqual(resp2.status_code, status.HTTP_404_NOT_FOUND)

    def test_jwt_login_obtain_pair(self):
        user = User.objects.create_user(**self.data)
        payload = {"email": user.email, "password": self.data["password"]}

        # 과제 라우트 네임에 맞게 사용 (커스텀 obtain)
        resp = self.client.post(reverse("jwt-login"), payload, format="json")

        # last_login 갱신 확인을 위해 새로고침
        before = user.last_login
        user.refresh_from_db()

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)
        self.assertNotEqual(user.last_login, before)

    def test_jwt_verify(self):
        user = User.objects.create_user(**self.data)
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        resp = self.client.post(reverse("token-verify"), {"token": access}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_jwt_refresh(self):
        user = User.objects.create_user(**self.data)
        refresh = RefreshToken.for_user(user)

        resp = self.client.post(reverse("token-refresh"), {"refresh": str(refresh)}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)

    @unittest.skipUnless(
        apps.is_installed("rest_framework_simplejwt.token_blacklist"),
        "token_blacklist app not installed",
    )
    def test_jwt_logout_blacklist(self):
        """
        블랙리스트 기반 로그아웃 테스트 (엔드포인트가 구현되어 있어야 함)
        """
        user = User.objects.create_user(**self.data)
        refresh = RefreshToken.for_user(user)

        # 커스텀 로그아웃 엔드포인트 (프로젝트 라우트 네임에 맞춰 변경)
        resp = self.client.post(reverse("jwt-logout"), {"refresh": str(refresh)}, format="json")
        self.assertIn(resp.status_code, (status.HTTP_200_OK, status.HTTP_205_RESET_CONTENT, status.HTTP_204_NO_CONTENT))