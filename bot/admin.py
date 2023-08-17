from django.contrib import admin

from bot.models import Orders
from bot.models import Tg_Users


admin.site.register(Orders)
admin.site.register(Tg_Users)
