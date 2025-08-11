from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.urls import reverse
from restaurants.models import Restaurant


class RestaurantModelTest(TestCase):
    def setUp(self):
        self.restaurant_info = {
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
        # TimeField는 time 객체이므로 문자열이 아닌 str()로 비교
        self.assertEqual(str(restaurant.open_time), self.restaurant_info["open_time"])
        self.assertEqual(str(restaurant.close_time), self.restaurant_info["close_time"])
        self.assertEqual(str(restaurant.last_order), self.restaurant_info["last_order"])
        self.assertEqual(
            restaurant.regular_holiday, self.restaurant_info["regular_holiday"]
        )
        self.assertEqual(str(restaurant), self.restaurant_info["name"])


class RestaurantViewTestCase(APITestCase):
    def setUp(self):
        self.restaurant_info = {
            "name": "Test Restaurant",
            "description": "Test Description",
            "address": "Test Address",
            "contact": "Test Contact",
            "open_time": "10:00:00",
            "close_time": "22:00:00",
            "last_order": "21:00:00",
            "regular_holiday": "MON",
        }
        # 인증 필요(POST/PUT/DELETE는 IsAuthenticated)
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="password1234"
        )
        # 이메일/커스텀 USERNAME_FIELD 문제 회피용
        self.client.force_authenticate(user=self.user)

    def test_restaurant_list_view(self):
        url = reverse("restaurant-list")
        Restaurant.objects.create(**self.restaurant_info)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # PageNumberPagination 기준
        self.assertEqual(len(response.data.get("results")), 1)
        item = response.data["results"][0]
        self.assertEqual(item["name"], self.restaurant_info["name"])
        self.assertEqual(item["description"], self.restaurant_info["description"])
        self.assertEqual(item["address"], self.restaurant_info["address"])
        self.assertEqual(item["contact"], self.restaurant_info["contact"])
        self.assertEqual(item["open_time"], self.restaurant_info["open_time"])
        self.assertEqual(item["close_time"], self.restaurant_info["close_time"])
        self.assertEqual(item["last_order"], self.restaurant_info["last_order"])
        self.assertEqual(
            item["regular_holiday"], self.restaurant_info["regular_holiday"]
        )

    def test_restaurant_post_view(self):
        url = reverse("restaurant-list")
        response = self.client.post(url, self.restaurant_info, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(Restaurant.objects.first().name, self.restaurant_info["name"])

    def test_restaurant_detail_view(self):
        restaurant = Restaurant.objects.create(**self.restaurant_info)
        url = reverse("restaurant-detail", kwargs={"pk": restaurant.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.restaurant_info["name"])

    def test_restaurant_update_view(self):
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

        response = self.client.put(url, updated, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(response.data["name"], updated["name"])
        self.assertEqual(response.data["description"], updated["description"])
        self.assertEqual(response.data["address"], updated["address"])
        self.assertEqual(response.data["contact"], updated["contact"])
        self.assertEqual(response.data["open_time"], updated["open_time"])
        self.assertEqual(response.data["close_time"], updated["close_time"])
        self.assertEqual(response.data["last_order"], updated["last_order"])
        self.assertEqual(response.data["regular_holiday"], updated["regular_holiday"])

    def test_restaurant_delete_view(self):
        restaurant = Restaurant.objects.create(**self.restaurant_info)
        url = reverse("restaurant-detail", kwargs={"pk": restaurant.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Restaurant.objects.count(), 0)
