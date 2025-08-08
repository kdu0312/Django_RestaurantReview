from restaurants import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"restaurants", views.RestaurantViewSet)
urlpatterns = router.urls
