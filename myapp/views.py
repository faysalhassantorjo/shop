from django.http import JsonResponse
from django.shortcuts import render,redirect
from .models import *
import json
from .utils import cartData
from django.contrib.auth.models import User,auth
from django.contrib import messages

from .decorators import admin_only

from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template


def index(request):
    categories = Category.objects.all()
    products = Product.objects.filter(hot_product=True)
    discounted_product = Product.objects.filter(discount_percent__gt=30)
    special_collection=Category.objects.filter(special_collection=True)
    special_discount =Category.objects.filter(any_special_discount=True)
    try:
        hero=Category.objects.get(hero_slide=True)
    except:
        hero={}

    # print('asdf',len(special_discount))
    # for banner in special_discount:
    #     print('banner name',banner.name)
    #     for product in discounted_product:
    #         if banner.superCategory and product.superCategory ==None:
    #             continue
    #         if banner.superCategory==product.superCategory:
    #             product.category.add(banner)
 
    

    Data = cartData(request)
    cartItems = Data['cartItems']
    items = Data['items']
    order = Data['order']

    

    context={'products': products ,
            'categories':categories,
            'items':items,
            'order':order,
            'cartItems':cartItems,
            'special_collection':special_collection,
            'special_discounts':special_discount,
            'hero_slide':hero,
            }
    return render(request,'myapp/index.html',context)


def category_list(request):
    categories = Category.objects.all()
    Data = cartData(request)
    cartItems = Data['cartItems']
    items = Data['items']
    order = Data['order']
    context = {'items': items, 'order': order, 'cartItems': cartItems,'categories':categories}
    return render(request, 'myapp/Category.html',context)


def product_list(request, category_id):
    Data = cartData(request)
    cartItems = Data['cartItems']
    categories = Category.objects.all()

    category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=category)

    products_in_category=len(products)

    return render(request, 'myapp/shop-grid.html',
                  {'products': products ,'cartItems':cartItems,'categories': categories,'products_in_category':products_in_category})

def productDetails(request,product_id):
    product=Product.objects.get(id=product_id)
    Data = cartData(request)
    cartItems = Data['cartItems']
    items = Data['items']
    order = Data['order']

    categories = Category.objects.all()


    return render(request,'myapp/product-details.html',{'product':product,'items':items,'order':order,'cartItems':cartItems,'categories':categories})

def cart(request):
    Data = cartData(request)
    cartItems = Data['cartItems']
    items = Data['items']
    order = Data['order']
    categories = Category.objects.all()

    coupon=Cuppon.objects.all()
    user=request.user
    c=Customer.objects.get(user=user)
    o=Order.objects.get(customer=c,complete=False)

    if request.method=='POST':
        q=request.POST['q']

        for c in coupon:
            if c.cuppon_name==q:
                o.after_using_coupn=c.percent
                o.save()
    
    save=o.total*(o.after_using_coupn/100)
    

    context={'items':items,'order':order,'cartItems':cartItems,"categories":categories,'save':save}
    return render(request,'myapp/cart-main.html',context)

def checkout(request):
    Data = cartData(request)
    cartItems = Data['cartItems']
    order = Data['order']
    items=Data['items']
    categories = Category.objects.all()

    context = {'cartItems': cartItems, 'order': order,'categories':categories,'items':items}
    return render(request,'myapp/checkout-main.html',context)



def updatItem(request):
    data = json.loads(request.body)
    print(data)
    productId = data['productID']
    action = data['action']

    size = data['selectedSize']
    print(size)

    user = request.user.username
    customer, created = Customer.objects.get_or_create(id=request.user.customer.id,
                                                       defaults={'name': user, 'user': user})
    print("Nam: ", user)
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product, size=size)
    if action == 'add':
        if product.instock == 0:
            messages.success(request, "out of stock")
        elif orderItem.quantity >= 2:
            messages.info(request, "maximum order limit is 2")
        else:
            orderItem.quantity = (orderItem.quantity + 1)
            product.instock = (product.instock - 1)
            messages.success(request, "Item added successfully")
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
        product.instock = (product.instock + 1)
    
    elif action == 'delete':
        orderItem.quantity=0

    orderItem.save()
    product.save()
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)


def updatCartItem(request):
    # data = json.loads(request.body)
    # print(data)
    # productId = data['productID']
    # action = data['action']
    # user = request.user.username
    # customer = Customer.objects.get(id=request.user.customer.id)
    # product = Product.objects.get(id=productId)
    # order= Order.objects.get(customer=customer, complete=False)
    # orderItem = OrderItem.objects.get(order=order, product=product)
    # if action == 'add':
    #     orderItem.quantity = (orderItem.quantity + 1)
    #     product.instock = (product.instock - 1)
    #     messages.success(request, "Item added successfully")
    # elif action == 'remove':
    #     orderItem.quantity = (orderItem.quantity - 1)
    #     product.instock = (product.instock + 1)
    #
    # # orderItem.save()
    # product.save()
    # if orderItem.quantity <= 0:
    #     orderItem.delete()
    return JsonResponse("Operation done", safe=False)

