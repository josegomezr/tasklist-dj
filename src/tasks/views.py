from django.shortcuts import get_object_or_404

from json_views.views import JSONListView, JSONDetailView
from jwt_auth.mixins import JSONWebTokenAuthMixin as JWTRequired
from . import mixins
from .models import Task
from .forms import TaskForm

class ListTasksView(JWTRequired, mixins.TasksQSForLoggedUser, mixins.JSONListView):
    model = Task
    def get_context_data(self, **kwargs):
        return {
            'data': [i.serialize() for i in self.get_queryset()]  # pylint: disable=undefined-variable
        }

class ViewTaskView(JWTRequired, mixins.TasksQSForLoggedUser, mixins.JSONDetailView):
    model = Task

    def get_context_data(self, **kwargs):
        return {
            'data': self.get_object().serialize()
        }

class DeleteTaskView(JWTRequired, mixins.TasksQSForLoggedUser, mixins.JSONDeleteView):
    model = Task

    def get_context_data(self, **kwargs):
        self.status_code = 204

        return {}

class MarkTaskDoneView(JWTRequired, mixins.TasksQSForLoggedUser, mixins.JSONView):
    def put(self, request, **kwargs):
        obj = get_object_or_404(self.get_queryset(), id=kwargs['pk'])

        obj.done = True
        obj.save()
        self.status_code = 204
        return self.render_to_response({})

class MarkTaskUndoneView(JWTRequired, mixins.TasksQSForLoggedUser, mixins.JSONView):
    def put(self, request, **kwargs):
        obj = get_object_or_404(self.get_queryset(), id=kwargs['pk'])

        obj.done = False
        obj.save()
        self.status_code = 204
        return self.render_to_response({})


class UpdateTaskView(JWTRequired, mixins.TasksQSForLoggedUser, mixins.JSONUpdateView):
    form_class = TaskForm
    
    def get(self, *args, **kwargs):
        return self.http_method_not_allowed(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        self.status_code = 204
        context = self.get_context_data(form)
        return self.render_to_response(context)

    def form_invalid(self, form):
        self.status_code = 400
        context = self.get_context_data(form)
        return self.render_to_response(context)

    def get_context_data(self, form):
        if not form.errors:
            return {}
        return {
            'errors': form.errors
        }

class CreateTaskView(JWTRequired, mixins.TasksQSForLoggedUser, mixins.JSONCreateView):
    form_class = TaskForm
    
    def get(self, *args, **kwargs):
        return self.http_method_not_allowed(*args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        self.status_code = 200
        context = self.get_context_data(form)
        return self.render_to_response(context)

    def form_invalid(self, form):
        self.status_code = 400
        context = self.get_context_data(form)
        return self.render_to_response(context)

    def get_context_data(self, form):
        if not form.errors:
            return {
                'data': form.instance.serialize()
            }

        return {
            'errors': form.errors
        }
