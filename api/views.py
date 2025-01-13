from django.db.models import Max
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import Order, Product
from api.serializers import OrderSerializer, ProductInfoSerializer, ProductSerializer


# products
class ProductListAPIView(generics.ListAPIView):
	queryset = Product.objects.filter(stock__gt=0)
	serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveAPIView):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	lookup_url_kwarg = 'product_id'


@api_view(['GET'])
def product_info(request):
	products = Product.objects.all()
	serializer = ProductInfoSerializer(
		{
			'products': products,
			'count': products.count(),
			'max_price': products.aggregate(max_price=Max('price'))['max_price'],
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
