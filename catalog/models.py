from django.db import models
from django.urls import reverse
import uuid
from datetime import date
from django.contrib.auth.models import User

# Create your models here.
class Genre(models.Model):
	"""Model representing a book genre"""
	name = models.CharField(max_length=200, help_text='Enter a book Genre (e.g. Romance)')

	def __str__(self):
		"""String for representing the Model object"""
		return self.name


class Language(models.Model):
	"""Model representing a language"""
	name = models.CharField(max_length=200, help_text="Enter the book's natural language (Bengali, English, Hindi)")

	def __str__(self):
		"""String for representing Model Object (admin site)"""
		return self.name


class Book(models.Model):
	"""Model representing a book (not a specific copy of a book)"""
	title = models.CharField(max_length=200)

    # Foreign Key used because book can only have one author, but authors can have multiple books
	author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
	summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
	isbn = models.CharField('ISBN', max_length=13, unique=True, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    # ManyToManyField used because genre can contain many books. Books can cover many genres
	genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')
	language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

	class Meta:
		ordering = ['title', 'author']

	def display_genre(self):
		"""Creates a string for the Genre. This is required to display in Admin"""
		return ', '.join([genre.name for genre in self.genre.all()[0:3]])

	display_genre.short_description = 'Genre' # it will set title Genre(default fn name)

	def __str__(self):
		"""String for representing the Model Object"""
		return self.title

	def get_absolute_url(self):
		"""Returns the url to access a particular book instance."""
		return reverse('book-detail', args=[str(self.id)])


class BookInstance(models.Model):
	"""Model representing a specific copy of a book (that can be borrowed from library)"""
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique Id for this Particular book across whole library')
	# book can't be deleted while it referenced by bookInstance
	book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
	imprint = models.CharField(max_length=200)
	due_back = models.DateField(null=True, blank=True)
	borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

	@property
	def is_overdue(self):
		if self.due_back and date.today() > self.due_back:
			return True
		return False

	LOAN_STATUS = [
		('m', 'Maintenance'),
		('o', 'On loan'),
		('a', 'Available'),
		('r', 'Reserved'),
	]

	status = models.CharField(
		max_length=1,
		choices=LOAN_STATUS,
		blank=True,
		default='m',
		help_text='Book Availability',
	)

	class Meta:
		ordering = ['due_back']
		permissions = (('can_mark_returned', 'Set a book as returned'),)

	def __str__(self):
		"""String for representing the Model Object"""
		return f'{self.id} ({self.book.title})'

class Author(models.Model):
	"""Model representing an author"""
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	date_of_birth = models.DateField('birthday',null=True, blank=True)
	date_of_death = models.DateField('died', null=True, blank=True)

	class Meta:
		ordering = ['last_name', 'first_name']

	def get_absolute_url(self):
		"""Returns the URL to access a particular author instance"""
		return reverse('author-details', args=[str(self.id)])

	def __str__(self):
		"""String for representing the Model Object"""
		return f'{self.last_name}, {self.first_name}'
