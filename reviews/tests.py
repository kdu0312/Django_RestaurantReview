from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from restaurants.models import Restaurant
from reviews.models import Review


class ReviewModelTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            nickname="testuser", email="test@example.com", password="password1234"
        )
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            description="Test Description",
            address="123 Test St",
            contact="Phone: 010-0000-0000",
        )
        self.data = {
            "user": self.user,
            "restaurant": self.restaurant,
            "title": "Test Review Title",
            "comment": "Tasty Yammy Yammy~",
        }

    def test_create_review_model(self):
        review = Review.objects.create(**self.data)
        self.assertEqual(review.title, self.data["title"])
        self.assertEqual(review.comment, self.data["comment"])
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.restaurant, self.restaurant)


class ReviewAPIViewTestCase(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            nickname="testuser", email="test@example.com", password="password1234"
        )
        self.other = User.objects.create_user(
            nickname="other", email="other@example.com", password="password1234"
        )
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            description="Test Description",
            address="123 Test St",
            contact="Phone: 010-0000-0000",
        )
        # API 권한 필요 → 세션 로그인 대신 force_authenticate가 가장 안정적
        self.client.force_authenticate(user=self.user)

        # 기본 페이로드(POST/PATCH 용)
        self.payload = {
            "title": "Test Review Title",
            "comment": "Tasty Yammy Yammy~",
        }

    def test_get_review_list(self):
        Review.objects.create(
            user=self.user, restaurant=self.restaurant, title="A", comment="B"
        )
        # 레스토랑별 리뷰 목록 (중첩 경로 가정)
        url = reverse("review-list", kwargs={"restaurant_id": self.restaurant.id})

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("results", res.data)
        self.assertEqual(len(res.data["results"]), 1)
        item = res.data["results"][0]
        # 응답 스키마를 일관되게: user는 객체, restaurant는 PK 로 가정
        self.assertEqual(item["title"], "A")
        self.assertEqual(item["comment"], "B")
        self.assertEqual(item["restaurant"], self.restaurant.id)
        self.assertIsInstance(item["user"], dict)
        self.assertEqual(item["user"]["id"], self.user.id)

    def test_post_review(self):
        url = reverse("review-list", kwargs={"restaurant_id": self.restaurant.id})
        # POST는 바디에 title/comment만, user는 인증에서, restaurant는 URL에서
        res = self.client.post(url, self.payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        created = Review.objects.first()
        self.assertEqual(created.user_id, self.user.id)
        self.assertEqual(created.restaurant_id, self.restaurant.id)
        self.assertEqual(created.title, self.payload["title"])
        self.assertEqual(created.comment, self.payload["comment"])
        # 응답 본문 검증(스키마 일관)
        self.assertEqual(res.data["restaurant"], self.restaurant.id)
        self.assertEqual(res.data["user"]["id"], self.user.id)

    def test_get_review_detail(self):
        review = Review.objects.create(
            user=self.user, restaurant=self.restaurant, title="A", comment="B"
        )
        url = reverse("review-detail", kwargs={"review_id": review.id})

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "A")
        self.assertEqual(res.data["comment"], "B")
        # 상세도 리스트와 동일한 스키마 유지(불일치 방지)
        self.assertEqual(res.data["restaurant"], self.restaurant.id)
        self.assertEqual(res.data["user"]["id"], self.user.id)

    def test_update_review(self):
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

    def test_delete_review(self):
        review = Review.objects.create(
            user=self.user, restaurant=self.restaurant, title="A", comment="B"
        )
        url = reverse("review-detail", kwargs={"review_id": review.id})

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=review.id).exists())
