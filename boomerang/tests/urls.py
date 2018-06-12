from django.conf.urls import url
from django.contrib import admin

from boomerang.model_admins import JobAdmin
from boomerang.models import Job


admin.site.register(Job, JobAdmin)


urlpatterns = [
    url(r'^admin/', admin.site.urls),
]
