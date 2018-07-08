from django.conf.urls import url, include
from django.conf import settings
from django.contrib.auth import views as authviews

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^table-records$', views.table_records, name='table'),
    url(r'^logout/$', authviews.logout, {"next_page": '/'}, name="logout"), 
    url(r'^auth-token/(?P<token>\w+)/$',views.authenticate_token,name="auth-token"),
    url(r'^records/ajax-records-date$',views.ajax_records_date,name="ajax-records-date"),
    url(r'^cache-error$', views.error_cache, name='error-cache'),
]