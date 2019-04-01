from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    done = models.NullBooleanField(default=False)

    def __str__(self):
        return '<Task user={} done={} content={}>'.format(self.user.username, self.done, self.content[0:20])  # pylint: disable=no-member, unsubscriptable-object

    """
    Wild patches for my makeshift rest-framework
    """
    def serialize(self):
        return {
            'id': self.pk,
            'content': self.content,
            'done': self.done
        }

    @classmethod
    def deserialize(klass, data):
        pk = data.get('id', None)
        if pk:
            try:
                return klass.objects.get(pk=pk)  # pylint: disable=no-member
            except klass.DoesNotExist:  # pylint: disable=no-member
                pass
        return klass(**data)
