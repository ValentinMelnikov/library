from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import Book, Author, BookInstance, Genre


def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_books_with_title = Book.objects.filter(title__icontains="stars").count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(
        request,
        'books/index.html',
        context={'num_books': num_books,
                 'num_instances': num_instances,
                 'num_instances_available': num_instances_available,
                 'num_authors': num_authors,
                 'num_books_with_title': num_books_with_title,
                 'num_visits': num_visits},
    )


class BookListView(ListView):
    template_name = 'books/book_list.html'
    model = Book
    paginate_by = 5


class BookDetailView(DetailView):
    template_name = 'books/book_detail.html'
    model = Book


class AuthorListView(ListView):
    template_name = 'authors/author_list.html'
    model = Author


class AuthorDetailView(DetailView):
    template_name = 'authors/author_detail.html'
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin,ListView):
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')