# food_app/context_processors.py

from .models import Category

def category_links(request):
    """Makes all categories available as 'category_links' in every template context."""
    # You need to run migrations and create categories for this to return anything
    return {
        'category_links': Category.objects.all()
    }