import datetime
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
@csrf_exempt
def processOrder(request):
    Data = cartData(request)
    items = Data['items']
    data=json.loads(request.body)
    transaction_id = datetime.datetime.now().timestamp()

    if request.user.is_authenticated:
        data['form']['name'] = request.user.customer.name
        data['form']['email'] = request.user.customer.email

        if request.user.is_authenticated:
            customer = request.user.customer
            address= data['shipping']['address']
            phon_number= data['shipping']['phon-number']
            email=data['shipping']['email-address']
            total=data['form']['total']

            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            shipping,created=ShippingAddress.objects.get_or_create(customer=customer,oder=order,address=address,phonNumber=phon_number)
            shipping.save()
            total = float(data['form']['total'])
            order.transaction_id = transaction_id
            if total == order.get_cart_total:
                order.complete = True
            order.save()


            a = []
            orderdProduct = []
            orderItems = OrderItem.objects.filter(order=order)

            for i in orderItems:
                a = [i.product.name, f'{i.quantity}', i.size, i.get_total,i.product.imageURL]
                orderdProduct.append(a)

            customorder = orderdProduct
            print("Customer Order:   ",customorder)
            name = request.user.username

            # Create a CustomerOrder instance and set the orderItem field
            customerOrder = CustomerOrder(order_by=order, customer_name=name, shipping=shipping, total_tk=total)
            customerOrder.set_two_d_array(customorder)
            customerOrder.save()


            your_order = "<br>"
            for index, item in enumerate(customorder):
                your_order += f'{index+1}: {item[0]}  qty - {item[1]} size - {item[2]} price - {item[3]}tk <br>'

            email_subject = "Your Order is Completed"
            email_body = f"""
    Hi {request.user.customer.name},<br><br>
    We are thrilled to inform you that your order has been successfully processed!<br><br>
    <strong>Your Order Details:</strong><br>

   {your_order}

    <strong>Total Amount:</strong><span> { data['form']['total'] } Tk.<span><br><br>
    <strong>Payment Information:</strong><br>
    Please make the payment at your earliest convenience to ensure a smooth delivery process.<br><br>
    Thank you for choosing us! Your satisfaction is our priority.<br>
    If you have any questions or concerns, feel free to reach out to us on our <a href="https://web.facebook.com/LONGGFASHION">Longg : লং </a>.
    Join our facebook group <a href="https://www.facebook.com/groups/350757722968576/?mibextid=c7yyfP">longg</a> <br><br>
    Best regards,<br>
    Longg : লং <br>
    01323-426706<br>
    https://web.facebook.com/LONGGFASHION
"""


            email = EmailMessage(
                email_subject,
                email_body,
                'faysalhassantorjo8@gmail.com',
                [f'{email}'],
            )
            email.content_subtype = 'html'
            email.send()




    total = float(data['form']['total'])
    order.transaction_id=transaction_id

    if total >= order.get_cart_total:
        order.complete = True
    order.save()
    print('data',data)

   
    return JsonResponse('Payment complete',safe=False)

def register(request):
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['pass']
        password2=request.POST['pass2']

        if password==password2:
            if User.objects.filter(email=email).exists():
                messages.info(request,'Email Already Used')
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.info(request,'Username already exist!!! User different username')
                return redirect('register')
            else:
                user_create=User.objects.create_user(username=username,email=email,password=password)
                user_create.save()
                user=auth.authenticate(username=username,password=password,email=email)
                if user is not None:
                    auth.login(request,user)
                    return redirect('index')
        else:
            messages.info(request,'Password not the same')
            return redirect('register')
    else:
        return render(request,'myapp/register.html')

def login(request):
    if request.method=='POST':
        name=request.POST['name']
        email=request.POST['email']
        pas=request.POST['pass']
        # if User.objects.filter(username=name).exists() and User.objects.filter(password=pas):
        user=auth.authenticate(username=name,password=pas,email=email)
        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,'Password did not match')
            return redirect('login')
    else:
        return render(request,'myapp/login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

@admin_only
def customerOrderView(request):
    orders = CustomerOrder.objects.all().order_by('-date_added')
    for order in orders:
            l = order.get_two_d_array()
            
            print(type(l))
        


    return render(request, 'myapp/customerOrder.html', {'orders': orders})

from django.shortcuts import get_object_or_404
@admin_only
def delete_customer_order(request, pk):
    # Get the CustomerOrder instance to be deleted or return a 404 error if not found
    order = get_object_or_404(CustomerOrder, id=pk)

    if request.method == 'POST':
        # If the request method is POST, it means the user has confirmed the deletion
        order.delete()
        return redirect('customerOrderView')  # Redirect to the list of orders after deletion

    # If the request method is GET, display a confirmation page
    return render(request, 'myapp/delete.html', {'order': order})




def adminPage(request):
    return render(request,'myapp/adminPage.html')


from .form import AddProductForm,AddCategoryForm
def addProduct(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST,request.FILES)
        form.save()
        return redirect('index')
    else:
        form =AddProductForm()
    
    context={
        'form':form,
    }
    return render(request,'myapp/AddProduct.html',context)

def addCategory(request):
    if request.method == 'POST':
        form = AddCategoryForm(request.POST,request.FILES)
        form.save()
        return redirect('index')
    else:
        form =AddCategoryForm()
    
    context={
        'form':form,
        'hi':'hi'
    }
    return render(request,'myapp/AddCategory.html',context)

