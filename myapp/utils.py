import json
from django.utils import timezone
from .models import User, Customer, Order

def cartData(request):
    cartItems = None
    order = None
    items = None

    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        customer, created = Customer.objects.get_or_create(
            user=user,
            defaults={'name': user.username, 'email': user.email}
        )

        # Get the order and create it if it doesn't exist
        order, created = Order.objects.get_or_create(
            customer=customer,
            complete=False,
            defaults={'date_order': timezone.now()}  # Set the date_order field for new orders
        )

        # Retrieve the items in the cart
        items = order.orderitem_set.all()

        # Get the cart item count using your implementation
        cartItems = order.get_cart_items

    return {'cartItems': cartItems, 'order': order, 'items': items}