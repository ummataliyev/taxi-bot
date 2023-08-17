from django.urls import path
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

from bot.views import web_hook_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('secret/', csrf_exempt(web_hook_view))
]
