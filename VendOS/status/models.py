from django.db import models

# Create your models here.
class Status(models.Model):
    last_hardbeat = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Last hardbeat: {self.last_hardbeat})"