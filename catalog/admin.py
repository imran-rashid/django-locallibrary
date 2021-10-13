from django.contrib import admin
from catalog.models import Genre,Book,BookInstance,Author,Language

admin.site.register(Genre)
admin.site.register(Language)

admin.site.site_header = 'Local Library Admin Panel'
admin.site.site_title = 'Welcome to Local Library'
admin.site.index_title = 'Books Catalog'

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
	list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
	fields = ('last_name', 'first_name', ('date_of_birth', 'date_of_death')) # how all the items will be laid out
	# exclude = ('date_of_death') //= won't be included in list display table

# Inline editing of associated records
class BookInstanceInline(admin.TabularInline):
	model = BookInstance
	extra = 0

@admin.register(Book)
class BookAdmin(admin.ModelAdmin): 
	list_display = ('title', 'author', 'display_genre')

	inlines = (BookInstanceInline,)


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin): 
	#list_display = ('book', 'due_back', 'id','status') # display as title
	# list_filter = ('status', 'due_back') # showing filtering options

	list_display = ('book', 'status', 'borrower', 'due_back', 'id')
	list_filter = ('status', 'due_back')

	fieldsets = (
		('Add Book', {
			'fields': ('book', 'imprint', 'id')	
		}),
		('Availability', {
			'fields': ('status','due_back')
		})
	)
