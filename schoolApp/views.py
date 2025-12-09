from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import re
import json
from . import models

def school(request):
    return render(request, 'schoolApp/home.html')

def readmore(request):
    return render(request, 'schoolApp/readmore.html')

def instructor_view(request):
    return render(request, 'schoolApp/instructor.html')

def certificate_view(request):
    return render(request, 'schoolApp/certification.html')

def contacts_view(request):
    return render(request, 'schoolApp/contact.html')

def books_view(request):
    return render(request, 'schoolApp/books.html')

def class_view(request):
    courses = models.Course.objects.all()
    context = {
        'courses': courses
    }
    return render(request, 'schoolApp/class.html', context)


def is_user_logged_in(request):
    """Check if user is logged in and return user info"""
    if 'user_id' in request.session and 'user_role' in request.session:
        return True
    return False


def login_view(request):
    """Handle student or mentor login"""
    # If already logged in, redirect to learning center
    if is_user_logged_in(request):
        return redirect('learning_center')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        role = request.POST.get('role', '').lower()
        remember_me = request.POST.get('remember_me', False)
        
        # Validation
        if not all([email, password, role]):
            messages.error(request, 'Please fill in all fields')
            return render(request, 'schoolApp/login.html', {'role': role})
        
        if role not in ['student', 'mentor']:
            messages.error(request, 'Invalid role selected')
            return render(request, 'schoolApp/login.html')
        
        # Find user
        user = None
        if role == 'student':
            try:
                user = models.Student.objects.get(email=email)
            except models.Student.DoesNotExist:
                messages.error(request, 'Invalid email or password')
                return render(request, 'schoolApp/login.html', {'role': role})
        else:
            try:
                user = models.Mentor.objects.get(email=email)
            except models.Mentor.DoesNotExist:
                messages.error(request, 'Invalid email or password')
                return render(request, 'schoolApp/login.html', {'role': role})
        
        # Check password
        if not user.check_password(password):
            messages.error(request, 'Invalid email or password')
            return render(request, 'schoolApp/login.html', {'role': role})
        
        # Set session
        request.session['user_id'] = user.id
        request.session['user_name'] = f"{user.first_name} {user.last_name}"
        request.session['user_email'] = user.email
        request.session['user_role'] = role
        request.session['logged_in'] = True
        
        # Set session expiry to 1 week if "Remember me" is checked
        if remember_me:
            request.session.set_expiry(604800)  # 1 week in seconds
        else:
            request.session.set_expiry(None)  # Browser session
        
        # Save session
        request.session.save()
        
        messages.success(request, f'Welcome back, {user.first_name}!')
        return redirect('learning_center')
    
    # GET request - show login form
    role = request.GET.get('role', 'student')
    return render(request, 'schoolApp/login.html', {'role': role})


