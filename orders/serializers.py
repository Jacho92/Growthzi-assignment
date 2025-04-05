from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory
from products.serializers import ProductSerializer
from products.models import Product, Discount

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_id', 'quantity', 'price', 'subtotal')
        read_only_fields = ('price', 'subtotal')

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ('id', 'status', 'notes', 'created_at')
        read_only_fields = ('created_at',)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    discount_code = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'user', 'status', 'payment_status',
            'shipping_address', 'billing_address', 'phone_number',
            'email', 'items', 'subtotal', 'shipping_cost',
            'discount_code', 'discount_amount', 'total', 'notes',
            'tracking_number', 'estimated_delivery_date',
            'status_history', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'order_number', 'user', 'subtotal', 'discount_amount',
            'total', 'created_at', 'updated_at'
        )

    def validate_discount_code(self, value):
        if not value:
            return None
            
        try:
            discount = Discount.objects.get(code=value)
            if not discount.is_valid:
                raise serializers.ValidationError('This discount code is not valid.')
            return value
        except Discount.DoesNotExist:
            raise serializers.ValidationError('Invalid discount code.')

    def validate(self, attrs):
        items = attrs.get('items')
        if not items:
            raise serializers.ValidationError({
                'items': 'At least one item is required.'
            })

        # Validate stock availability
        for item in items:
            product = item['product']
            quantity = item['quantity']
            if quantity > product.stock:
                raise serializers.ValidationError({
                    'items': f'Only {product.stock} items available for {product.name}.'
                })

        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        discount_code = validated_data.pop('discount_code', None)
        
        # Calculate order totals
        subtotal = sum(
            item['product'].price * item['quantity']
            for item in items_data
        )

        # Apply discount if valid
        discount_amount = 0
        if discount_code:
            try:
                discount = Discount.objects.get(code=discount_code)
                if discount.is_valid and subtotal >= discount.min_purchase_amount:
                    if discount.discount_type == 'percentage':
                        discount_amount = subtotal * (discount.amount / 100)
                    else:
                        discount_amount = discount.amount

                    if discount.max_discount_amount:
                        discount_amount = min(discount_amount, discount.max_discount_amount)

                    # Update discount usage
                    discount.times_used += 1
                    discount.save()
            except Discount.DoesNotExist:
                pass

        # Create order
        validated_data['subtotal'] = subtotal
        validated_data['discount_amount'] = discount_amount
        validated_data['total'] = subtotal - discount_amount + validated_data.get('shipping_cost', 0)
        
        if discount_code and discount_amount > 0:
            validated_data['discount'] = discount

        order = Order.objects.create(**validated_data)

        # Create order items
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
                subtotal=product.price * quantity
            )

            # Update product stock
            product.stock -= quantity
            product.save()

        return order 