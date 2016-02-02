from django.conf.urls.defaults import patterns, url
from isc_admin import AdminApp
from views import abc


class BoomerangAdminApp(AdminApp):
    def get_urls(self):
        urls = patterns('',
             url(r'^abc/?$', abc, name='abc'),
        )
        return urls