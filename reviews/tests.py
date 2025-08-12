from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from restaurants.models import Restaurant
from reviews.models import Review


# ---------- Model Tests ----------
class ReviewModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            nickname="testuser", email="test@example.com", password="password1234"
        )
        cls.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            description="Test Description",
            address="123 Test St",
            contact="Phone: 010-0000-0000",
        )
        cls.data = {
            "user": cls.user,
            "restaurant": cls.restaurant,
            "title": "Test Review Title",
            "comment": "Tasty Yammy Yammy~",
        }

    def test_create_review_model(self):
        review = Review.objects.create(**self.data)
        self.assertEqual(review.title, self.data["title"])
        self.assertEqual(review.comment, self.data["comment"])
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.restaurant, self.restaurant)


# ---------- API Tests ----------
class ReviewAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(
            nickname="testuser", email="test@example.com", password="password1234"
        )
        cls.other = User.objects.create_user(
            nickname="other", email="other@example.com", password="password1234"
        )
        cls.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            description="Test Description",
            address="123 Test St",
            contact="Phone: 010-0000-0000",
        )

    def setUp(self):
        # 모든 테스트 기본은 user 인증 상태
        self.client.force_authenticate(user=self.user)
        self.payload = {
            "title": "Test Review Title",
            "comment": "Tasty Yammy Yammy~",
        }

    def test_get_review_list(self):
        Review.objects.create(
            user=self.user, restaurant=self.restaurant, title="A", comment="B"
        )
        url = reverse("review-list", kwargs={"restaurant_id": self.restaurant.id})

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("results", res.data)
        self.assertEqual(len(res.data["results"]), 1)
        item = res.data["results"][0]
        # 스키마: restaurant는 PK, user는 객체(예: {id, nickname, ...})
        self.assertEqual(item["title"], "A")
        self.assertEqual(item["comment"], "B")
        self.assertEqual(item["restaurant"], self.restaurant.id)
        self.assertIsInstance(item["user"], dict)
        self.assertEqual(item["user"]["id"], self.user.id)

    def test_post_review(self):
        url = reverse("review-list", kwargs={"restaurant_id": self.restaurant.id})
        # 바디에는 title, comment만 보냄
        res = self.client.post(url, self.payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        created = Review.objects.first()
        self.assertEqual(created.user_id, self.user.id)
        self.assertEqual(created.restaurant_id, self.restaurant.id)
        self.assertEqual(created.title, self.payload["title"])
        self.assertEqual(created.comment, self.payload["comment"])
        # 응답 본문
        self.assertEqual(res.data["restaurant"], self.restaurant.id)
        self.assertEqual(res.data["user"]["id"], self.user.id)

    def test_post_review_unauthenticated_rejected(self):
        self.client.force_authenticate(user=None)
        url = reverse("review-list", kwargs={"restaurant_id": self.restaurant.id})

        res = self.client.post(url, self.payload, format="json")

        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_post_review_validation_error(self):
        url = reverse("review-list", kwargs={"restaurant_id": self.restaurant.id})
        bad = {"title": "", "comment": ""}

        res = self.client.post(url, bad, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertGreaterEqual(len(res.data.keys()), 1)  # 어떤 필드든 에러가 있어야 함

    def test_get_review_detail(self):
        review = Review.objects.create(
            user=self.user, restaurant=self.restaurant, title="A", comment="B"
        )
        url = reverse("review-detail", kwargs={"review_id": review.id})

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "A")
        self.assertEqual(res.data["comment"], "B")
        self.assertEqual(res.data["restaurant"], self.restaurant.id)
        self.assertEqual(res.data["user"]["id"], self.user.id)

    def test_get_review_detail_404(self):
        url = reverse("review-detail", kwargs={"review_id": 999999})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_review_by_owner(self):
        review = Review.objects.create(
            user=self.user, restaurant=self.restaurant, title="A", comment="B"
        )
        url = reverse("review-detail", kwargs={"review_id": review.id})
        updated = {"title": "Updated", "comment": "Updated~~~"}

        res = self.client.patch(url, updated, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.title, "Updated")
        self.assertEqual(review.comment, "Updated~~~")

    def test_update_review_forbidden_for_other_user(self):
        review = Review.objects.create(
            user=self.other, restaurant=self.restaurant, title="A", comment="B"
        )
        url = reverse("review-detail", kwargs={"review_id": review.id})
        updated = {"title": "Updated", "comment": "Updated~~~"}

        res = self.client.patch(url, updated, format="json")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_by_owner(self):
        review = Review.objects.create(
            user=self.user, restaurant=self.restaurant, title="A", comment="B"
        )
        url = reverse("review-detail", kwargs={"review_id": review.id})

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_delete_review_forbidden_for_other_user(self):
        review = Review.objects.create(
            user=self.other, restaurant=self.restaurant, title="A", comment="B"
        )
        url = reverse("review-detail", kwargs={"review_id": review.id})

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_for_invalid_restaurant_returns_404(self):
        url = reverse("review-list", kwargs={"restaurant_id": 999999})
        res = self.client.get(url)
        # 구현에 따라 빈 리스트(200)로 할 수도 있으나, 이번 과제 컨벤션은 404 가정
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)