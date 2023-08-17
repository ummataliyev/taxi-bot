from django.db import models


class Province(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=256)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
