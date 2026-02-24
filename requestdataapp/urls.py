
from django.urls import path

from requestdataapp.views import process_get_view, user_bio, handle_file_upload

app_name = "req"

urlpatterns = [
    path("get/", process_get_view, name="get_view"),
    path("bio/", user_bio, name="user_bio"),
    path("upload/", handle_file_upload, name="file_upload"),
]