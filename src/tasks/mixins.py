"""
Wild monkey patches to django to mimic DRF behavior.
"""

from .models import Task
from django.http import JsonResponse
import json
from django.views.generic import View
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import BaseDeleteView, BaseUpdateView, BaseCreateView


class TasksQSForLoggedUser:
    def get_queryset(self):
        if not self.request.user.is_authenticated: # pylint: disable=no-member
            # this is a very stupid hack, but just
            # in case someone mess-up with authentication
            # if no authenticated user is present
            # filter the queryset with an impossible contidion
            return Task.objects.filter(id=-1).filter(id=0) # pylint: disable=no-member

        return Task.objects.filter(user=self.request.user) # pylint: disable=no-member


class JsonResponseMixin:
    response_class = JsonResponse
    content_type = 'application/json'
    status_code = 200

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.

        Pass response_kwargs to the constructor of the response class.
        """
        response_kwargs.setdefault('content_type', self.content_type)
        response = self.response_class(
            data=context,
            **response_kwargs
        )
        response.status_code = self.status_code
        return response


class JSONView(JsonResponseMixin, View):
    pass


class JSONListView(BaseListView, JSONView):
    pass


class JSONDetailView(BaseDetailView, JSONView):
    pass


class JSONDeleteView(BaseDetailView, JSONView):
    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        self.object.delete()
        
        return self.render_to_response(context)


class ProcessFormJSONBody:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()  # pylint: disable=no-member
        if (self.request.method in ('POST', 'PUT')  # pylint: disable=no-member
            and self.request.content_type == 'application/json'):  # pylint: disable=no-member
            try:
                body = json.loads(self.request.body)  # pylint: disable=no-member
                kwargs.update({
                    'data': body
                })
            except ValueError:
                pass
        return kwargs


class JSONUpdateView(ProcessFormJSONBody, BaseUpdateView, JSONView):
    pass


class JSONCreateView(ProcessFormJSONBody, BaseCreateView, JSONView):
    pass
