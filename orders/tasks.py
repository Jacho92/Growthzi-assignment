from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Order

@shared_task
def send_order_confirmation_email(order_id):
    """
    Send order confirmation email to customer
    """
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Order Confirmation - {order.order_number}'
        message = render_to_string('orders/email/order_confirmation.html', {
            'order': order
        })
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            html_message=message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order confirmation email: {str(e)}")
        return False

@shared_task
def send_order_status_update_email(order_id):
    """
    Send order status update email to customer
    """
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Order Status Update - {order.order_number}'
        message = render_to_string('orders/email/order_status_update.html', {
            'order': order
        })
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            html_message=message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order status update email: {str(e)}")
        return False

@shared_task
def update_order_status(order_id, new_status, notes=''):
    """
    Update order status and create status history entry
    """
    try:
        order = Order.objects.get(id=order_id)
        old_status = order.status
        order.status = new_status
        order.save()

        # Create status history entry
        order.status_history.create(
            status=new_status,
            notes=notes
        )

        # Send status update email
        if old_status != new_status:
            send_order_status_update_email.delay(order_id)
        
        return True
    except Exception as e:
        print(f"Error updating order status: {str(e)}")
        return False

@shared_task
def process_pending_orders():
    """
    Process pending orders (can be extended based on business logic)
    """
    try:
        pending_orders = Order.objects.filter(status='pending')
        for order in pending_orders:
            # Add your business logic here
            # For example, check inventory, process payment, etc.
            update_order_status.delay(order.id, 'processing', 'Order is being processed')
        return True
    except Exception as e:
        print(f"Error processing pending orders: {str(e)}")
        return False 