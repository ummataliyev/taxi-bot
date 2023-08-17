from django.db import models

from data.models import District
from data.models import Province


class Tg_Users(models.Model):
    user_id = models.IntegerField()
    step = models.IntegerField(default=0)
    number = models.IntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Tg_User"
        verbose_name_plural = "Tg_Users"

    def __str__(self) -> str:
        return f'{self.user_id}'


class Orders(models.Model):
    user = models.ForeignKey(Tg_Users, on_delete=models.SET_NULL, null=True, related_name='user_orders')
    from_to = models.ForeignKey(Province, on_delete=models.SET_NULL, blank=True, null=True)
    where = models.ForeignKey(District, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self) -> str:
        status_str = "Completed" if self.status else "Pending"
        return f"{self.user.user_id} has {status_str} taxi booking"
