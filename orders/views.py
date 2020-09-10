from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created


# There are several options for a message broker for Celery, including key/value stores
# such as Redis, or an actual message system such as RabbitMQ. Let's configure Celery
# with RabbitMQ, since it's the recommended message worker for Celery. RabbitMQ
# is lightweight, it supports multiple messaging protocols, and it can be used when
# scalability and high availability are required.


def order_create(request):
  cart = Cart(request)
  if request.method == 'POST':
    form = OrderCreateForm(request.POST)
    if form.is_valid():
      order = form.save()
      for item in cart:
        OrderItem.objects.create(order=order,
                                product=item['product'],
                                price=item['price'],
                                quantity=item['quantity'])
      # clear the cart
      cart.clear()
      # launch asynchronous task
      order_created.delay(order.id)
      return render(request,
                    'orders/order/created.html',
                    {'order': order})
  else:
    form = OrderCreateForm()
  return render(request,
                'orders/order/create.html',
                {'cart': cart, 'form': form})