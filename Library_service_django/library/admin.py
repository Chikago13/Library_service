from django.contrib import admin
from .models import Author, Book, Reader, BookOrder

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Reader)
admin.site.register(BookOrder)
