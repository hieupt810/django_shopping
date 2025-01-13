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


# products
class ProductListCreateAPIView(generics.ListCreateAPIView):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer

	def get_permissions(self):
		self.permission_classes = [AllowAny]
		if self.request.method == 'POST':
			self.permission_classes = [IsAdminUser]

		return super().get_permissions()


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	lookup_url_kwarg = 'product_id'

	def get_permissions(self):
		self.permission_classes = [AllowAny]
		if self.request.method in ['PUT', 'PATCH', 'DELETE']:
			self.permission_classes = [IsAdminUser]

		return super().get_permissions()


class ProductInfoAPIView(generics.GenericAPIView):
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


# orders
class OrderListAPIView(generics.ListAPIView):
	queryset = Order.objects.prefetch_related('items__product')
	serializer_class = OrderSerializer


class UserOrderListAPIView(generics.ListAPIView):
	queryset = Order.objects.prefetch_related('items__product')
	serializer_class = OrderSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		return super().get_queryset().filter(user=self.request.user)
