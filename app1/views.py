from datetime import date, timedelta, datetime
from .models import Product
from django.shortcuts import render
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Contact
from .models import Product, Cart, CartItem
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal
import razorpay
# View function for rendering index page


def index(request):
    products = Product.objects.all()
    return render(request, 'index.html')




def blog(request):

    return render(request, 'blog.html')


# View function for rendering about page
def aboutus(request):
    return render(request, 'about.html')


# View function for rendering contact page and processing form submission
def contact(request):
    if request.method == 'POST':

        # Get values from form submission
        Name = request.POST.get('Cname')
        Email = request.POST.get('Cemail')
        contact_val = request.POST.get('Ccontact')
        Subject = request.POST.get('Csubject')
        Message = request.POST.get('Cmessage')

        # Print form values to console
        print(Name, Email, contact_val, Subject, Message)

        # Add success message for successful form submission
        messages.success(request, 'Your message has Successfully Sent')

        # Save contact details to Contact model
        contact_model = Contact(
            Name=Name, Email=Email, Contact=contact_val, Subject=Subject, Message=Message)
        contact_model.save()

        return render(request, 'contact.html')
    else:

        # Render contact page if request method is not POST
        return render(request, 'contact.html')

# View function for rendering bicycle list page
def bicyclelist(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'bicyclelist.html', context)


# View function for rendering cart page
@login_required
def cart(request):
    cart_items = CartItem.objects.filter(cart__user=request.user)
    context = {'items': cart_items}
    return render(request, 'cart.html', context)


# View function for rendering signup page and processing form submission
def SignupPage(request):
    if request.method == 'POST':

        # Get values from form submission
        uname = request.POST.get('username')
        email = request.POST.get('email')

        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        # Check if passwords match
        if pass1 != pass2:
            messages.error(
                request, 'Your password and confirm password are not Same!!')
        else:

            # Create new user and redirect to login page if passwords match
            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            return redirect('login')
    return render(request, 'signup.html')


# View function for rendering login page and processing form submission
def LoginPage(request):
    if request.method == 'POST':

        # Get values from form submission
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')

        # Authenticate user and redirect to home page
        user = authenticate(request, username=username, password=pass1)
        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in')
            return redirect('home')
        else:

            # Add error message for invalid credentials
            messages.error(request, 'Invalid Credentials')

    return render(request, 'login.html')

# View function for logging out user and redirecting to home page


def LogoutPage(request):
    logout(request)
    return redirect('home')


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    try:
        cart = Cart.objects.get(user=request.user, is_paid=False)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user, is_paid=False)

    cart_item, created = CartItem.objects.get_or_create(
        product=product, cart=cart)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    # Save the product image and price to the cart item
    if product.image:
        cart_item.image = product.image
    # set default value for price
    cart_item.price = product.product_price if product.product_price else 0
    cart_item.save()

    return redirect('cart')


def invoice(request):
    cart_items = CartItem.objects.filter(cart__user=request.user)

    total_price_security = sum(item.product.product_price * item.quantity for item in cart_items)
    context = {
       
        'total_price_security': total_price_security,
        'items': cart_items,
        
    }

    return render(request, 'invoice.html', context)


def calculate_total_price(cart_items):
    total_price = sum(item.product.product_price *
                      item.quantity for item in cart_items)
    total_price = Decimal(total_price).quantize(Decimal('.01'))
    return total_price


@login_required(login_url='/accounts/login/')
def cart(request):
    try:
        cart = Cart.objects.get(user=request.user, is_paid=False)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user, is_paid=False)

    cart_items = cart.cartitem_set.all()

    total_price = sum(item.product.product_price * item.quantity for item in cart_items)
    total_price_security = total_price
    cart.price_paid = total_price_security
    cart.save()
    razor_amount = int(total_price_security) * 100

    context = {
        'items': cart_items,
        'total_price_security': total_price_security,
        'total_price': total_price,
        'razor_amount': razor_amount,
    }

    return render(request, 'cart.html', context)



def clear_cart(request):
    cart_items = CartItem.objects.filter(cart__user=request.user)
    cart_items.delete()
    messages.success(request, 'Cart has been cleared successfully!')
    return redirect('cart')


def delete_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def product_list(request):
    # Retrieve all products from the database
    products = Product.objects.all()

    # Define a function to sort the products based on selected criteria
    def sort_products(sort_by):
        if sort_by == 'price-asc':
            return products.order_by('product_price')
        elif sort_by == 'price-desc':
            return products.order_by('-product_price')
        elif sort_by == 'avail-asc':
            return products.order_by('product_quantity')
        elif sort_by == 'avail-desc':
            return products.order_by('-product_quantity')
        else:
            return products

    # Get the selected sort criteria from the request
    sort_by = request.GET.get('sort-by', 'price-asc')

    # Sort the products based on the selected criteria
    products = sort_products(sort_by)

    # Pass the sorted products to the HTML template
    context = {'products': products, 'sort_by': sort_by}

    return render(request, 'bicyclelist.html', context)
