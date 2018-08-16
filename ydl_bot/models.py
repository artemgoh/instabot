from django.db import models


class InstPost(models.Model):
    media = models.CharField(max_length=60)


class LikeQty(models.Model):
    qty = models.IntegerField(default=50)


class Description(models.Model):
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name
# Create your models here.
