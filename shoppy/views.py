import json
import os

import sweetify
from androidAuthApi.models import ShortCode
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, Max
from django.http import JsonResponse
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.contrib.auth import authenticate, logout, login, get_user_model
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import africastalking
from django.views.decorators.csrf import csrf_exempt
from requests import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


from .forms import *


# Create your views here.

# # Base method with no type specified
# sweetify.sweetalert(self.request, 'Westworld is awesome', text='Really... if you have the chance - watch it!' persistent='I agree!')
#
# # Additional methods with the type already defined
# sweetify.info(self.request, 'Message sent', button='Ok', timer=3000)
# sweetify.success(self.request, 'You successfully changed your password')
# sweetify.error(self.request, 'Some error happened here - reload the site', persistent=':(')
# sweetify.warning(self.request, 'This is a warning... I guess')




def search(request):

    if request.method=="POST":
        search_text = request.POST['search_text']
        print(search_text)
    else:
        search_text =""

    products = Product.objects.filter(name__contains=search_text, status='VERIFIED' )
    context={
        'products': products,
        'search_text': search_text,
    }
    return render_to_response('shoppy/search.html',context)

def placeholder(request):

    product =Product.objects.order_by("?").first()
    context={
        'product':product.name,
    }
    return JsonResponse(context)

def home(request):
    user = request.user
    carousels =Carousel.objects.order_by("-created_at")
    brand = Brand.objects.order_by('?').last()
    category = Category.objects.order_by('?').first()
    products = Product.objects.order_by("?")
    featured_products = Product.objects.filter(feat_product='FEATURED', status='VERIFIED')
    products_all = Product.objects.filter(status='VERIFIED').order_by('?')
    # brand_products_greater_than_14 = Product.objects.filter(bra)
    wishlist_count = Wishlist.objects.filter(buyer_id=request.user.id).count()

    side_carousel_product = Product.objects.order_by("?")
    if Product.objects.filter(category_id=category.id).order_by("?").count() >= 18:
        brand_products = Product.objects.filter(category_id=category.id).order_by("?")
    else:
        brand_products = Product.objects.order_by("-created_at")

    # mod = os.path.dirname(__file__)
    # file = os.path.join(mod, 'county.json')
    #
    # with open(file) as f:
    #     print()
    #     data = f.read()
    #     # print(data.split('¿', 1)[1])
    #     json_data = json.loads(data.split('¿', 1)[1])
    #
    #     for p in json_data:
    #         County.objects.create(
    #            number=p['county_number'],
    #            name=p['county']
    #
    #         )
            # print(p['county_number'], p['county'])


    context ={
        'title':'Mashkys',
        'user': user,
        'carousels' : carousels,
        'featured_products': featured_products,
        # 'products': products,
        'product_brands':brand_products,
        'productsaz':products_all,
        'wishlist_count':wishlist_count,
        'brand':brand,
        'side_carousel_product':side_carousel_product,
        # 'categories':categories,
        # 'orderproducts': orderproducts
    }
    return render(request, 'shoppy/home.html', context)




@csrf_exempt
@login_required()
def addToWishlist(request):
    if request.method=="POST" and request.is_ajax():
        product_id = request.POST.get("product_id")

        product = Product.objects.filter(id=product_id).first()
        buyer = Buyer.objects.filter(user_ptr_id=request.user.id).first()

        order = Order_Product.objects.filter(product=product, buyer=buyer, checkout__isnull=True).first()
        if not Wishlist.objects.filter(buyer=buyer, product=product).exists():

            order.delete()
            Wishlist.objects.create(
                buyer=buyer,
                product=product
            )

            context={
                "results":"add_success",
                "wishlist_count": Wishlist.objects.filter(buyer=buyer).count(),
                "message": 'Added successfully',
            }
        else:
            wishlist = Wishlist.objects.filter(buyer=buyer, product=product).first()
            wishlist.delete()
            context = {
                "results": "deleted_success",
                "wishlist_count": Wishlist.objects.filter(buyer=buyer).count(),
                "message": 'Wish Removed successfully',
            }
        return JsonResponse(context)


@login_required()
def unWishProduct(request, wishlist_id, source):
    buyer = Buyer.objects.filter(user_ptr_id=request.user.id).first()
    wishlist = Wishlist.objects.filter(id=wishlist_id)
    if buyer is not None:
        wishlist.delete()
        sweetify.success(request,  'Your Wish Have Been Removed', button='ok', timer=3000)
        # messages.success(request, '')
    source = source.replace('____', '/')
    return redirect(source)


