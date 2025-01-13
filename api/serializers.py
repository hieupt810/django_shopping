from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from api.models import Order, OrderItem, Product


# Product
class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = sorted(['name', 'description', 'price', 'stock'])

	def validate_price(self, value):
		if value <= 0:
			raise serializers.ValidationError('Price must be greater than 0.')

		return value


class ProductInfoSerializer(serializers.Serializer):
	products = ProductSerializer(many=True)
	count = serializers.IntegerField()
	max_price = serializers.FloatField()


# Order
class OrderItemSerializer(serializers.ModelSerializer):
	product_name = serializers.CharField(
		max_length=255, source='product.name', read_only=True
	)
	product_price = serializers.DecimalField(
		max_digits=10, decimal_places=2, source='product.price', read_only=True
	)

	class Meta:
		model = OrderItem
		fields = sorted(
			['product_name', 'product_price', 'quantity', 'item_subtotal']
		)


class OrderSerializer(serializers.ModelSerializer):
	items = OrderItemSerializer(many=True, read_only=True)
	created_at = serializers.SerializerMethodField(
		method_name='get_formatted_date'
	)
	total_price = serializers.SerializerMethodField(method_name='get_total')

	@extend_schema_field(serializers.CharField(max_length=255))
	def get_formatted_date(self, obj):
		return obj.created_at.strftime('%B %d, %Y')

	@extend_schema_field(
		serializers.DecimalField(max_digits=10, decimal_places=2)
	)
	def get_total(self, obj):
		order_items = obj.items.all()
		return sum(order_items.item_subtotal for order_items in order_items)

	class Meta:
		model = Order
		fields = sorted(
			['order_id', 'user', 'status', 'created_at', 'items', 'total_price']
		)
