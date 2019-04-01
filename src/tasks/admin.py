"""
Admin classes for tasks app.
"""
from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    AdminHandler for tasks
    """
