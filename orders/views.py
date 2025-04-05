from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .tasks import send_order_confirmation_email, update_order_status
from cart.models import Cart

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        
        # Send order confirmation email
        send_order_confirmation_email.delay(order.id)

        # Clear the user's cart if order was created from cart
        cart_id = self.request.data.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, user=self.request.user)
                cart.items.all().delete()
                cart.discount = None
                cart.save()
            except Cart.DoesNotExist:
                pass

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff members can update order status'},
                status=status.HTTP_403_FORBIDDEN
            )

        order = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')

        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update status asynchronously
        update_order_status.delay(order.id, new_status, notes)

        return Response({'message': 'Status update initiated'})

    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        order = self.get_object()
        history = order.status_history.all().order_by('-created_at')
        data = [{
            'status': item.status,
            'notes': item.notes,
            'created_at': item.created_at
        } for item in history]
        return Response(data)

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        orders = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
