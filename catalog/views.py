import datetime

from .models import Genre,Author,BookInstance,Book
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404,render
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse

from catalog.forms import RenewBookForm

# Create your views here.
def home(req):
	return HttpResponse('Hello World')

def index(request):
	"""View function for home page of site"""

	num_books = Book.objects.all().count()
	num_visits = request.session.get('num_visits', 0)
	request.session['num_visits'] = num_visits + 1
	num_instances = BookInstance.objects.all().count()

	# Available books(status = 'a')
	num_instances_available = BookInstance.objects.filter(status__exact='a').count()

	# The `all()` is implied by default
	# num_authors = Author.objects.all().count()
	num_authors = Author.objects.count()

	num_genres = Genre.objects.count()

	context = {
		'num_books': num_books,
		'num_authors': num_authors,
		'num_instances_available': num_instances_available,
		'num_instances': num_instances,
		'num_genres':num_genres,
		'num_visits':num_visits, 
	}

	return render(request, 'index.html', context=context)

# Book View
class BookListView(generic.ListView):
	model = Book
	context_object_name = 'lists'
	paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

# Author View
class AuthorListView(generic.ListView):
	model = Author

class AuthorDetailView(generic.DetailView):
	model = Author

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_user.html'
	paginate_by = 10

	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
	"""view function for renewing a specific BookInstance by librarian."""
	book_instance = get_object_or_404(BookInstance, pk=pk)

	# if this is a POST request then process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request
		form = RenewBookForm(request.POST)

		# Check the form is valid
		if form.is_valid():
			book_instance.due_back = form.cleaned_data['renewal_date']
			book_instance.save()

			# redirect to a new URL
			return HttpResponseRedirect(reverse('all-borrowed'))
	# If this is a GET (or any other method) create the default form.
	else:
		proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
		form = RenewBookForm(initial={'renewal_date': 'proposed_renewal_date'})
	
	context = {
		'form': form,
		'book_instance': book_instance,
	}

	return render(request, 'catalog/book_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from catalog.models import Author, Book

class AuthorCreate(CreateView):
	model = Author
	fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
	initial = {'date_of_death': '11/06/2022'}

class AuthorUpdate(UpdateView):
	model = Author
	fields = '__all__'

class AuthorDelete(DeleteView):
	model = Author
	success_url = reverse_lazy('authors')

# Book
class BookCreate(CreateView):
	model = Book
	fields = ['title', 'author', 'summary', 'isbn','genre', 'language']
	initial = {'language': 'Bengali'}

class BookUpdate(UpdateView):
	model = Book
	fields = '__all__'

class BookDelete(DeleteView):
	model = Book
	success_url = reverse_lazy('books')