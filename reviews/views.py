from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    BasePermission,
    SAFE_METHODS,
)

from restaurants.models import Restaurant
from reviews.models import Review
from reviews.serializers import ReviewSerializer, ReviewDetailSerializer


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id


class ReviewListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return (
            Review.objects.select_related("user", "restaurant")
            .filter(restaurant_id=self.kwargs["restaurant_id"])
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs["restaurant_id"])
        serializer.save(user=self.request.user, restaurant=restaurant)


class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = ReviewDetailSerializer
    lookup_url_kwarg = "review_id"

    def get_queryset(self):
        return Review.objects.select_related("user", "restaurant").all()
