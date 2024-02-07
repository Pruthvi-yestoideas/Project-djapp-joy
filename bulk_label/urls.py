from django.urls import path
from . import views

app_name = 'bulk_label'

urlpatterns = [
    path('', views.bulk_label, name="bulk_label"),
    path('file-upload/', views.file_upload, name="file_upload"),
    path('upload-data/', views.upload_data, name="upload_data"),
    path('send-bulk-label-request/', views.send_bulk_label_request, name="send_bulk_label_request"),
    path('validate-address/', views.validate_address, name="address_validation"),
    path('validate-package/', views.validate_package, name="validate_package")
]
