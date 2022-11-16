from django.shortcuts import render, redirect
from . import models
from django.http import HttpResponse

import telebot

bot = telebot.TeleBot('5776485376:AAGBeR4Ai0JB_7e2n-Y-__A7WmKhpJvrzco')

# Create your views here.
def index_page(request):
    # If user sends feedback
    if request.method == 'POST':
        mail = request.POST.get('mail')
        feedback = request.POST.get('message')
        
        models.Feedback.objects.create(user_mail=mail, feedback_message=feedback)
        
    
    products = models.Product.objects.all()
    categories = models.Category.objects.all()
    sales = models.Sale.objects.all()
    currency_rate = 11140
    weather = '+32 C'
    
    return render(request, 'index.html', {'products':products, 
                                          'categories':categories,
                                          'sales':sales})


# Function of searching
def search_product(request):
    if request.method == 'POST':
        user_search_product = request.POST.get('search')
        try:
            result_product = models.Product.objects.get(product_name=user_search_product)
            
            return render(request, 'current_product.html', {'result_product': result_product})
        
        except:
            return redirect('/')
        

#Get certain product
def current_product(request, name, pk):
    product = models.Product.objects.get(product_name=name, id=pk)
    
    return render(request, 'current_product.html', {'result_product':product})

# Getting all products from certain category
def current_category(request, pk):
    category = models.Category.objects.get(id=pk)
    category_part = models.Product.objects.filter(product_category=category)

    
    return render(request, 'current_category.html', {'category_part':category_part})
    
# Adding to cart 
def add_product_to_user_cart(request, pk):
    if request.method == 'POST':
        product = models.Product.objects.get(id=pk)
        product_count = float(request.POST.get('count'))
        
        user = models.Cart(user_id=request.user.id, 
                           user_product = product, 
                           product_quantity = product_count,
                           total_for_current_product = product_count * product.product_price)
        
        product.product_quantity -= product_count
        product.save()
        user.save()
        
        return redirect(f'/product/{product.product_name}/{pk}')

# Showing cart    
def show_cart(request):
    cart_product = models.Cart.objects.filter(user_id = request.user.id)
    
    total = sum([i.total_for_current_product for i in cart_product])
    
    return render(request, 'cart.html', {'cart_product': cart_product, 
                                         'total': total})

# Deleting product from cart
def delete_product_from_cart(request, pk):
    if request.method == 'POST':
        product_to_delete = models.Cart.objects.get(id=pk, user_id=request.user.id)
        product = models.Product.objects.get(product_name=product_to_delete.user_product)
        product.product_quantity += product_to_delete.product_quantity
        
        product.save()
        
        product_to_delete.delete()
        
        return redirect('/cart')

# Ordering
def confirm_order(request):
    if request.method == 'POST':
        current_user_cart = models.Cart.objects.filter(user_id=request.user.id)
        
        # Getting values from front part
        client_name = request.POST.get('client_name')
        client_adress = request.POST.get('client_adress')
        client_number = request.POST.get('client_number')
        client_comment = request.POST.get('client_comment')  
        
        # Messages for admin in tg
        full_message = f'New order (from site)\n\nName: {client_name}'\
                       f'\nAdress: {client_adress}'\
                       f'\nPhone number: {client_number}'\
                       f'\nComment about order: {client_comment}\n\n'
        
        for i in current_user_cart:
            full_message += f'Product: {i.user_product}'\
                            f'\nQuantity: {i.product_quantity}'\
                            f'\nSum: {i.total_for_current_product}'



    bot.send_message(268465740, full_message)
    
    return redirect('/')