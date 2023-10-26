from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from .models import Author, Book, Reader, BookOrder
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterUserForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

menu = ['Учет выдачи книг ', 'Учет хранения книг', 'Учет читателей ', 'Войти']

def base(request):
    data = {
        'title': 'Главная страница',
        'menu': menu,
    }
    return render(request, 'base.html', context= data)


class BookRentedListView(ListView):
    model = Book
    template_name = 'book_index.html'


    def get(self, request, *args, **kwargs):
        get_order = BookOrder.objects.all()
        book = Book.objects.filter(pk__in = get_order.values('book'))
        return render(request, 'book_index.html', {'book_list':book})
    
    # @login_required
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:  # Проверка, зарегистрирован ли пользователь
            messages.error(request, 'Только зарегистрированные пользователи могут выполнять действия.')
            return redirect('login')
        
    
        action = request.POST.get('action')
        book_code = request.POST.get('book_code')

        if action == 'return':
            try:
                book = Book.objects.get(book_code=book_code)
                if not book.is_available:
                    book_order = BookOrder.objects.get(book=book, reader=request.user.reader)
                    book_order.delete()
                    book.is_available = True
                    book.save()
                    messages.success(request, 'Книга успешно сдана.')
                else:
                    messages.error(request, 'Книга уже находится на остатках.')
            except Book.DoesNotExist:
                messages.error(request, 'Книга с указанным кодом не найдена.')

        return redirect('book_available')
        

class BookAvailableListView(ListView):
    model = Book
    template_name = 'book_available.html'
    context_object_name = 'books'


    def get_queryset(self):
        rented_books = BookOrder.objects.values('book')
        available_books = Book.objects.exclude(pk__in=rented_books)
        return available_books
    

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        book_code = request.POST.get('book_code')
        if action == 'borrow':
            try:
                book = Book.objects.get(book_code=book_code)
                if book.is_available:
                    book_order = BookOrder.objects.create(book=book, reader=request.user.reader)
                    book_order.save()
                    book.is_available = False
                    book.save()
                    messages.success(request, 'Вы взяли книгу.')
                    return redirect('book_index')
                else:
                    messages.error(request, 'Книга уже взята.')
            except Book.DoesNotExist:
                messages.error(request, 'Книга с указанным кодом не найдена.')
        
        elif action == 'return':
            try:
                book = Book.objects.get(book_code=book_code)
                if not book.is_available:
                    book_order = BookOrder.objects.get(user=request.user.reader, book=book)
                    book_order.delete()
                    book.is_available = True
                    book.save()
                    messages.success(request, 'Книга успешно сдана.')
                else:
                    messages.error(request, 'Книга уже находится на остатках.')
            except Book.DoesNotExist:
                messages.error(request, 'Книга с указанным кодом не найдена.')

        return redirect('book_available')
    
    

class ReaderListView(LoginView, ListView):
    model = Reader
    template_name = 'reader_list.html'
    context_object_name = 'readers'
    authentication_form = AuthenticationForm

    
class ReaderCreateView(CreateView):
    model = Reader
    template_name = 'reader_create.html'
    fields = ['last_name', 'first_name', 'middle_name']
    success_url = '/library/book_available'


class RegisterView(LoginRequiredMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = reverse_lazy('/login')

    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/library/book_available')



class LoginView(ListView, LoginView):
    model = Reader
    template_name = 'login.html'
    context_object_name = 'readers'

    def post(self, request, *args, **kwargs):
        last_name = request.POST.get('last_name')
        try:
            reader = Reader.objects.get(last_name=last_name)
            login(request, reader.user)
            return redirect('/library/book_available')
        except Reader.DoesNotExist:
            messages.error(request, 'Читатель с указанной фамилией не найден.')
            return redirect('/library/register')

#     def get_success_url(self):
#         return reverse_lazy('/library/book_available')
