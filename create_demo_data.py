# Run this after running migrations:
# python manage.py shell < create_demo_data.py
from django.contrib.auth import get_user_model
from food_app.models import Category, Product
User = get_user_model()

# Create admin user
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@foodie.com', 'admin123')
    print('Created admin user: admin / admin123')
else:
    print('Admin user already exists')

# Create sample category and products
cat, _ = Category.objects.get_or_create(name='Fast Food')
sample_products = [
    {'name':'Cheesy Burger','description':'Classic beef burger with cheddar cheese','price':5.99},
    {'name':'Margherita Pizza','description':'Fresh tomato, basil and mozzarella','price':8.50},
    {'name':'Crispy Fries','description':'Golden salted fries','price':2.99},
    {'name':'Veg Wrap','description':'Healthy veg wrap with sauces','price':4.25},
    {'name':'Chocolate Ice Cream','description':'Creamy chocolate scoop','price':1.99},
]
for p in sample_products:
    prod, created = Product.objects.get_or_create(name=p['name'], defaults={
        'description': p['description'],
        'price': p['price'],
        'quantity': 50,
        'category': cat,
    })
    if created:
        print('Created product', prod.name)
    else:
        print('Product exists', prod.name)
