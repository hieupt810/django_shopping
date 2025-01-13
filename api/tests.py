import random
import string

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from api.models import Order, User


# Create your tests here.
def random_string(k=10):
	return ''.join(random.choices(string.ascii_lowercase + string.digits, k=k))


class UserOrderTestCase(TestCase):
	usernames = [random_string() for _ in range(10)]

	def setUp(self):
		users = []
		for username in self.usernames:
			users.append(
				User.objects.create_user(
					username=username, password=random_string()
				)
			)

		for user in users:
			for _ in range(random.randint(1, 10)):
				Order.objects.create(user=user)

	def test_user_order_enpoint_retrieves_only_authenticated_user_orders(self):
		for username in self.usernames:
			user = User.objects.get(username=username)
			self.client.force_login(user)

			response = self.client.get(reverse('user-orders'))
			self.assertEqual(response.status_code, status.HTTP_200_OK)

			orders = response.json()
			self.assertTrue(all(order['user'] == user.id for order in orders))

	def test_user_order_enpoint_unauthenticated(self):
		response = self.client.get(reverse('user-orders'))
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
