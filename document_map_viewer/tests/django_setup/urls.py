from django.urls import include, re_path

urlpatterns = [
    re_path(r'^map/', include('document_map_viewer.urls'), name='document_map_viewer'),
]
