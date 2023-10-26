from django.urls import path
from .views import  BookRentedListView, BookAvailableListView, RegisterView, ReaderCreateView, ReaderListView, LoginView, base


urlpatterns = [
    path('book_index/', BookRentedListView.as_view(), name='book_index'),
    path('book_available/', BookAvailableListView.as_view(), name='book_available'),
    path('register/', RegisterView.as_view(), name='register'),
    path('reader_list/', ReaderListView.as_view(), name='reader_list'),
    path('reader_create/', ReaderCreateView.as_view(), name='reader_create'),
    path('login/', LoginView.as_view(), name='login'),
    path('base/', base, name='base'),
]