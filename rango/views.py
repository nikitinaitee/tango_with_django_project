from django.shortcuts import render
from django.http import HttpResponse
# Import the Category model
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryFormfrom rango.forms import PageForm


def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary that will be passed to the template engine.

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    # Construct a dictionary to pass to the template engine as its context.
    context_dict = {'categories': category_list, "pages" : page_list}

    # Render the response and send it back!
    return render(request, 'rango/index.html', context_dict)

def about (request):
    context_dict = {'boldmessage': "This tutorial has been put together by Ugne Nikitinaite"}
    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}
    try:
        # If we can't find a category name slug with the given name, the .get() method raises
        # a DoesNotExist exception. So the .get() returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        # Retrieve all of the associated pages.
        # Note that filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category)
        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        context_dict['category'] = None
        context_dict['pages'] = None
    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)


def add_category(request):
    form = CategoryForm()
    # two different types of HTTP requests:
    # GET - request a representation of the specified resource.
    # POST -  submits data from the client’s web browser to be processed.
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
    
        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            cat = form.save(commit=True)
            # Now the category is saved, We could give a confirmation message, but since the most
            # recent category added is in index page, we can direct the user back to index page.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print(form.errors)
            
    # Will handle the bad form, new form, or no form supplied cases.
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None
		
	form = PageForm()
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
				return show_category(request, category_name_slug)
		else:
			print(form.errors)
			
	context_dict = {'form':form, 'category': category}
	return render(request, 'rango/add_page.html', context_dict)
