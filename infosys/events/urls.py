from django.urls import path
from .views import *


urlpatterns = [
    path('', EventList.as_view(), name='list'),
    path('search/', EventSearch.as_view(), name='event_search'),
    path('create/', EventCreate.as_view(), name='event_create'),
    path('room/<int:pk>', room_view),
    path('list/', list_view),
    path('<int:pk>', room_test),
    path('<int:pk>/edit/', EventUpdate.as_view(), name='event_update'),
    path('<int:pk>/delete/', EventDelete.as_view(), name='event_Delete'),
    path('anek/', anek),
    ]