from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    # 입력 시에만 받도록 write_only
    password = serializers.CharField(
        write_only=True, min_length=8, trim_whitespace=False
    )
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ["id", "nickname", "email", "password", "is_staff", "is_superuser"]
        read_only_fields = ["id", "is_staff", "is_superuser"]  # 권한 상승 차단
        extra_kwargs = {
            "nickname": {"required": True},
            "email": {"required": True},
        }

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "Password is required."})
        # create_user에 password를 넘겨 백엔드 표준 로직 사용
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    # 부분 업데이트(PATCH)에서만 전달되도록 required=False
    password = serializers.CharField(
        write_only=True, required=False, min_length=8, trim_whitespace=False
    )
    email = serializers.EmailField(
        read_only=True
    )  # 이메일은 수정 불가로 고정(요구 시 정책에 맞춰 조정)
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

        # 프로필 이미지가 들어오면 교체(없으면 유지)
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

        # 인증 백엔드가 이메일 기반으로 설정되어 있다는 가정하에 명시적으로 전달
        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )

        if not user:
            # 인증 실패 시 메시지를 통일
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
