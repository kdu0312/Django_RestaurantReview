from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, min_length=8, trim_whitespace=False
    )
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ["id", "nickname", "email", "password", "is_staff", "is_superuser"]
        read_only_fields = ["id", "is_staff", "is_superuser"]
        extra_kwargs = {
            "nickname": {"required": True},
            "email": {"required": True},
        }

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "Password is required."})
        # 표준 매니저 로직 사용 (비번 해시 포함)
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=False, min_length=8, trim_whitespace=False
    )
    email = serializers.EmailField(read_only=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ["id", "nickname", "email", "password", "profile_image"]
        read_only_fields = ["id", "email"]

    def update(self, instance, validated_data):
        nickname = validated_data.get("nickname")
        if nickname is not None:
            instance.nickname = nickname

        password = validated_data.get("password")
        if password:
            instance.set_password(password)

        if "profile_image" in validated_data:
            instance.profile_image = validated_data.get("profile_image")

        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError(
                {"detail": 'Both "email" and "password" are required.'}
            )

        # AUTH_USER_MODEL의 USERNAME_FIELD가 'email'이어야 동작.
        # 아니라면 authenticate(username=email, password=...)로 바꾸거나 커스텀 백엔드 설정 필요.
        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )

        if not user:
            raise AuthenticationFailed(
                detail="Unable to log in with provided credentials.",
                code="authorization",
            )

        if not getattr(user, "is_active", True):
            raise AuthenticationFailed(
                detail="User account is disabled.", code="authorization"
            )

        attrs["user"] = user
        return attrs
