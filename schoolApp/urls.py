from django.urls import path
from . import views

urlpatterns = [
    path('school', views.school, name='school'),
    path('about/', views.about_view, name='about'),
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
    path('course/<int:course_id>/', views.course_detail_view, name='course_detail'),
    # path('contacts/', views.contacts_view, name='contacts'),
    
    # Course and enrollment URLs
    # path('course/<int:course_id>/', views.course_detail_view, name='course_detail'),
    path('course/<int:course_id>/enroll/', views.enroll_course_view, name='enroll_course'),
    
    # Student dashboard
    path('student-dashboard/', views.student_dashboard_view, name='student_dashboard'),
    
    # Mentor dashboard
    path('mentor-dashboard/', views.mentor_dashboard_view, name='mentor_dashboard'),
    path('mentor/create-course/', views.mentor_create_course_view, name='mentor_create_course'),
    path('mentor/courses/', views.mentor_course_list_view, name='mentor_course_list'),
    path('mentor/student-progress/<int:enrollment_id>/', views.mentor_student_progress_view, name='mentor_student_progress'),
    
    # Messaging
    path('send-message/<int:enrollment_id>/', views.send_message_view, name='send_message'),
    
    # Newsletter
    path('newsletter/signup/', views.newsletter_signup, name='newsletter_signup'),
    path('newsletter/unsubscribe/<str:email>/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    
    # API endpoints
    path('api/session/', views.api_session_info, name='api_session'),
    path('api/login/', views.api_login, name='api_login'),
]

