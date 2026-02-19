# views.py
import random
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from rest_framework.permissions import IsAuthenticated



def generate_otp():
    return str(random.randint(100000, 999999))


class LoginRegisterView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        username = request.data.get("username", "")

        if not phone:
            return Response(
                {"error": "Phone is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={"username": username}
        )

        otp = generate_otp()

        # ✅ Store OTP in cache (5 minutes)
        cache.set(f"otp_{phone}", otp, timeout=300)

        return Response({
            "message": "OTP generated",
            "otp": otp,  # ⚠️ show only for testing
            "phone": phone
        }, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        otp = request.data.get("otp")

        if not phone or not otp:
            return Response(
                {"error": "Phone and OTP required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cached_otp = cache.get(f"otp_{phone}")

        if not cached_otp:
            return Response(
                {"error": "OTP expired or not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if cached_otp != otp:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ OTP verified → delete from cache
        cache.delete(f"otp_{phone}")

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }, status=status.HTTP_200_OK)


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.query_params.get("search", "")

        users = User.objects.exclude(id=request.user.id)

        # ✅ If search is provided → filter by username
        if search:
            users = users.filter(username__icontains=search)

        return Response([
            {
                "id": str(u.id),
                "username": u.username
            }
            for u in users
        ])
