from django.test import TestCase
from rest_framework.test import APITestCase
from restaurants.models import Restaurant
from django.urls import reverse


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
        self.assertEqual(restaurant.open_time, self.restaurant_info["open_time"])
        self.assertEqual(restaurant.close_time, self.restaurant_info["close_time"])
        self.assertEqual(restaurant.last_order, self.restaurant_info["last_order"])
        self.assertEqual(
            restaurant.regular_holiday, self.restaurant_info["regular_holiday"]
        )
        self.assertEqual(restaurant.__str__(), self.restaurant_info["name"])


# restaurants/tests.py

...


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

    def test_restaurant_list_view(self):
        url = reverse("restaurant-list")
        Restaurant.objects.create(**self.restaurant_info)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get("results")), 1)
        self.assertEqual(
            response.data.get("results")[0].get("name"), self.restaurant_info["name"]
        )
        self.assertEqual(
            response.data.get("results")[0].get("description"),
            self.restaurant_info["description"],
        )
        self.assertEqual(
            response.data.get("results")[0].get("address"),
            self.restaurant_info["address"],
        )
        self.assertEqual(
            response.data.get("results")[0].get("contact"),
            self.restaurant_info["contact"],
        )
        self.assertEqual(
            response.data.get("results")[0].get("open_time"),
            self.restaurant_info["open_time"],
        )
        self.assertEqual(
            response.data.get("results")[0].get("close_time"),
            self.restaurant_info["close_time"],
        )
        self.assertEqual(
            response.data.get("results")[0].get("last_order"),
            self.restaurant_info["last_order"],
        )
        self.assertEqual(
            response.data.get("results")[0].get("regular_holiday"),
            self.restaurant_info["regular_holiday"],
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
        self.assertEqual(response.data.get("name"), self.restaurant_info["name"])

    def test_restaurant_update_view(self):
        restaurant = Restaurant.objects.create(**self.restaurant_info)
        url = reverse("restaurant-detail", kwargs={"pk": restaurant.id})
        updated_restaurant_info = {
            "name": "Updated Restaurant",
            "description": "Updated Description",
            "address": "Updated Address",
            "contact": "Updated Contact",
            "open_time": "11:00:00",
            "close_time": "23:00:00",
            "last_order": "22:00:00",
            "regular_holiday": "TUE",
        }

        response = self.client.put(url, updated_restaurant_info, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(response.data.get("name"), updated_restaurant_info["name"])
        self.assertEqual(
            response.data.get("description"), updated_restaurant_info["description"]
        )
        self.assertEqual(
            response.data.get("address"), updated_restaurant_info["address"]
        )
        self.assertEqual(
            response.data.get("contact"), updated_restaurant_info["contact"]
        )
        self.assertEqual(
            response.data.get("open_time"), updated_restaurant_info["open_time"]
        )
        self.assertEqual(
            response.data.get("close_time"), updated_restaurant_info["close_time"]
        )
        self.assertEqual(
            response.data.get("last_order"), updated_restaurant_info["last_order"]
        )
        self.assertEqual(
            response.data.get("regular_holiday"),
            updated_restaurant_info["regular_holiday"],
        )

    def test_restaurant_delete_view(self):
        restaurant = Restaurant.objects.create(**self.restaurant_info)
        url = reverse("restaurant-detail", kwargs={"pk": restaurant.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Restaurant.objects.count(), 0)