@login_required()
def unWish_All_Products(request):
    buyer = Buyer.objects.filter(user_ptr_id=request.user.id).first()
    wishlist = Wishlist.objects.all().filter(buyer_id=request.user.id)
    if buyer is not None:

        wishlist.delete()
        sweetify.success(request,  'All Your Wishes Have Been Removed',
button='ok', timer=3000)
        # messages.success(request, '')
    return redirect('Shoppy:shoppy-user_account')

# cart
def cart(request):

    if request.method == 'GET':
        cookie = request.COOKIES.get('Mashkys', False)
        mash_cookie = MashCartCookie.objects.filter(mashcookie__exact=cookie).first()
        # print(mash_cookie)
        order_varianto = OrderProductVariantOption.objects.all()
        buyer =  Buyer.objects.filter(user_ptr_id=request.user.id).first()
        if request.user.is_authenticated:
            carts = Order_Product.objects.filter(buyer=buyer , checkout__isnull=True)
        else:
            carts = Order_Product.objects.filter(session=mash_cookie, checkout__isnull=True, buyer_id__isnull=True ).all()


        total = 0
        for order_product in Order_Product.objects.filter(session=mash_cookie, checkout_id__isnull=True):
            total += float(order_product.total)





        context = {
            'carts' :carts,
            'title': 'Shoppy-Cart',
            'ordervarianto': order_varianto,
            'buyer':buyer,
            'total':total,
        }
        return render(request, 'shoppy/cart.html', context)




def addCart(request, source):
    source = source.replace('____', '/')
    buyer = Buyer.objects.filter(user_ptr_id=request.user.id).first()
    if request.method == 'POST':

        quantity = request.POST.get('quantity')
        product_id = request.POST.get('product')
        cookie_data = request.POST.get('cookie')
        total = (float(request.POST.get('unit_cost')) * int(quantity))
        request.POST = request.POST.copy()
        request.POST['buyer'] = buyer
        options = request.POST.getlist('variant_options[]')
        if not request.user.is_authenticated:
            product = Product.objects.filter(id=product_id).first()
            if not MashCartCookie.objects.filter(mashcookie__iexact=cookie_data).exists():
                newmashCookie = MashCartCookie.objects.create(
                    mashcookie=cookie_data,
                )
                orderProduct =Order_Product.objects.create(
                    product_id=product.id,
                    total=total,
                    quantity=quantity,
                    session=newmashCookie,
                )
                if options is not None:
                    for variantoption in options:
                        variant_option = Variant_Option.objects.filter(id=variantoption).first()
                        OrderProductVariantOption.objects.create(
                            variantOptions=variant_option,
                            orderProduct=orderProduct,
                        )
                sweetify.success(request, title='Success' 'Product Added To Cart', button='ok', timer=3000)
                return redirect(source)

            else:
                existingmashcookie = MashCartCookie.objects.filter(mashcookie__iexact=cookie_data).first()
                if not Order_Product.objects.filter(session=existingmashcookie , product=product).exists():
                    orderProduct =Order_Product.objects.create(
                        product_id=product.id,
                        total=total,
                        quantity=quantity,
                        session=existingmashcookie,
                    )
                    if options is not None:
                        for variantoption in options:
                            variant_option = Variant_Option.objects.filter(id=variantoption).first()
                            OrderProductVariantOption.objects.create(
                                variantOptions=variant_option,
                                orderProduct=orderProduct,
                            )

                    sweetify.success(request, title='Success' 'Product Added To Cart', button='ok', timer=3000)
                    return redirect(source)
                else:
                    sweetify.error(request, title='Erroe' 'Error Adding Product To Cart', button='ok', timer=3000)
                    return redirect(source)

        else:
            product = Product.objects.filter(id=product_id).first()
            orderProduct = Order_Product.objects.create(
                product=product,
                buyer=buyer,
                quantity=quantity,
                total=total,
            )
            if options is not None:
                for variantoption in options:
                    variant_option = Variant_Option.objects.filter(id=variantoption).first()
                    OrderProductVariantOption.objects.create(
                        variantOptions=variant_option,
                        orderProduct=orderProduct,
                    )
            sweetify.success(request,  'Product Added To Cart', button='ok', timer=3000)
            source = source.replace('____', '/')
            return redirect(source)



    return redirect(source)

