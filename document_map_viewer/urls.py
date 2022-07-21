from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'document_map_viewer'

urlpatterns = [
    re_path('^search', views.search_view),
]

urlpatterns = format_suffix_patterns(urlpatterns)
