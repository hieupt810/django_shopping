from django.db.models import Max
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
			self.permission_classes = [IsAuthenticated]

		return super().get_permissions()


class ProductDetailAPIView(generics.RetrieveAPIView):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	lookup_url_kwarg = 'product_id'


class ProductInfoAPIView(APIView):
	def get(self, request):
		products = Product.objects.all()
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