def deleteCartProduct(request, order_id):
    cart_product = Order_Product.objects.filter(id=order_id).first()
    cart_product.delete()
    return redirect("Shoppy:shoppy-cart")


def productDetails(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    images = Image.objects.filter(product= product_id)
    review_images = Image.objects.filter(product=product_id)[:2]
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    product_carts = Product.objects.filter(id=product_id)
    similar_products= Product.objects.filter( product_brand=product.product_brand)
    buyer = Buyer.objects.filter(user_ptr_id=request.user.id).first()
    buyers_count = []
    buyer_total_ratin = Review.objects.filter(product=product)
    for review in buyer_total_ratin:
        buyers_count.append(review.buyer)

    if request.method == 'POST':
        ratings = request.POST.get('ratings', False)
        comments = request.POST['comments']
        productt = request.POST['product']
        product = Product.objects.filter(id=productt).first()
        Review.objects.create(
            buyer=buyer,
            product=product,
            ratings=ratings,
            comments=comments,
        )
        sweetify.success(request, title='Success' 'Your Review Was Taken', button='ok', timer=3000)

    # sweetify.error(request, title='Error' 'You Can Only Review Products You Have Bought ', button='ok', timer=5000)


    context={
        'product' : product,
        'images' : images,
        'review_images': review_images,
        'similar_products':similar_products,
        'product_carts': product_carts,
        'reviews': reviews,
        'countratin':len(list(set(buyers_count)))

    }

    return render(request, 'shoppy/product_details.html',context)

def productsList(request, category_id):
    # products = Product.objects.filter(status='VERIFIED')
    if category_id == 100000:
        products = Product.objects.filter(status='VERIFIED').order_by('-unit_cost')
    else:

        category= Category.objects.filter(id=category_id).first()
        products= Product.objects.filter(status='VERIFIED', category_id=category.id).order_by('-unit_cost')
    max_cost = Product.objects.order_by('-unit_cost').values('unit_cost').first()['unit_cost']
    context={
        'products':products,
        'categories':Category.objects.filter(parent_id__isnull=True).order_by('name'),
        'brands':Brand.objects.all(),
        'max_cost':max_cost,


    }

    return render(request, 'shoppy/view_products/all_category_products.html', context)
@csrf_exempt
def allcategoryproductsList(request):
    if request.method == "POST":
        category = request.POST.get('category')
        brand = request.POST.get('brand')
        unit_cost_from = request.POST.get('unit_cost_from')
        unit_cost_to = request.POST.get('unit_cost_to')

        filter_category = Category.objects.filter(id=category).first()
        filer_brand = Brand.objects.filter(id=brand).first()
        print(unit_cost_from, unit_cost_to, category, brand)
        if category is not None and brand is not None and unit_cost_from is not None and unit_cost_to is not None:
            products = Product.objects.filter(
                Q(category=filter_category) | Q(product_brand=filer_brand) | Q(status='VERIFIED') | Q(
                    unit_cost__range=[int(unit_cost_from), int(unit_cost_to)]))
            print('one')
            # print(products)

        elif category is not None and brand is not None:
            products = Product.objects.filter(Q(category=filter_category), Q(product_brand=filer_brand),
                                              Q(status='VERIFIED'),
                                              Q(unit_cost__range=[int(unit_cost_from), int(unit_cost_to)]))
            print('three')
            # print(products)
        elif brand is not None and unit_cost_from is not None and unit_cost_to is not None:
            products = Product.objects.filter(Q(product_brand=filer_brand), Q(status='VERIFIED'),
                                              Q(unit_cost__range=[int(unit_cost_from), int(unit_cost_to)]))
            print('four')
            # print(products)
        elif category is not None and unit_cost_from is not None and unit_cost_to is not None:
            products = Product.objects.filter(Q(category=filter_category), Q(status='VERIFIED'),
                                              Q(unit_cost__range=[int(unit_cost_from), int(unit_cost_to)]))
            print('five')
            # print(products)
        elif category is not None:
            products = Product.objects.filter(Q(category=filter_category), Q(status='VERIFIED'),
                                              Q(unit_cost__range=[int(unit_cost_from), int(unit_cost_to)]))
            print('six')
            # print(products)
        elif brand is not None:
            products = Product.objects.filter(Q(product_brand=filer_brand), Q(status='VERIFIED'),
                                              Q(unit_cost__range=[int(unit_cost_from), int(unit_cost_to)]))
            print('seven')
            # print(products)
        elif unit_cost_to is not None and unit_cost_from is not None:
            products = Product.objects.filter(Q(status='VERIFIED'),
                                              Q(unit_cost__range=[int(unit_cost_from), int(unit_cost_to)]))
            print('two')
            # print(products)

        max_cost = Product.objects.order_by('-unit_cost').values('unit_cost').first()['unit_cost']
        # print(products)
        context = {
            'products': products,
            'categories': Category.objects.filter(parent_id__isnull=True).order_by('name'),
            'brands': Brand.objects.all(),
            'max_cost': int(max_cost),
            'min_cost': 0,

        }
        # return TemplateResponse(request, "shoppy/view_products/filtered_products.html", context)
        # return render_to_response('shoppy/view_products/filtered_products.html',context)
        return render(request, 'shoppy/view_products/all_category_products.html', context)

    else:
        products= Product.objects.filter(status='VERIFIED').order_by('-unit_cost')
        context = {
            'products': products,
            'categories': Category.objects.all(),
            'brands': Brand.objects.all(),
            'max_cost': int(Product.objects.order_by('-unit_cost').values('unit_cost').first()['unit_cost']),
            'min_cost': 0,

        }
        return render(request, 'shoppy/view_products/all_category_products.html', context)


@csrf_exempt
def product_filter(request):

    return render(request, 'shoppy/view_products/all_products.html')

# def productReview(request):
#     buyer = Buyer.objects.filter(user_ptr_id=request.user.id).first()
#     if buyer is not None:
#         if request.method == 'POST':
#             ratings = request.POST.get('ratings', False)
#             comments = request.POST['comments']
#             productt = request.POST['product']
#             product = Product.objects.filter(id=productt).first()
#             Review.objects.create(
#                 buyer=buyer,
#                 product=product,
#                 ratings=ratings,
#                 comments=comments,
#             )
#             sweetify.success(request, title='Success' 'Your Review Was Taken', button='ok', timer=3000)
#             return redirect("Shoppy:shoppy_product_details")
#     sweetify.error(request, title='Error' 'You Can Only Review Products You Have Bought ', button='ok', timer=5000)
#     return redirect("Shoppy:shoppy_product_details")

# def user_account_product(request, product_id):
#     similar =Product.objects.filter(id=product_id).first()
#     product = Product.objects.filter(product_brand=similar.product_brand)
#     context={
#         'product':product,
#     }
#     return render(request, 'shoppy/user_account.html', context)

@login_required()
def user_account(request):
    user = request.user
    buyer = Buyer.objects.filter(user_ptr_id=user.id).first()
    seller = Seller.objects.filter(user_ptr_id=user.id).first()
    wishlist = Wishlist.objects.filter(buyer_id=request.user.id)


    if buyer is not None:
        logged_in_user = 'buyer'
    elif seller is not None:
        logged_in_user = 'seller'

    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone_number = request.POST['phone_number']
        if buyer is not None:
            user = User.objects.get(pk=request.user.id)
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.save()
            Buyer.objects.filter(user_ptr_id = user.id).update(
                phone_number = phone_number,
            )
            sweetify.success(request, title='Success' 'Account Updated', button='ok', timer=5000)
    context ={
        'user': logged_in_user,
        'wishlist': wishlist,
        'orders': Order_Product.objects.filter(buyer=buyer, checkout__isnull=False, checkout__status='PAID'),
        'buyer' : Buyer.objects.filter(user_ptr_id=user.id).first(),
    }
    return render(request,'shoppy/user_account.html',context)




def buyer_register(request):
    # user= request.user

    if request.method == 'POST':
        username =request.POST['username']
        form = BuyerSignUpForm(request.POST)
        print(form)
        if form.is_valid():
            new_form = form.save()
            # user = User.objects.filter(id=n)
            Buyer.objects.filter(user_ptr_id=new_form.id).update(
                phone_number = username,
            )
            sweetify.success(request, 'Buyer Registered Successfully, Now Log In', persistent='Continue', timer=3000)
            return redirect('Shoppy:shoppy-login')
        else:
            form1 = BuyerSignUpForm(request.POST)
            sweetify.error(request, 'Error', text='Ensure you fill all fields correctly', persistent='Retry', timer=3000)
            return render(request,"shoppy/buyer-registration.html", {'form':form1})
    else:
        form2 = BuyerSignUpForm()
    context={
        'form': form2,
    }
    return  render(request,"shoppy/buyer-registration.html",context)
    # return redirect('Shoppy:shoppy-buyer-reg',context)


def user_login(request):
    # messages = []
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        mashcookie = request.COOKIES.get('Mashkys', False)


        def buyerusername(phone_number):
            uz= Buyer.objects.filter(phone_number=phone_number).first()
            if uz:
                usename = User.objects.filter(id=uz.user_ptr_id).first()
                if uz.phone_number:
                    return usename.username
                return None
        def sellerusername(email):
            # uz = User.objects.filter(email__exact=email).first()
            uz= Seller.objects.filter(Q(email__exact=email) | Q(username__exact=email)).first()
            usename = User.objects.filter(id=uz.id).first()
            if uz.email:
                return usename.username
            return None
        def adminusername(username):
            uzer=User.objects.filter(Q(username__exact=username) | Q(email__exact=username)).first()
            if uzer:
                return uzer.username
            return None




        if  User.objects.filter(Q(username__exact=username)|Q(email__exact=username)).first() or \
            Buyer.objects.filter(phone_number__exact=username).first() or \
            Seller.objects.filter(Q(email__exact=username)|Q(username__exact=username)).first():
            if Buyer.objects.filter(Q(phone_number__exact=username) | Q(username__exact=username)).first():
                user = authenticate(username=buyerusername(username), password=password)
                if user is not None:
                    if user.is_active:
                        if Buyer.objects.filter(user_ptr_id=user.id).exists():
                            buyer1 = Buyer.objects.filter(user_ptr_id=user.id).first()
                            login(request, user)
                            mashcookie1 = MashCartCookie.objects.filter(mashcookie__exact=mashcookie).first()
                            if mashcookie1 is not None:
                                Order_Product.objects.filter(session=mashcookie1, buyer_id__isnull=True).update(
                                    buyer=buyer1,
                                )
                                sweetify.success(request, 'Success', text='Welcome Back You Can Proceed To Checkout', persistent='OK')
                                return redirect('Shoppy:shoppy-cart')

                            sweetify.success(request, 'Success', text='Welcome to Mashkys', persistent='Continue')
                            return redirect('Shoppy:shoppy-home')
                    else:
                        sweetify.error(request, 'Error', text='Your account has been Deactivated!',
                                       persistent='Retry')
                        return render(request, 'shoppy/login.html')
                else:
                    sweetify.error(request, 'Error', text='Invalid login credentials', persistent='Retry')
                    return render(request, 'shoppy/login.html')
            if Seller.objects.filter(Q(email__exact=username) | Q(username__exact=username)).first():
                user = authenticate(username=sellerusername(username), password=password)
                if user is not None:
                    if user.is_active:
                        if Seller.objects.filter(user_ptr_id=user.id).exists():
                            if Seller.objects.filter(user_ptr_id=user.id, status="VERIFIED").exists():
                                login(request, user)
                                sweetify.success(request, 'Success', text='Welcome to Mashkys', persistent='Retry')
                                return redirect('ShoppyAdmin:shoppy-admin-home')
                            else:
                                sweetify.error(request, 'Error',
                                               text='It Seems That Your Account Has Been Deactivated: Contact The Admin For More Info',
                                               persistent='Retry')
                                return render(request, 'shoppy/login.html')
                    else:
                        sweetify.error(request, 'Error', text='Your account has been Deactivated!',
                                       persistent='Retry')
                        return render(request, 'shoppy/login.html')
                else:
                    sweetify.error(request, 'Error', text='Invalid login credentials', persistent='Retry')
                    return render(request, 'shoppy/login.html')
            if User.objects.filter(Q(username__exact=username)|Q(email__exact=username) and Q(is_superuser=True)).first():
                user = authenticate(username=adminusername(username), password=password,)
                if user is not None:
                    if user.is_staff and user.is_active:
                        login(request, user)
                        sweetify.success(request, 'Success', text='Welcome Admin',persistent='Continue')
                        return redirect('ShoppyAdmin:shoppy-admin-home')
                    else:
                        sweetify.error(request, 'Error', text='Please Retry', persistent='Retry')
                        return render(request, 'shoppy/login.html')
                else:
                    sweetify.error(request, 'Error', text='Invalid login credentials', persistent='Retry')
                    return render(request, 'shoppy/login.html')

        else:

            sweetify.error(request, 'Error', text='Invalid user credentials', persistent='Continue')

    return render(request,"shoppy/login.html")



def logout_view(request):
    logout(request)
    return redirect('Shoppy:shoppy-login')

def seller_register(request):

    if request.method == 'POST':
        form = SellerSignUpForm(request.POST, request.FILES)
        # print(form)
        if form.is_valid():
            form.save()
            sweetify.success(request, 'Success', text='Seller Registered Successfully, You Will Be Notified When Your Account Is Activated', persistent='Continue')
            return redirect('Shoppy:shoppy-login')
        else:
            form = SellerSignUpForm(request.POST, request.FILES)
            sweetify.error(request, 'Error', text='Error Registering, ensure all your details are field correctly', persistent='Retry')
            # return redirect('shoppy/seller_registration.html')
            return render(request,'shoppy/seller_registration.html',{'form':form,'counties': County.objects.order_by('-number'),})

    # kenyan_county_api_url = "https://raw.githubusercontent.com/mikelmaron/kenya-election-data/master/data/counties.geojson"
    # data = requests.get(kenyan_county_api_url).json()
    #
    # for county in data['features']:
    #     County.objects.create(
    #         name=county['properties']['COUNTY_NAM'],
    #         number=county['properties']['COUNTY_COD'],
    #     )
    context = {
        'counties': County.objects.order_by('-number'),
    }

    return render(request, 'shoppy/seller_registration.html', context)


# def seller_home(request):
#     user = request.user
#     seller = Seller.objects.filter(user_ptr_id=user.id).first()
#     return render(request, 'shoppy_seller/sellerhome.html', {'seller':seller})

def checkout(request):
    buyer = Buyer.objects.filter(user_ptr_id=request.user.id).first()
    # print(buyer.)
    regions= Region.objects.order_by('-name')
    carts = Order_Product.objects.filter(buyer_id=buyer.id ,checkout__isnull=True)

    total = 0
    for order_product in Order_Product.objects.filter(buyer_id=buyer.id , checkout_id__isnull=True):
        total += float(order_product.total)
    # voucher_buyer = Voucher_Buyer.objects.filter(bu)
    voucher = Voucher.objects.filter(end_time__gt=datetime.datetime.today(), no_of_users__gt=0)


    # print(buyer)
    context={
        'buyer':buyer,
        'regions': regions,
        'carts':carts,
        'total':total,
        'voucher':voucher,
    }
    return render(request, 'shoppy/checkout.html', context)

def confirmCheckout(request):
    buyer = Buyer.objects.filter(user_ptr_id=request.user.id).first()
    if request.method =="POST":
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        region_id=request.POST.get('region')
        address=request.POST.get('address')
        voucher=request.POST.get('voucher', False)
        total=request.POST['total']
        phonenumber= request.POST['phone_number']
        reference_code =('M'+ get_random_string(length=4, allowed_chars='ABCDEFGHIJLNPQRSTUVWXYZ123456789'))
        region = Region.objects.filter(id=region_id).first()


        new_total1 = (float(total) + region.region_cost)


        if not User.objects.filter(id=request.user.id, last_name__iexact=last_name, first_name__iexact=first_name).exists():
            User.objects.filter(id = request.user.id).update(
                first_name=first_name,
                last_name=last_name,
            )
        checkout = Checkout.objects.create(
            buyer=buyer,
            reference_code = reference_code,
            total = float(new_total1),
            phonenumber = phonenumber,
            delivery=region,
            address=address,
        )

        if checkout is not None:
            checkoutt = Checkout.objects.filter(id=int(checkout.id)).first()
            buyerr = Buyer.objects.filter(user_ptr_id=request.user.id).first()
            Order_Product.objects.filter(buyer=buyerr, checkout__isnull=True).update(
                buyer=buyer,
                checkout=checkoutt,
            )
            if voucher is not None:
                if Voucher.objects.filter(code__exact=voucher,end_time__gt=datetime.datetime.today(), no_of_users__gt=0).exists():
                    if not Voucher_Buyer.objects.filter(buyer=buyer, voucher__code__exact=voucher).exists():
                        voucher = Voucher.objects.filter(code__exact=voucher).first()
                        voucher_amount = voucher.amount
                        checkout_total = checkoutt.total
                        new_total = float(checkout_total-float(voucher_amount))
                        Checkout.objects.filter(id=checkoutt.id).update(
                            total=new_total,
                        )
                        Voucher_Buyer.objects.create(
                            voucher=voucher,
                            buyer=buyer
                        )
                        new_no_of_users = (voucher.no_of_users - 1)
                        Voucher.objects.filter(id=voucher.id).update(
                            no_of_users=new_no_of_users,
                        )
                    else:
                        sweetify.success(request, title='Error' ' It Seams You Have Already Used The Voucher, But Your Order Was Taken You Will Be Notified If It Is Ready.', button='Retry', timer=5000)
                        return redirect("Shoppy:how_to_pay")


        sweetify.success(request, title='Success' 'Order Taken You Will Be Notified If Its Ready', button='Continue', timer=5000)
    else:
        sweetify.error(request, title='Error' 'Error taking your order', button='Retry', timer=5000)

    return redirect("Shoppy:how_to_pay")

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            sweetify.success(request, title='Sucess' 'Your password was successfully updated!', button='ok', timer=5000)
            # messages.success(request, '')
            return redirect('Shoppy:shoppy-user_account')
        else:
            sweetify.error(request, title='Error' 'Please correct the error in the form', button='ok', timer=5000)
            # messages.error(request, '')
    else:
        form = PasswordChangeForm(request.user)

    return render(request,'shoppy/user_account.html', {
        'form': form
    })





def how_to_pay(request):
    user = request.user.id
    buyer = Buyer.objects.filter(user_ptr_id=user).first()
    checkout_id = Checkout.objects.filter(buyer=buyer).order_by('-id').first()
    order_total =  Order_Product.objects.filter(buyer=buyer, checkout_id__exact=checkout_id )

    context={
        'order_total':order_total,
        'checkout':checkout_id,
    }
    return render(request,'shoppy/how_to_pay.html',context)





def getShortcode(request):
    # Initialize SDK
    if request.method == 'POST':
        try:
            username = "Mashkys"  # use 'sandbox' for development in the test environment
            api_key = "652230d338f11fd49333722a8acba0161942b5b3efb880caf2fb21958e4fdde4"  # use your sandbox app API key for development in the test environment
            africastalking.initialize(username, api_key)
            random_code = get_random_string(length=6, allowed_chars='123456789')
            phonenumber = request.POST.get("phone_number")
            # appKey = request.data.get("appSignature")
            new_phone_number = f"{254}{phonenumber[-9:]}"
            # print(new_phone_number)
            short_code = ShortCode.objects.create(

                phone_number=phonenumber,
                short_code=random_code,
            )
            # Initialize a service e.g. SMS
            sms = africastalking.SMS
            # Use the service synchronously
            response = sms.send("<#> Your MASHKYS code is:" + random_code, ["+" + new_phone_number], "MASHKYS")
            context = {
                'results': 'success',
                'response': "We have text you pin for setting your password, if an account exists with the phonenumber you entered You should receive an SMS shortly. If you don't receive an email, please make sure you've entered the phonenumber you registered with "

            }
            # sweetify.success(request, title='Success' 'Check your phone for a code we have sent to your and key it into the number pad below. ', button='ok')
        except:
            print('NO INTERNET')
            context = {
                'results': 'error',
                'response': "No Internet "

            }

        return JsonResponse(context, safe=False)
    # return render(request, 'shoppy/registration/password_reset_done.html', context)

def password_resett(request):
    return render(request, 'shoppy/registration/password_reset.html')


def pin_confirmm(request):
    return render(request, 'shoppy/registration/password_reset_done.html')
def new_pin(request):

    return render(request, 'shoppy/registration/password_reset_confirm.html')

def verifyCode(request):
    if request.method == 'POST':
        short_code = request.POST.get("short_code")
        db_short_code = ShortCode.objects.filter(short_code=short_code).order_by('-created_at')[0]
        phoneno = db_short_code.phone_number
        if ShortCode.objects.filter(phone_number = phoneno, short_code = short_code).exists():
           print(db_short_code)
           db_short_code.delete()
           # sweetify.success(request, title='Success' 'Change your pin now!. ',
           #                  button='ok', timer=5000)

           # redirect('Shoppy:new_pin',title='Success' 'Change your pin now!. ',
           #                  button='ok', timer=5000)
           context = {
               'results': 'success',
               'response': 'Change your pin now',
               'phone_number': phoneno,
           }
           return JsonResponse(context, safe=False)

        else:
            print('error')
            context = {
                'results': 'error',
                'response': 'Wrong Short Code Please Retry'
            }
            return JsonResponse(context, safe=False)
    context = {
        'response': 'Wrong Short Code'
    }
    return JsonResponse(context, safe=False)

def verifypassword(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            u = User.objects.get(username__exact=phone_number)
            u.set_password(password1)
            u.save()
            context = {
                'results':'success',
                'response': 'You have successfuly changed your pin. You can log in Now'
            }
            return JsonResponse(context, safe=False)
        else:
            context = {
                'results':'error',
                'response': 'Pin dont match'
            }
            return JsonResponse(context, safe=False)

    context = {
        'response': ''
    }
    return JsonResponse(context, safe=False)
def deleteme(request):
    user = request.user
    carousels = Carousel.objects.order_by("-created_at")
    brand = Brand.objects.order_by('?').first()
    products = Product.objects.order_by("?")
    featured_products = Product.objects.filter(feat_product='FEATURED', status='VERIFIED')
    products_all = Product.objects.filter(status='VERIFIED').order_by('?')
    wishlist_count = Wishlist.objects.filter(buyer_id=request.user.id).count()

    context = {
        'title': 'Shoppy-Home',
        'user': user,
        'carousels': carousels,
        'featured_products': featured_products,
        # 'products': products,
        'products': products_all,
        'wishlist_count': wishlist_count,
        # 'brand':brand,
        # 'categories':categories,
        # 'orderproducts': orderproducts
    }
    return render(request, 'shoppy/deleteme.html', context)


@login_required()
def addToWishlist2(request, product_id, source):

    product = Product.objects.filter(id=product_id).first()
    buyer = Buyer.objects.filter(user_ptr_id=request.user.id).first()
    print(buyer)
    print(product)
    order = Order_Product.objects.filter(product=product, buyer=buyer, checkout__isnull=True).first()
    if not Wishlist.objects.filter(buyer=buyer, product=product).exists():
        order.delete()
        Wishlist.objects.create(
            buyer=buyer,
            product=product
        )

        sweetify.success(request, 'Added successfully', timer=3000)
    else:
        wishlist = Wishlist.objects.filter(buyer=buyer, product=product).first()
        wishlist.delete()
        sweetify.success(request, title='Success' 'Wish Removed', button='ok', timer=5000)



    source = source.replace('____', '/')
    return redirect(source)

@csrf_exempt
def check_voucher_if_it_exists(request):
    if request.method == 'POST' and request.is_ajax():
        voucher_value = request.POST.get('voucher')
        voucher = Voucher.objects.filter(code__iexact=voucher_value).first()
        buyer = Buyer.objects.filter(user_ptr_id=request.user.id).first()

        if voucher is not None:
            if not Voucher_Buyer.objects.filter(buyer=buyer, voucher=voucher).exists():
                context={
                    'results':'valid',
                    'response':'Thank You For Using This Voucher'
                }
            else:
                context = {
                    'results': 'invalid',
                    'response': 'It Seems You Have Used This Voucher You Wont Get The Offer'
                }
        else:
            context = {
                'results': 'invalid_voucher',
                'response': 'Voucher Does not exist'
            }

    return JsonResponse(context)


def all_buyers_orders(request):
    checkouts = Checkout.objects.filter(status__exact='PENDING').order_by('-created_at')
    print(checkouts)
    context ={
        'checkouts':checkouts,
    }
    return render(request, 'shoppy/buyersorders.html', context)


def orders_payment_opions(request, checkout_id):
    user = request.user.id
    buyer = Buyer.objects.filter(user_ptr_id=user).first()
    checkout = Checkout.objects.filter(buyer=buyer, id=checkout_id).first()
    order_total = Order_Product.objects.filter(buyer=buyer, checkout=checkout)

    context = {
        'order_total': order_total,
        'checkout': checkout,
    }
    return render(request, 'shoppy/buyerorderpaymentdetails.html', context)



def all_buyers_order_products(request, reference_code):
    user = request.user.id
    buyer = Buyer.objects.filter(user_ptr_id=user).first()
    orders = Order_Product.objects.filter(checkout__reference_code__exact=reference_code)
    print(orders)
    procucts = []
    for order in orders:
        procucts.append(order.product)
    print(procucts)
    context = {

        'products':procucts,
    }
    return render(request, 'shoppy/view_products/buyer_pending_checkout_products.html', context)