from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
