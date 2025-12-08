from django.urls import path
from . import views

urlpatterns = [
    path('school', views.school, name='school'),
    path('readmore/', views.readmore, name='readmore'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('instructor/', views.instructor_view, name='instructor'),
    path('classes/', views.class_view, name='classes'),
    path('certificate/', views.certificate_view, name='certificate'),
    path('books/', views.books_view, name='books'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('learning-center/', views.learning_center_view, name='learning_center'),
    # API endpoints
    path('api/session/', views.api_session_info, name='api_session'),
    path('api/login/', views.api_login, name='api_login'),
]

