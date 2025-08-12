from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission, SAFE_METHODS

from restaurants.models import Restaurant
from reviews.models import Review
from reviews.serializers import ReviewSerializer, ReviewDetailSerializer


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # GET/HEAD/OPTIONS는 모두 허용
        if request.method in SAFE_METHODS:
            return True
        # 수정/삭제는 작성자만
        return obj.user_id == getattr(request.user, "id", None)


class ReviewListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        # 유효하지 않은 restaurant_id이면 404
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs["restaurant_id"])
        return (
            Review.objects.select_related("user", "restaurant")
            .filter(restaurant=restaurant)
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs["restaurant_id"])
        # user/restaurant는 클라이언트가 바꾸지 못하도록 read_only + 서버 주입
        serializer.save(user=self.request.user, restaurant=restaurant)


class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = ReviewDetailSerializer
    lookup_url_kwarg = "review_id"   # reverse('review-detail', kwargs={'review_id': ...})와 일치

    def get_queryset(self):
        # 객체 권한 체크가 동작하도록 전체 쿼리셋 반환(객체 단에서 IsOwnerOrReadOnly가 403 처리)
        return Review.objects.select_related("user", "restaurant").all()