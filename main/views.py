# # views.py
#
# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login
# from main.serializers import FoodPostSerializer, RegisterSerializer
# from .models import Member, FoodPost
# from .forms import MemberForm, FoodPostForm
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from django.http import JsonResponse
# from rest_framework import generics
#
# # Home Page
# def home(request):
#     return render(request, 'home.html')
#     # return render(request, 'index.html')
#
# # Register View
# @api_view(['GET', 'POST'])
# def register(request):
#     if request.method == 'GET':
#         # If it's a GET request, we could return a registration form (for a front-end interface).
#         return Response({"message": "Register page"})
#
#     elif request.method == 'POST':
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# # Food Feed View
# @api_view(['GET'])
# def food_feed(request):
#     if request.method == 'GET':
#         # Get all food posts from the database
#         food_posts = FoodPost.objects.all()
#         # Serialize the food posts
#         serializer = FoodPostSerializer(food_posts, many=True)
#         # Return the serialized data as JSON
#         return Response(serializer.data)
#
#     elif request.method == 'POST':
#         # Create a new food post
#         serializer = FoodPostSerializer(data=request.data)
#         if serializer.is_valid():
#             # Save the new food post and return it
#             serializer.save()
#             return Response(serializer.data, status=201)  # 201 Created status
#         return Response(serializer.errors, status=400)
#
# # Post Food View
# @api_view(['GET', 'POST'])
# def post_food_page(request):
#     if request.method == 'GET':
#         # Get all food posts
#         food_posts = FoodPost.objects.all()
#         serializer = FoodPostSerializer(food_posts, many=True)
#         return Response(serializer.data)
#
#     elif request.method == 'POST':
#         # Handle the creation of a new food post
#         serializer = FoodPostSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)
# # Login View (Add actual authentication logic)
#
# @api_view(['GET', 'POST'])
# def login(request):
#     if request.method == 'GET':
#         # Return a login form or message (adjust as necessary)
#         return Response({"message": "Login page"})
#
#     elif request.method == 'POST':
#         username = request.data.get('username')
#         password = request.data.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return Response({"message": "Logged in successfully"})
#         return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
#
#
# class FoodPostDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = FoodPost.objects.all()
#     serializer_class = FoodPostSerializer
#
# def index(request):
#     # Ensure the path to your build folder is correct
#     return render(request, 'index.html')
#     # return render(request, 'index.html')
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer, FoodPostSerializer, FoodRequestSerializer
from .models import FoodPost, FoodRequest, User
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_stats(request):
    users = request.user.__class__.objects.annotate(
        posts_count=Count('posts', distinct=True),
        requests_count=Count('foodrequest', distinct=True)
    ).values(
        'id', 'email', 'firstname', 'lastname',
        'is_active', 'is_staff', 'posts_count', 'requests_count'
    )
    return Response(list(users))

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(email=email, password=password)

    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def food_feed(request):
    posts = FoodPost.objects.all().order_by('-expiration_date')
    serializer = FoodPostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def post_food(request):
    serializer = FoodPostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(posted_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FoodPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FoodPost.objects.all()
    serializer_class = FoodPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if serializer.instance.posted_by == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied()

    def perform_destroy(self, instance):
        if instance.posted_by == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied()


class FoodRequestListCreateView(generics.ListCreateAPIView):
    queryset = FoodRequest.objects.all()
    serializer_class = FoodRequestSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Allow get request without authentication
    permission_classes = [permissions.IsAuthenticated]  # Allow get request without authentication

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)


class FoodRequestRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FoodRequest.objects.all()
    serializer_class = FoodRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if serializer.instance.requested_by == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied("You do not have permission to update this request.")

    def perform_destroy(self, instance):
        if instance.requested_by == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied("You do not have permission to delete this request.")
