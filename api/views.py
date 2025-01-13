from django.db.models import Max
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from api.filters import InStockFilterBackend, OrderFilter, ProductFilter
from api.models import Order, Product
from api.serializers import (
	OrderSerializer,
	ProductInfoSerializer,
	ProductSerializer,
)


class ProductListCreateAPIView(generics.ListCreateAPIView):
	"""List and create products"""

	queryset = Product.objects.order_by('pk')
	serializer_class = ProductSerializer

	filter_backends = [
		DjangoFilterBackend,
		filters.SearchFilter,
		filters.OrderingFilter,
		InStockFilterBackend,
	]
	filterset_class = ProductFilter
	search_fields = ['name', 'description']
	ordering_fields = ['name', 'price', 'stock']

	pagination_class = LimitOffsetPagination
	pagination_class.max_limit = 50

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


class OrderViewSet(viewsets.ModelViewSet):
	queryset = Order.objects.prefetch_related('items__product')
	serializer_class = OrderSerializer
	permission_classes = [IsAuthenticated]

	filter_backends = [DjangoFilterBackend]
	filterset_class = OrderFilter

	def get_queryset(self):
		queryset = super().get_queryset()
		if not self.request.user.is_staff:
			queryset = queryset.filter(user=self.request.user)

		return queryset

	@action(detail=False, methods=['get'], url_path='user-orders')
	def user_orders(self, request):
		orders = self.get_queryset().filter(user=request.user)
		serializer = self.get_serializer(orders, many=True)

		return Response(serializer.data, status=status.HTTP_200_OK)
