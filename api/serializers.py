from rest_framework import serializers

from api.models import Order, OrderItem, Product


class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = sorted(['id', 'name', 'description', 'price', 'stock'])

	def validate_price(self, value):
		if value <= 0:
			raise serializers.ValidationError('Price must be greater than 0.')

		return value


class OrderItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = OrderItem
		fields = sorted(['product', 'quantity'])


class OrderSerializer(serializers.ModelSerializer):
	items = OrderItemSerializer(many=True, read_only=True)

	class Meta:
		model = Order
		fields = sorted(['order_id', 'user', 'status', 'created_at', 'items'])
