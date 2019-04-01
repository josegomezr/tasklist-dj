"""
Form classes for tasks app.
"""
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    """
    Task Create/Update form.
    """
    class Meta:
        model = Task
        fields = ('content', 'done',)
