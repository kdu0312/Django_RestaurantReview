from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from restaurants.models import Restaurant


# ---------- Model Tests ----------
class RestaurantModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.restaurant_info = {
            "name": "Test Restaurant",
            "description": "Test Description",
            "address": "Test Address",
            "contact": "Test Contact",
            "open_time": "10:00:00",
            "close_time": "22:00:00",
            "last_order": "21:00:00",
            "regular_holiday": "MON",
        }

    def test_create_restaurant(self):
        restaurant = Restaurant.objects.create(**self.restaurant_info)

        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(restaurant.name, self.restaurant_info["name"])
        self.assertEqual(restaurant.description, self.restaurant_info["description"])
        self.assertEqual(restaurant.address, self.restaurant_info["address"])
        self.assertEqual(restaurant.contact, self.restaurant_info["contact"])
        # TimeField는 time 객체이므로 문자열 비교 시 str()로
        self.assertEqual(str(restaurant.open_time), self.restaurant_info["open_time"])
        self.assertEqual(str(restaurant.close_time), self.restaurant_info["close_time"])
        self.assertEqual(str(restaurant.last_order), self.restaurant_info["last_order"])
        self.assertEqual(restaurant.regular_holiday, self.restaurant_info["regular_holiday"])
        # __str__ 확인 (restaurant.str() 아님에 주의)
        self.assertEqual(str(restaurant), self.restaurant_info["name"])


# ---------- API Tests ----------
class RestaurantViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.restaurant_info = {
            "name": "Test Restaurant",
            "description": "Test Description",
            "address": "Test Address",
            "contact": "Test Contact",
            "open_time": "10:00:00",
            "close_time": "22:00:00",
            "last_order": "21:00:00",
            "regular_holiday": "MON",
        }
        cls.user = get_user_model().objects.create_user(
            email="test@example.com", password="password1234"
        )

    def setUp(self):
        # Session/JWT 어떤 인증이든 통과시키기 위해 강제 인증
        # (self.client.login(email=...)는 커스텀 USERNAME_FIELD/백엔드 설정에 따라 실패 가능)
        self.client.force_authenticate(user=self.user)

    def test_restaurant_list_view(self):
        url = reverse("restaurant-list")  # DRF DefaultRouter 기준
        Restaurant.objects.create(**self.restaurant_info)

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # PageNumberPagination 사용 시 results 키 존재
        self.assertIn("results", res.data)
        self.assertEqual(len(res.data["results"]), 1)

        item = res.data["results"][0]
        self.assertEqual(item["name"], self.restaurant_info["name"])
        self.assertEqual(item["description"], self.restaurant_info["description"])
        self.assertEqual(item["address"], self.restaurant_info["address"])
        self.assertEqual(item["contact"], self.restaurant_info["contact"])
        self.assertEqual(item["open_time"], self.restaurant_info["open_time"])
        self.assertEqual(item["close_time"], self.restaurant_info["close_time"])
        self.assertEqual(item["last_order"], self.restaurant_info["last_order"])
        self.assertEqual(item["regular_holiday"], self.restaurant_info["regular_holiday"])

    def test_restaurant_post_view(self):
        url = reverse("restaurant-list")
        res = self.client.post(url, self.restaurant_info, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(Restaurant.objects.first().name, self.restaurant_info["name"])

    def test_restaurant_detail_view(self):
        restaurant = Restaurant.objects.create(**self.restaurant_info)
        url = reverse("restaurant-detail", kwargs={"pk": restaurant.id})

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], self.restaurant_info["name"])

    def test_restaurant_update_view_put(self):
        restaurant = Restaurant.objects.create(**self.restaurant_info)
        url = reverse("restaurant-detail", kwargs={"pk": restaurant.id})
        updated = {
            "name": "Updated Restaurant",
            "description": "Updated Description",
            "address": "Updated Address",
            "contact": "Updated Contact",
            "open_time": "11:00:00",
            "close_time": "23:00:00",
            "last_order": "22:00:00",
            "regular_holiday": "TUE",
        }

        res = self.client.put(url, updated, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(res.data["name"], updated["name"])
        self.assertEqual(res.data["description"], updated["description"])
        self.assertEqual(res.data["address"], updated["address"])
        self.assertEqual(res.data["contact"], updated["contact"])
        self.assertEqual(res.data["open_time"], updated["open_time"])
        self.assertEqual(res.data["close_time"], updated["close_time"])
        self.assertEqual(res.data["last_order"], updated["last_order"])
        self.assertEqual(res.data["regular_holiday"], updated["regular_holiday"])

    def test_restaurant_partial_update_view_patch(self):
        restaurant = Restaurant.objects.create(**self.restaurant_info)
        url = reverse("restaurant-detail", kwargs={"pk": restaurant.id})
        patch_data = {"name": "Patched Name"}

        res = self.client.patch(url, patch_data, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        restaurant.refresh_from_db()
        self.assertEqual(restaurant.name, "Patched Name")

    def test_restaurant_delete_view(self):
        restaurant = Restaurant.objects.create(**self.restaurant_info)
        url = reverse("restaurant-detail", kwargs={"pk": restaurant.id})

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Restaurant.objects.count(), 0)

    def test_unauthenticated_post_is_rejected(self):
        # 인증 해제
        self.client.force_authenticate(user=None)
        url = reverse("restaurant-list")

        res = self.client.post(url, self.restaurant_info, format="json")

        # IsAuthenticatedOrReadOnly 기준: 비인증 POST → 401 Unauthorized
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
