from decimal import Decimal
from random import randint, sample

from django.core.management.base import BaseCommand
from faker import Faker

from api.models import Order, OrderItem, Product, User


class Command(BaseCommand):
	help = 'Populate the database with some initial data'

	def handle(self, *args, **options):
		# Create an superuser if it doesn't exist
		user = User.objects.filter(username='admin').first()
		if not user:
			user = User.objects.create_superuser(
				username='admin', password='test'
			)

		# Create some products
		fake: Faker = Faker()

		for _ in range(randint(10, 10**2)):
			Product.objects.create(
				name=fake.name(),
				description=fake.paragraph(),
				price=Decimal(randint(0, 10**6) / 100),
				stock=randint(0, 10**4),
			)

		products = Product.objects.all()

		# Create some orders
		for _ in range(randint(10, 10**2)):
			order = Order.objects.create(user=user)

			for product in sample(list(products), randint(1, 5)):
				OrderItem.objects.create(
					order=order, product=product, quantity=randint(1, 10)
				)
