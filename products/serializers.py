from rest_framework import serializers
from .models import Category, Product, ProductImage, Discount

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'image', 'parent')

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'is_primary')

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source='category'
    )
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'price', 'category',
            'category_id', 'stock', 'is_active', 'images', 'uploaded_images',
            'created_at', 'updated_at'
        )
        read_only_fields = ('slug',)

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = Product.objects.create(**validated_data)

        for image in uploaded_images:
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=not product.images.exists()
            )

        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if uploaded_images:
            for image in uploaded_images:
                ProductImage.objects.create(
                    product=instance,
                    image=image,
                    is_primary=not instance.images.exists()
                )

        return instance

class DiscountSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.all(),
        write_only=True,
        source='products',
        required=False
    )
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        write_only=True,
        source='categories',
        required=False
    )

    class Meta:
        model = Discount
        fields = (
            'id', 'code', 'description', 'discount_type', 'amount',
            'start_date', 'end_date', 'min_purchase_amount',
            'max_discount_amount', 'usage_limit', 'times_used',
            'is_active', 'products', 'product_ids', 'categories',
            'category_ids', 'created_at', 'updated_at', 'is_valid'
        )
        read_only_fields = ('times_used', 'is_valid') 