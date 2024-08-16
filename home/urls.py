from django.urls import path

from .views import (
    index_page,
    download_page,
    disclaimer_contact_page
)

app_name='homeapp'
urlpatterns = [
    path('', index_page, name='index_page'),
    path('dc', disclaimer_contact_page, name='disclaimer_contact_page'),
    path('du/', download_page, name='download_page'),
]