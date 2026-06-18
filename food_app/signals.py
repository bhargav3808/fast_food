from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    # Only run for the food_app app
    if sender.name != 'food_app':
        return
    Category = apps.get_model('food_app', 'Category')
    defaults = [
        ('Breakfast','Hearty morning meals'),
        ('Lunch','Midday favourites'),
        ('Dinner','Evening specials'),
        ('Desserts','Sweet treats'),
        ('Drinks','Beverages'),
        ('Fast Food','Quick bites'),
    ]
    for name, desc in defaults:
        obj, created = Category.objects.get_or_create(name=name, defaults={'description': desc})