def register_view(request):
    """Handle student or mentor registration"""
    # If already logged in, redirect to learning center
    if is_user_logged_in(request):
        return redirect('learning_center')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', '').lower()
        expertise = request.POST.get('expertise', '').strip() if role == 'mentor' else None
        
        # Validation
        if not all([first_name, last_name, email, phone_number, password, confirm_password, role]):
            messages.error(request, 'Please fill in all required fields')
            return render(request, 'schoolApp/register.html', {'role': role})
        
        if role not in ['student', 'mentor']:
            messages.error(request, 'Invalid role selected')
            return render(request, 'schoolApp/register.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'schoolApp/register.html', {'role': role})
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long')
            return render(request, 'schoolApp/register.html', {'role': role})
        
        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            messages.error(request, 'Please enter a valid email address')
            return render(request, 'schoolApp/register.html', {'role': role})
        
        # Check if user already exists
        if role == 'student':
            if models.Student.objects.filter(email=email).exists():
                messages.error(request, 'A student with this email already exists')
                return render(request, 'schoolApp/register.html', {'role': role})
            
            user = models.Student(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number
            )
        else:
            if models.Mentor.objects.filter(email=email).exists():
                messages.error(request, 'A mentor with this email already exists')
                return render(request, 'schoolApp/register.html', {'role': role})
            
            user = models.Mentor(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                expertise=expertise
            )
        
        # Save user to database
        user.set_password(password)
        user.save()
        
        # Set session and redirect to learning center
        request.session['user_id'] = user.id
        request.session['user_name'] = f"{user.first_name} {user.last_name}"
        request.session['user_email'] = user.email
        request.session['user_role'] = role
        request.session['logged_in'] = True
        request.session.save()
        
        messages.success(request, 'Account created successfully! Welcome to EduForAll!')
        return redirect('learning_center')
    
    # GET request - show register form
    role = request.GET.get('role', 'student')
    return render(request, 'schoolApp/register.html', {'role': role})


def logout_view(request):
    """Handle logout"""
    request.session.flush()
    messages.success(request, 'You have been logged out successfully')
    return redirect('school')


def dashboard_view(request):
    """Show user dashboard after login"""
    if 'user_id' not in request.session:
        messages.warning(request, 'Please log in first')
        return redirect('/schoolApp/login/')
    
    user_role = request.session.get('user_role')
    user_id = request.session.get('user_id')
    
    try:
        if user_role == 'student':
            user = models.Student.objects.get(id=user_id)
        else:
            user = models.Mentor.objects.get(id=user_id)
    except (models.Student.DoesNotExist, models.Mentor.DoesNotExist):
        request.session.flush()
        messages.error(request, 'User not found. Please log in again')
        return redirect('/schoolApp/login/')
    
    context = {
        'user': user,
        'user_role': user_role
    }
    return render(request, 'schoolApp/dashboard.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def api_session_info(request):
    """API endpoint to get current session info (for AJAX calls if needed)"""
    if 'user_id' in request.session:
        return JsonResponse({
            'logged_in': True,
            'user_id': request.session.get('user_id'),
            'user_name': request.session.get('user_name'),
            'user_email': request.session.get('user_email'),
            'user_role': request.session.get('user_role')
        })
    return JsonResponse({'logged_in': False})


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """API endpoint for login (JSON)"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        password = data.get('password', '')
        role = data.get('role', '').lower()
        
        if not all([email, password, role]):
            return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)
        
        if role not in ['student', 'mentor']:
            return JsonResponse({'success': False, 'error': 'Invalid role'}, status=400)
        
        # Find user
        user = None
        if role == 'student':
            try:
                user = models.Student.objects.get(email=email)
            except models.Student.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
        else:
            try:
                user = models.Mentor.objects.get(email=email)
            except models.Mentor.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
        
        if not user.check_password(password):
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
        
        # Set session
        request.session['user_id'] = user.id
        request.session['user_name'] = f"{user.first_name} {user.last_name}"
        request.session['user_email'] = user.email
        request.session['user_role'] = role
        request.session['logged_in'] = True
        request.session.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Welcome back, {user.first_name}!',
            'user_name': f"{user.first_name} {user.last_name}"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def learning_center_view(request):
    """Learning center - accessible only to logged-in users"""
    if 'user_id' not in request.session:
        messages.warning(request, 'Please log in first')
        return redirect('/schoolApp/login/')
    
    user_role = request.session.get('user_role')
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    
    try:
        if user_role == 'student':
            user = models.Student.objects.get(id=user_id)
        else:
            user = models.Mentor.objects.get(id=user_id)
    except (models.Student.DoesNotExist, models.Mentor.DoesNotExist):
        request.session.flush()
        messages.error(request, 'User not found. Please log in again')
        return redirect('/schoolApp/login/')
    
    # Get all courses for display
    all_courses = models.Course.objects.all()
    
    context = {
        'user': user,
        'user_role': user_role,
        'user_name': user_name,
        'courses': all_courses,
    }
    return render(request, 'schoolApp/learning_center.html', context)


def course_detail_view(request, course_id):
    """Display course details with enrollment options"""
    try:
        course = models.Course.objects.get(id=course_id)
    except models.Course.DoesNotExist:
        messages.error(request, 'Course not found')
        return redirect('learning_center')
    
    user = None
    user_role = None
    is_enrolled = False
    enrollment = None
    
    if 'user_id' in request.session:
        user_role = request.session.get('user_role')
        user_id = request.session.get('user_id')
        
        if user_role == 'student':
            try:
                user = models.Student.objects.get(id=user_id)
                enrollment = models.StudentCourse.objects.filter(student=user, course=course).first()
                is_enrolled = enrollment is not None
            except models.Student.DoesNotExist:
                pass
    
    context = {
        'course': course,
        'user': user,
        'user_role': user_role,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
    }
    return render(request, 'schoolApp/course_detail.html', context)


def enroll_course_view(request, course_id):
    """Handle course enrollment"""
    if 'user_id' not in request.session or request.session.get('user_role') != 'student':
        messages.warning(request, 'Please log in as a student to enroll')
        return redirect('login')
    
    try:
        course = models.Course.objects.get(id=course_id)
        student = models.Student.objects.get(id=request.session.get('user_id'))
    except (models.Course.DoesNotExist, models.Student.DoesNotExist):
        messages.error(request, 'Course or student not found')
        return redirect('learning_center')
    
    # Check if already enrolled
    if models.StudentCourse.objects.filter(student=student, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course')
        return redirect('course_detail', course_id=course_id)
    
    if request.method == 'POST':
        enrollment_type = request.POST.get('enrollment_type', 'free')
        mentor_id = request.POST.get('mentor_id', None)
        
        if enrollment_type not in ['free', 'mentored']:
            messages.error(request, 'Invalid enrollment type')
            return redirect('course_detail', course_id=course_id)
        
        mentor = None
        if enrollment_type == 'mentored' and mentor_id:
            try:
                mentor = models.Mentor.objects.get(id=mentor_id)
            except models.Mentor.DoesNotExist:
                messages.error(request, 'Mentor not found')
                return redirect('course_detail', course_id=course_id)
        
        # Create enrollment
        enrollment = models.StudentCourse.objects.create(
            student=student,
            course=course,
            enrollment_type=enrollment_type,
            mentor=mentor,
            status='enrolled'
        )
        
        # Create learning path
        models.LearningPath.objects.create(
            student_course=enrollment,
            total_lessons=10  # Default value, can be updated
        )
        
        # Create notification for mentor if mentored
        if mentor:
            models.Notification.objects.create(
                mentor=mentor,
                notification_type='enrollment',
                title=f'New Student: {student.first_name} {student.last_name}',
                message=f'{student.first_name} {student.last_name} enrolled in {course.title} with mentoring',
                related_course=course
            )
        
        messages.success(request, f'Successfully enrolled in {course.title}!')
        return redirect('student_dashboard')
    
    # GET request - show enrollment options
    mentors = models.Mentor.objects.all()
    context = {
        'course': course,
        'mentors': mentors,
    }
    return render(request, 'schoolApp/enroll_course.html', context)


def student_dashboard_view(request):
    """Student-specific dashboard with learning journey"""
    if 'user_id' not in request.session or request.session.get('user_role') != 'student':
        messages.warning(request, 'Please log in as a student')
        return redirect('login')
    
    try:
        student = models.Student.objects.get(id=request.session.get('user_id'))
    except models.Student.DoesNotExist:
        request.session.flush()
        messages.error(request, 'Student not found')
        return redirect('login')
    
    # Get enrolled courses with progress
    enrollments = models.StudentCourse.objects.filter(student=student).select_related('course', 'mentor', 'learning_path')
    
    # Get available courses (courses not yet enrolled in)
    enrolled_course_ids = enrollments.values_list('course_id', flat=True)
    available_courses = models.Course.objects.exclude(id__in=enrolled_course_ids)
    
    # Calculate statistics
    total_courses = enrollments.count()
    completed_courses = enrollments.filter(status='completed').count()
    in_progress = enrollments.filter(status='in_progress').count()
    
    # Calculate overall progress
    total_progress = 0
    if enrollments.exists():
        total_progress = sum(e.progress for e in enrollments) / enrollments.count()
    
    context = {
        'student': student,
        'enrollments': enrollments,
        'available_courses': available_courses,
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'in_progress': in_progress,
        'average_progress': round(total_progress, 1),
    }
    return render(request, 'schoolApp/student_dashboard.html', context)


def mentor_dashboard_view(request):
    """Mentor-specific dashboard with course management and student tracking"""
    if 'user_id' not in request.session or request.session.get('user_role') != 'mentor':
        messages.warning(request, 'Please log in as a mentor')
        return redirect('login')
    
    try:
        mentor = models.Mentor.objects.get(id=request.session.get('user_id'))
    except models.Mentor.DoesNotExist:
        request.session.flush()
        messages.error(request, 'Mentor not found')
        return redirect('login')
    
    # Get courses taught by this mentor
    courses = models.Course.objects.filter(instructor__email=mentor.email)
    
    # Get mentored students
    mentored_students = models.StudentCourse.objects.filter(mentor=mentor).select_related('student', 'course')
    
    # Get unread messages
    unread_messages = models.Message.objects.filter(receiver_mentor=mentor, is_read=False)
    
    # Get notifications
    notifications = models.Notification.objects.filter(mentor=mentor, is_read=False)
    
    context = {
        'mentor': mentor,
        'courses': courses,
        'mentored_students': mentored_students,
        'unread_messages': unread_messages,
        'notifications': notifications,
        'total_students': mentored_students.count(),
    }
    return render(request, 'schoolApp/mentor_dashboard.html', context)


def mentor_create_course_view(request):
    """Mentor creates a new course"""
    if 'user_id' not in request.session or request.session.get('user_role') != 'mentor':
        messages.warning(request, 'Please log in as a mentor')
        return redirect('login')
    
    try:
        mentor = models.Mentor.objects.get(id=request.session.get('user_id'))
    except models.Mentor.DoesNotExist:
        request.session.flush()
        messages.error(request, 'Mentor not found')
        return redirect('login')
    
    # Get or create instructor for this mentor
    instructor, created = models.Instructor.objects.get_or_create(
        email=mentor.email,
        defaults={
            'first_name': mentor.first_name,
            'last_name': mentor.last_name,
            'phone_number': mentor.phone_number,
        }
    )
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        course_type = request.POST.get('course_type', 'both')
        price = request.POST.get('price', 0)
        duration_weeks = request.POST.get('duration_weeks', 4)
        
        if not all([title, description, start_date, end_date]):
            messages.error(request, 'Please fill in all required fields')
            return render(request, 'schoolApp/mentor_create_course.html')
        
        try:
            course = models.Course.objects.create(
                title=title,
                description=description,
                instructor=instructor,
                start_date=start_date,
                end_date=end_date,
                course_type=course_type,
                price=price if course_type != 'free' else 0,
                duration_weeks=duration_weeks,
            )
            messages.success(request, f'Course "{title}" created successfully!')
            return redirect('mentor_dashboard')
        except Exception as e:
            messages.error(request, f'Error creating course: {str(e)}')
            return render(request, 'schoolApp/mentor_create_course.html')
    
    context = {}
    return render(request, 'schoolApp/mentor_create_course.html', context)


def mentor_course_list_view(request):
    """List all courses created by mentor for management"""
    if 'user_id' not in request.session or request.session.get('user_role') != 'mentor':
        messages.warning(request, 'Please log in as a mentor')
        return redirect('login')
    
    try:
        mentor = models.Mentor.objects.get(id=request.session.get('user_id'))
    except models.Mentor.DoesNotExist:
        request.session.flush()
        messages.error(request, 'Mentor not found')
        return redirect('login')
    
    # Get courses taught by this mentor
    courses = models.Course.objects.filter(instructor__email=mentor.email)
    
    context = {
        'mentor': mentor,
        'courses': courses,
    }
    return render(request, 'schoolApp/mentor_course_list.html', context)


def mentor_student_progress_view(request, enrollment_id):
    """View and track a student's progress"""
    if 'user_id' not in request.session or request.session.get('user_role') != 'mentor':
        messages.warning(request, 'Please log in as a mentor')
        return redirect('login')
    
    try:
        mentor = models.Mentor.objects.get(id=request.session.get('user_id'))
        enrollment = models.StudentCourse.objects.get(id=enrollment_id, mentor=mentor)
    except (models.Mentor.DoesNotExist, models.StudentCourse.DoesNotExist):
        messages.error(request, 'Enrollment not found or access denied')
        return redirect('mentor_dashboard')
    
    learning_path = enrollment.learning_path if hasattr(enrollment, 'learning_path') else None
    
    context = {
        'mentor': mentor,
        'enrollment': enrollment,
        'learning_path': learning_path,
    }
    return render(request, 'schoolApp/mentor_student_progress.html', context)


def send_message_view(request, enrollment_id):
    """Send a message to a student (mentor) or mentor (student)"""
    if 'user_id' not in request.session:
        messages.warning(request, 'Please log in')
        return redirect('login')
    
    user_role = request.session.get('user_role')
    user_id = request.session.get('user_id')
    
    try:
        enrollment = models.StudentCourse.objects.get(id=enrollment_id)
    except models.StudentCourse.DoesNotExist:
        messages.error(request, 'Enrollment not found')
        return redirect('learning_center')
    
    if request.method == 'POST':
        subject = request.POST.get('subject', '')
        body = request.POST.get('body', '').strip()
        
        if not body:
            messages.error(request, 'Message cannot be empty')
            return redirect('send_message', enrollment_id=enrollment_id)
        
        try:
            if user_role == 'student':
                student = models.Student.objects.get(id=user_id)
                message = models.Message.objects.create(
                    sender_student=student,
                    receiver_mentor=enrollment.mentor,
                    student_course=enrollment,
                    subject=subject,
                    body=body,
                )
                # Create notification for mentor
                if enrollment.mentor:
                    models.Notification.objects.create(
                        mentor=enrollment.mentor,
                        notification_type='message',
                        title=f'Message from {student.first_name}',
                        message=subject if subject else 'New message',
                    )
            else:  # mentor
                mentor = models.Mentor.objects.get(id=user_id)
                message = models.Message.objects.create(
                    sender_mentor=mentor,
                    receiver_student=enrollment.student,
                    student_course=enrollment,
                    subject=subject,
                    body=body,
                )
                # Create notification for student
                models.Notification.objects.create(
                    student=enrollment.student,
                    notification_type='message',
                    title=f'Message from Mentor {mentor.first_name}',
                    message=subject if subject else 'New message',
                )
            
            messages.success(request, 'Message sent successfully!')
            return redirect('student_dashboard' if user_role == 'student' else 'mentor_dashboard')
        except Exception as e:
            messages.error(request, f'Error sending message: {str(e)}')
            return redirect('send_message', enrollment_id=enrollment_id)
    
    context = {
        'enrollment': enrollment,
    }
    return render(request, 'schoolApp/send_message.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def newsletter_signup(request):
    """Handle newsletter signup"""
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        email = data.get('email', '').strip().lower()
        
        # Validate email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email or not re.match(email_regex, email):
            return JsonResponse({
                'success': False,
                'message': 'Please enter a valid email address'
            }, status=400)
        
        # Check if already subscribed
        if models.Newsletter.objects.filter(email=email, is_active=True).exists():
            return JsonResponse({
                'success': False,
                'message': 'You are already subscribed to our newsletter'
            }, status=400)
        
        # Create or reactivate subscription
        newsletter, created = models.Newsletter.objects.get_or_create(email=email)
        if not created and not newsletter.is_active:
            newsletter.is_active = True
            newsletter.save()
        
        # Send welcome email
        try:
            send_mail(
                subject='Welcome to EduForAll Newsletter',
                message=f'Thank you for subscribing to our newsletter! You will receive updates about our latest courses and learning opportunities.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True
            )
        except Exception as e:
            # Email sending failed but subscription was successful
            pass
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for subscribing to our newsletter!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }, status=500)


def newsletter_unsubscribe(request, email):
    """Handle newsletter unsubscribe"""
    try:
        newsletter = models.Newsletter.objects.get(email=email)
        newsletter.is_active = False
        newsletter.save()
        messages.success(request, 'You have been unsubscribed from our newsletter')
    except models.Newsletter.DoesNotExist:
        messages.error(request, 'Email not found')
    
    return redirect('school')