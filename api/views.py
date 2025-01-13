from django.db.models import Max
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from api.models import Order, Product
from api.serializers import (
	OrderSerializer,
	ProductInfoSerializer,
	ProductSerializer,
)


class ProductListCreateAPIView(generics.ListCreateAPIView):
	"""List and create products"""

	queryset = Product.objects.all()
	serializer_class = ProductSerializer

	def get_permissions(self):
		self.permission_classes = [AllowAny]
		if self.request.method == 'POST':
			self.permission_classes = [IsAdminUser]

		return super().get_permissions()


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
	"""Retrieve, update and delete a product"""

	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	lookup_url_kwarg = 'product_id'

	def get_permissions(self):
		self.permission_classes = [AllowAny]
		if self.request.method in ['PUT', 'PATCH', 'DELETE']:
			self.permission_classes = [IsAdminUser]

		return super().get_permissions()


class ProductInfoAPIView(generics.GenericAPIView):
	"""Get products info"""

	queryset = Product.objects.all()
	serializer_class = ProductInfoSerializer

	@extend_schema(responses=ProductInfoSerializer)
	@api_view(['GET'])
	def get(self, request):
		products = self.get_queryset()
		serializer = ProductInfoSerializer(
			{
				'products': products,
				'count': products.count(),
				'max_price': products.aggregate(max_price=Max('price'))[
					'max_price'
				],
			}
		)

		return Response(serializer.data, status=status.HTTP_200_OK)


class OrderListAPIView(generics.ListAPIView):
	"""List orders"""

	queryset = Order.objects.prefetch_related('items__product')
	serializer_class = OrderSerializer


class UserOrderListAPIView(generics.ListAPIView):
	"""List orders of the authenticated user"""

	queryset = Order.objects.prefetch_related('items__product')
	serializer_class = OrderSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		return super().get_queryset().filter(user=self.request.user)
