from django.contrib import admin
from .models import Author, Genre, Book, BookInstance


class BookInline(admin.TabularInline):
    list_display = ('title', 'author', 'display_genre')
    model = Book


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookInline]


@admin.register(BookInstance)
class BooksInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'due_back', 'id')


admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre)
admin.site.register(Book)
# admin.site.register(Author)

# admin.site.register(BookInstance)
