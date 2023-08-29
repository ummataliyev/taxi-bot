from django.db import models


class Province(models.Model):
    name_uz = models.CharField(max_length=256)
    name_ru = models.CharField(max_length=256)

    def __str__(self):
        return self.name_uz


class District(models.Model):
    name_uz = models.CharField(max_length=256)
    name_ru = models.CharField(max_length=256)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_uz
