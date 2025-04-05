from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer
from products.models import Product, Discount

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'subtotal')

    def validate(self, attrs):
        product = attrs['product']
        quantity = attrs['quantity']

        if quantity > product.stock:
            raise serializers.ValidationError({
                'quantity': f'Only {product.stock} items available in stock.'
            })

        return attrs

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    discount_code = serializers.CharField(write_only=True, required=False)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Cart
        fields = ('id', 'items', 'discount_code', 'subtotal', 'total', 'created_at', 'updated_at')

    def validate_discount_code(self, value):
        try:
            discount = Discount.objects.get(code=value)
            if not discount.is_valid:
                raise serializers.ValidationError('This discount code is not valid.')
            return value
        except Discount.DoesNotExist:
            raise serializers.ValidationError('Invalid discount code.') 