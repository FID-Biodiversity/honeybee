from django.urls import include, re_path

urlpatterns = [
    re_path(r'^map/', include('honeybee.urls'), name='honeybee'),
]
