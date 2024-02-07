from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.settings_view, name="settings_view"),
    path('ship-from-addresses/', views.ship_from_addresses, name="ship_from_addresses"),
    path('edit-address/<str:record_id>/', views.edit_address, name="edit_address"),
    path('delete-address/<str:record_id>', views.delete_address, name="delete_address"),
    path('add-default-address/', views.add_default_address, name="add_default_address"),
    path('edit-package/<str:record_id>/', views.edit_package, name="edit_package"),
    path('delete-package/<str:record_id>', views.delete_package, name="delete_package"),
    path('packages/', views.saved_packages, name="saved_packages"),
]
