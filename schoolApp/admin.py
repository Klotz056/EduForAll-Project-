from django.contrib import admin
from . import models


# Register your models here.

admin.site.register(models.School)
admin.site.register(models.Instructor)
admin.site.register(models.Course)
admin.site.register(models.Student)
admin.site.register(models.Mentor)
admin.site.register(models.StudentCourse)
admin.site.register(models.LearningPath)
admin.site.register(models.Message)
admin.site.register(models.Notification)
admin.site.register(models.Newsletter)