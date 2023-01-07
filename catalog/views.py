from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import Book, Author, BookInstance
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import RenewBookForm


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
    paginate_by = 5


class AuthorDetailView(DetailView):
    template_name = 'authors/author_detail.html'
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    model = BookInstance
    template_name = 'catalog/library_worker_templates/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class AllBorrowedBooksListView(LoginRequiredMixin, ListView):
    model = BookInstance
    template_name = 'catalog/library_worker_templates/all_borrowed_books.html'

    def get_queryset(self):
        return BookInstance.objects.all().filter(status__exact='o').order_by('due_back')


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '12/10/2016', }
    template_name = 'authors/author_form.html'


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    template_name = 'authors/author_form.html'


class AuthorDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('authors')
    template_name = 'books/book_confirm_delete.html'


class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    template_name = 'books/book_form.html'


class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']
    template_name = 'books/book_form.html'


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('index')
    template_name = 'books/book_confirm_delete.html'


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date, })

    return render(request, 'catalog/library_worker_templates/book_renew_librarian.html',
                  {'form': form, 'bookinst': book_inst})
