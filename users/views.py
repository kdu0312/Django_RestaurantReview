from django.shortcuts import get_object_or_404
from django.contrib.auth import login, get_user_model
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import logout

from users.serializers import (
    UserSerializer,  # 가입용 (create_user 사용)
    UserDetailSerializer,  # 조회/수정용 (email read_only, password optional)
    UserLoginSerializer,  # 로그인 검증
)

User = get_user_model()


class UserSignupView(CreateAPIView):
    """
    POST /users/signup/
    """

    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()  # 명시 (CreateAPIView 권장 패턴)


class UserLoginView(APIView):
    """
    POST /users/login/
    body: { "email": "...", "password": "..." }
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        login(request, user)
        return Response({"message": "login successful."}, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "logout successful."}, status=status.HTTP_200_OK)


class UserDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /users/me/
    - 본인 정보만 접근 가능
    """

    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        # 현재 로그인한 사용자만 자신의 정보를 조회/수정/삭제
        return get_object_or_404(User, id=self.request.user.id)
