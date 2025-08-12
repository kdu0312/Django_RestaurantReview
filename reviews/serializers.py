from rest_framework import serializers
from reviews.models import Review
from users.serializers import UserDetailSerializer


class ReviewSerializer(serializers.ModelSerializer):
    # 읽기 시: user는 객체, restaurant는 PK(int)로 노출
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Review
        fields = "__all__"
        # created_at, updated_at이 모델에 없으면 두 항목은 제거하세요.
        read_only_fields = ["id", "user", "restaurant", "created_at", "updated_at"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # 스키마 일관화: restaurant는 PK로 노출
        rep["restaurant"] = instance.restaurant_id
        return rep


class ReviewDetailSerializer(ReviewSerializer):
    # 상세도 리스트와 동일 스키마 유지
    pass
