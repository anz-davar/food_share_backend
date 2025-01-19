# # urls.py
#
# from django.urls import path
# from . import views
# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib import admin
# from .views import FoodPostDetailView
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', views.home, name='home'),
#     path('register/', views.register, name='register'),
#     path('login-page/', views.login, name='login'),
#     path('food-post/', views.post_food_page, name='post_food_page'),
#     path('food-feed/', views.food_feed, name='food_feed'),
#     # Corrected path for FoodPostDetailView
#     path('api/food_feed/<int:pk>/', FoodPostDetailView.as_view(), name='food_post_detail'),
#     path('', views.index, name='index'),
# ]
#
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', views.register, name='register'),
    path('api/login/', views.login, name='login'),
    path('api/food-feed/', views.food_feed, name='food_feed'),
    path('api/post-food/', views.post_food, name='post_food'),
    path('api/food-posts/<int:pk>/', views.FoodPostDetailView.as_view(), name='food_post_detail'),
    path('api/food-requests/', views.FoodRequestListCreateView.as_view(), name='food-request-list-create'),
    path('api/food-requests/<int:pk>/', views.FoodRequestRetrieveUpdateDestroyView.as_view(), name='food-request-retrieve-update-destroy'),
    path('api/admin/user-stats/', views.user_stats, name='user_stats'),

]
