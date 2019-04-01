from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListTasksView.as_view()),
    path('create', views.CreateTaskView.as_view()),
    path('<pk>', views.ViewTaskView.as_view()),
    path('<pk>/delete', views.DeleteTaskView.as_view()),
    path('<pk>/update', views.UpdateTaskView.as_view()),
    path('<pk>/mark/done', views.MarkTaskDoneView.as_view()),
    path('<pk>/mark/undone', views.MarkTaskUndoneView.as_view()),
]
