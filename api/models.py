import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
	pass


class Product(models.Model):
	name = models.CharField(max_length=255)
	description = models.TextField()
	price = models.DecimalField(max_digits=10, decimal_places=2)
	stock = models.PositiveIntegerField()
	image = models.ImageField(upload_to='products/', blank=True, null=True)

	@property
	def in_stock(self):
		return self.stock > 0

	def __str__(self):
		return self.name


class Order(models.Model):
	class StatusChoices(models.TextChoices):
		PENDING = 'Pending'
		COMPLETED = 'Completed'
		CANCELLED = 'Cancelled'

	order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	status = models.CharField(
		max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING
	)
	created_at = models.DateTimeField(auto_now_add=True)

	products = models.ManyToManyField(Product, through='OrderItem', related_name='orders')

	def __str__(self):
		return f'{self.order_id} by {self.user.username}'


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField()

	@property
	def item_subtotal(self):
		return self.product.price * self.quantity

	def __str__(self):
		return f'{self.quantity} of {self.product.name} in order {self.order.order_id}'
