from django.urls import path
from .views import JournalEntryListCreateView, JournalEntryRetrieveUpdateDestroyView

urlpatterns = [
    path('entries/', JournalEntryListCreateView.as_view(), name='journalentry-list-create'),
    path('entries/<int:pk>/', JournalEntryRetrieveUpdateDestroyView.as_view(), name='journalentry-retrieve-update-destroy'),
]