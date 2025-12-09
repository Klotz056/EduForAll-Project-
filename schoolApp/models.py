from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

# Create your models here.

class School(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    location = models.CharField(max_length=100)
    established_date = models.DateField()

    def __str__(self):
        return self.name

class Instructor(models.Model):
     first_name = models.CharField(max_length=50)
     last_name = models.CharField(max_length=50)
     email = models.EmailField(unique=True)
     phone_number = models.CharField(max_length=15)

     def __str__(self):
         return f"{self.first_name} {self.last_name}"       

class Course(models.Model):
    COURSE_TYPE_CHOICES = [
        ('free', 'Free Tutorial'),
        ('paid', 'Paid Course'),
        ('both', 'Both Options'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='courses')
    start_date = models.DateField()
    end_date = models.DateField()
    course_type = models.CharField(max_length=10, choices=COURSE_TYPE_CHOICES, default='both')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Price for paid courses")
    duration_weeks = models.IntegerField(default=4, help_text="Duration in weeks")
    # image = models.ImageField(upload_to='courses/', blank=True, null=True)
    content = models.TextField(blank=True, null=True, help_text="Course content/syllabus")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Student)"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Mentor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    expertise = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Mentor)"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class StudentCourse(models.Model):
    ENROLLMENT_TYPE_CHOICES = [
        ('free', 'Free Tutorial'),
        ('mentored', 'With Mentoring'),
    ]
    
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrolled_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_type = models.CharField(max_length=20, choices=ENROLLMENT_TYPE_CHOICES)
    mentor = models.ForeignKey(Mentor, on_delete=models.SET_NULL, null=True, blank=True, related_name='mentored_students')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0, help_text="Progress percentage 0-100")
    completed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.first_name} - {self.course.title}"

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-enrollment_date']


class LearningPath(models.Model):
    """Track the learning journey of a student in a course"""
    student_course = models.OneToOneField(StudentCourse, on_delete=models.CASCADE, related_name='learning_path')
    start_date = models.DateTimeField(auto_now_add=True)
    total_lessons = models.IntegerField(default=0)
    completed_lessons = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    def get_completion_percentage(self):
        if self.total_lessons == 0:
            return 0
        return (self.completed_lessons / self.total_lessons) * 100
    
    def __str__(self):
        return f"Learning Path - {self.student_course.student.first_name}"


class Message(models.Model):
    """Store messages between mentor and student"""
    sender_student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_messages')
    sender_mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_messages')
    receiver_student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages')
    receiver_mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages')
    student_course = models.ForeignKey(StudentCourse, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    subject = models.CharField(max_length=200, default='')
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.sender_student:
            return f"Message from {self.sender_student.first_name} to Mentor"
        else:
            return f"Message from Mentor {self.sender_mentor.first_name} to Student"

    class Meta:
        ordering = ['-created_at']


class Notification(models.Model):
    """Store notifications for students and mentors"""
    NOTIFICATION_TYPE_CHOICES = [
        ('message', 'New Message'),
        ('course_update', 'Course Update'),
        ('progress_alert', 'Progress Alert'),
        ('course_added', 'Course Added'),
        ('enrollment', 'Course Enrollment'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.student:
            return f"Notification for {self.student.first_name}"
        else:
            return f"Notification for Mentor {self.mentor.first_name}"

    class Meta:
        ordering = ['-created_at']


class Newsletter(models.Model):
    """Store newsletter subscriptions"""
    email = models.EmailField(unique=True)
    subscribed_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-subscribed_date']

