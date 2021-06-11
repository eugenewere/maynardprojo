from shoppy.models import Buyer, Category, Product, Order_Product, Wishlist, Checkout, Region, Product_Variant_Options
from shoppy.models import Variant_Option, Variant, Carousel, Review, Image, OrderProductVariantOption, Brand, Offer
from .serializers import buyersSerializer, CategorySerializer, ProductSerializer, OrderProductSerializer, ParentVariantSerializer
from .serializers import  AllProductsSerializer, AndroidProductSerializer, CustomCartSerializer, wishlistSerializer, CustomWishlistSerializer
from .serializers import RegionSerializer, CheckoutSerializer, VariantOptionsSerializer, CustomVariantsSerializer, VariantsSerializer
from .serializers import CarouselSerializer, ReviewSerializer, ImageSerializer, CartVariantSerializer, BrandSerializer
from .models import ShortCode
from shoppy.models import Voucher, Voucher_Buyer
from rest_framework import generics
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_201_CREATED
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, FloatField, IntegerField, CharField, Value, DateTimeField
from django.utils.crypto import get_random_string
from datetime import datetime
from django.utils import timezone
import pytz
import datetime
import africastalking


# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404


class UserList(generics.ListAPIView):
    queryset = Buyer.objects.all()
    serializer_class = buyersSerializer
    permission_classes = [IsAuthenticated]

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Buyer.objects.all()
    serializer_class = buyersSerializer

class CategoryList(generics.ListAPIView):
    queryset = Category.objects.filter(parent_id__isnull=True)
    serializer_class = CategorySerializer

class UnfilteredCategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class AllProductList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = AllProductsSerializer


class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class WishList(generics.ListAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = wishlistSerializer

class RegionList(generics.ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

class RegionList(generics.ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer    
 

class ProductDetails(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    # def get_queryset(self):
    #     category = self.kwargs['category']
    #     if category is not None:
    #         return Product.objects.filter(brand= category)
    #     else:
    #         return Product.objects.all()

class OrderProductList(generics.ListAPIView):
    queryset = Order_Product.objects.all()
    serializer_class = OrderProductSerializer

class VariantOptionList(generics.ListAPIView):
    queryset = Product_Variant_Options.objects.all()
    serializer_class = VariantOptionsSerializer

class ReviewList(generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class CarouselAdverts(generics.ListAPIView):
    queryset = Carousel.objects.all()
    serializer_class = CarouselSerializer
   
 
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def signup2(request):
    username = request.data.get("username", "")
    password = request.data.get("password", "")
    email = request.data.get("email", "")
    first_name = request.data.get("first_name", "")
    last_name = request.data.get("last_name", "")
    phone_number = request.data.get("phone_number", "")
    if not username and not password and not email and not first_name and not last_name:
        return Response(
            data={
                "message": "username, password and email is required to register a user"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    new_buyer = Buyer.objects.create_user(
        # user_ptr_id=new_buyer.id,
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        is_staff=False
    )
    context = {
        'message': 'You Have Been Successfully Registered'
    }
    return Response(context,status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    phonenumber = request.data.get("username")
    password = request.data.get("password")
    buyer = Buyer.objects.filter(phone_number = phonenumber).first()
    username = buyer.username
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'}, status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)

    if not user:
        context = {
            'error': 'Invalid Username or Password',
        }
        return Response(context, status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    context = {
        'token': token.key,
        'id': user.id,
        'username': username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name
    }
    return Response(context,
                    status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def addtocart(request, product_id):
    # print(request.META['HTTP_AUTHORIZATION'])
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    print(new_token)
    product = Product.objects.filter(id=product_id).first()
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    quantity = request.data.get("quantity")
    if not product_id and not quantity:
        return Response(
            data={
                "Message": "Make Sure All The Fields Are Included"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if Order_Product.objects.filter(buyer = buyer, product = product, checkout__isnull = True).exists():
        return Response(
            data={
                "Message": "Product Already In Cart"
            },
            status = status.HTTP_400_BAD_REQUEST
        )
    offer = Offer.objects.filter(product = product).first()
    if offer is not None:
        amount = offer.discount
    else:
        amount = product.unit_cost

    new_OrderProduct = Order_Product.objects.create(
        product=product,
        buyer=buyer,
        quantity=quantity,
        total=(float(amount)*float(quantity)),
    )
    products = []
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    cart_items = Order_Product.objects.filter(buyer=buyer, checkout__isnull=True)
    for order in cart_items:
        if order.quantity is not None:
            print(order.quantity)
            product = Product.objects.filter(id=order.product.id).annotate(order_id=Sum(order.id, output_field=IntegerField()),quantity=Sum(order.quantity, output_field=FloatField()), total=Sum(order.total, output_field=FloatField())).first()
            print(product.quantity)
            products.append(product)
    data = CustomCartSerializer(products, many=True)    
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def addCartVariant(request, order_id):
    variants = request.data.get("stringPojo")
    variant = Variant_Option.objects.filter(name = variants).first()
    cartProduct = Order_Product.objects.filter(id = order_id).first()
    new_OrderProductVariant = OrderProductVariantOption.objects.create(
        orderProduct = cartProduct,
        variantOptions = variant,
    )
    context = {
        'response': 'success'
    }
    return Response(data={
                "Message": "Success"
            }, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def getCartVariant(request, order_id):
    variants = []
    print(order_id)
    cart = Order_Product.objects.filter(id = order_id).first()
    orderProductVariant = OrderProductVariantOption.objects.filter(orderProduct = cart)
    for order in orderProductVariant:
        variant = Variant_Option.objects.filter(id = order.variantOptions.id).first()
        variants.append(variant)
    data = VariantsSerializer(variants, many= True)
    context = {
        'data': data.data
    }
    return Response(data.data, status=status.HTTP_200_OK) 
    

@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def removefromcart(request, order_id):
    cart_product = Order_Product.objects.filter(id=order_id).first()
    cart_variant = OrderProductVariantOption.objects.filter(orderProduct = cart_product)
    for variant in cart_variant:
        variant.delete()
    cart_product.delete()
    products = []
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    cart_items = Order_Product.objects.filter(buyer=buyer, checkout__isnull=True)
    for order in cart_items:
        if order.quantity is not None:
            print(order.quantity)
            product = Product.objects.filter(id=order.product.id).annotate(order_id=Sum(order.id, output_field=IntegerField()),quantity=Sum(order.quantity, output_field=FloatField()), total=Sum(order.total, output_field=FloatField())).first()
            print(product.quantity)
            products.append(product)
    data = CustomCartSerializer(products, many=True)    
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(["PUT"])
@permission_classes((IsAuthenticated,))
def updatecart(request, order_id):
    print(order_id)
    current_orderproduct = Order_Product.objects.filter(id = order_id).first()
    quantity = request.data.get("quantity",)
    product = Product.objects.filter(id =current_orderproduct.product.id).first()
    amount = product.unit_cost
    if not quantity:
        return Response(
            data={
                "Message": "Make Sure All The Fields Are Included"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    current_orderproduct.quantity = quantity
    current_orderproduct.total = float(amount)*float(quantity)
    current_orderproduct.save()
 
    products = []
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    cart_items = Order_Product.objects.filter(buyer=buyer, checkout__isnull=True)
    for order in cart_items:
        if order.quantity is not None:
            print(order.quantity)
            product = Product.objects.filter(id=order.product.id).annotate(order_id=Sum(order.id, output_field=IntegerField()),quantity=Sum(order.quantity, output_field=FloatField()), total=Sum(order.total, output_field=FloatField())).first()
            print(product.quantity)
            products.append(product)
    data = CustomCartSerializer(products, many=True)    
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def getcartproducts(request):
    products = []
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    cart_items = Order_Product.objects.filter(buyer=buyer, checkout__isnull=True)
    for order in cart_items:
        if order.quantity is not None:
            print(order.quantity)
            product = Product.objects.filter(id=order.product.id).annotate(order_id=Sum(order.id, output_field=IntegerField()),quantity=Sum(order.quantity, output_field=FloatField()), total=Sum(order.total, output_field=FloatField())).first()
            print(product.quantity)
            products.append(product)
    data = CustomCartSerializer(products, many=True)    
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def getPendingPaymentProducts(request, checkout_id):
    products = []
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    cart_items = Order_Product.objects.filter(buyer=buyer, checkout = checkout_id )
    for order in cart_items:
        product = Product.objects.filter(id=order.product.id).first()
        products.append(product)
    data = ProductSerializer(products, many=True)    
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def getBuyerOrderHistory(request,):
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    orders = Checkout.objects.filter(buyer = buyer)
    data = CheckoutSerializer(orders, many=True)    
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_200_OK)        


@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def addtowishlist(request, product_id):
    # print(request.META['HTTP_AUTHORIZATION'])
    products = []
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    product = Product.objects.filter(id=product_id).first()
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    if not product_id:
        return Response(
            data={
                "Message": "Product does not exist"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if Wishlist.objects.filter(buyer = buyer, product = product).exists():
        return Response(
            data={
                "Message": "Product already in wishlist"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    new_wishlistProduct = Wishlist.objects.create(
        product=product,
        buyer=buyer,
    )

    productID = Wishlist.objects.filter(buyer=buyer)
    for order in productID:
        Wishlist_product = Product.objects.filter(id = order.product.id).annotate(wishlist_id=Sum(order.id, output_field=IntegerField())).first()
        products.append(Wishlist_product)
    data = CustomWishlistSerializer(products, many=True)    
    context = {
        'data': data.data
    }
    return Response(data.data,status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def getwishlistproducts(request):
    # print(request.META['HTTP_AUTHORIZATION'])
    products = []
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    if not buyer:
        return Response(
            data={
                "Message": "You are not logged in"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    wishlistProducts = Wishlist.objects.filter(buyer=buyer)
    for order in wishlistProducts:
        allwishlistproducts = Product.objects.filter(id = order.product.id).annotate(wishlist_id=Sum(order.id, output_field=IntegerField())).first()
        products.append(allwishlistproducts)
    data = CustomWishlistSerializer(products, many=True)    
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def removefromwishlist(request, wishlist_id):
    products = []
    wishlist_product = Wishlist.objects.filter(id=wishlist_id).first()
    wishlist_product.delete()
    products = []
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    if not buyer:
        return Response(
            data={
                "Message": "You are not logged in"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    wishlistProducts = Wishlist.objects.filter(buyer=buyer)
    for order in wishlistProducts:
        allwishlistproducts = Product.objects.filter(id = order.product.id).annotate(wishlist_id=Sum(order.id, output_field=IntegerField())).first()
        products.append(allwishlistproducts)
    data = CustomWishlistSerializer(products, many=True)    
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def getproducts(request):
    category = request.data.get("name")
    print(category)
    categories = Category.objects.filter(name = category).first()
    products = Product.objects.filter(category=categories.id, status = 'VERIFIED')
    data = ProductSerializer(products, many = True)
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def getProductsFromCategoryId(request, category_id):
    categories = Category.objects.filter(id = category_id).first()
    products = Product.objects.filter(category=categories.id, status = 'VERIFIED')
    data = ProductSerializer(products, many = True)
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def getProductImages(request, product_id):
    images = Image.objects.filter(product=product_id)
    data = ImageSerializer(images, many = True)
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def getSpecificProduct(request, product_id):
    products = Product.objects.filter(id=product_id, status = 'VERIFIED')
    data = ProductSerializer(products, many = True)
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_200_OK)        

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def getfeaturedproducts(request):
    products = Product.objects.filter(feat_product = 'FEATURED')
    data = ProductSerializer(products, many = True)
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def getBrands(request):
    brands = Brand.objects.all()
    data = BrandSerializer(brands, many = True)
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_200_OK)    

@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def checkout(request):
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    # new_region_id = Region.objects.filter(id = region_id).first()
    # if not region_id:
    #     return Response(
    #         data={
    #             "Message": "You have to pick a region"
    #         },
    #         status=status.HTTP_400_BAD_REQUEST
    #     )

    total = request.data.get("quantity")
    location_details = request.data.get("location")
    region_name = request.data.get("region")
    region = Region.objects.filter(name = region_name).first()     
    new_checkoutorder = Checkout.objects.create(
        buyer = buyer,
        phonenumber = buyer.phone_number,
        total = total,
        delivery = region,
        address = location_details,
        reference_code = "M"+ get_random_string(length=4, allowed_chars='123456789ABCDEFGHIJKLMNPQRSTUVWXYZ'),
        status = "PENDING"
    )
    cart_items = Order_Product.objects.filter(buyer=buyer, checkout__isnull=True).update(
        checkout = new_checkoutorder.id
    )
    # checkouts = Checkout.objects.filter(id = new_checkoutorder.id).first()
    data = CheckoutSerializer([new_checkoutorder], many=True)    
    context = {
        'data': data.data
    }
    return Response(data.data,status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def getvariantoptions(request, product_id):
    variants = []
    variant_option = Product_Variant_Options.objects.filter(product = product_id)
    for order in variant_option:
        parent_variant = Variant_Option.objects.filter(id=order.variant_options.id)

        for order2 in parent_variant:
            variant = Variant.objects.filter(id=order2.variant.id).annotate(variant_option_id = Sum(order2.id, output_field = IntegerField()), variant_option_name = Value(order2.name, output_field = CharField())).first()
            variants.append(variant)
    data = CustomVariantsSerializer(variants, many=True)    
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def getReview(request, product_id):
    review = []
    reviews = Review.objects.filter(product = product_id)
    for order in reviews:
        buyers = Buyer.objects.filter(id = order.buyer.id).annotate(ratings = Sum(order.ratings, output_field = IntegerField()), comments = Value(order.comments, output_field = CharField()), created_at = Value(order.created_at, output_field = DateTimeField())).first()
        review.append(buyers)

    data = ReviewSerializer(review, many=True)

    return Response(data.data, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def addReview(request,product_id):
    review = []
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    product = Product.objects.filter(id = product_id).first()
    comment = request.data.get("comments")
    ratings = request.data.get("ratings")

    new_review = Review.objects.create(
        buyer = buyer,
        product = product,
        comments = comment,
        ratings = int(ratings),
    )

    reviews = Review.objects.filter(product = product_id)

    for order in reviews:
        buyers = Buyer.objects.filter(id = order.buyer.id).annotate(ratings = Sum(order.ratings, output_field = IntegerField()), comments = Value(order.comments, output_field = CharField()), created_at = Value(order.created_at, output_field = DateTimeField())).first()
        review.append(buyers)

    data = ReviewSerializer(review, many=True)

    return Response(data.data, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def getReviewStatus(request,product_id):
    review = []
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()

    if Checkout.objects.filter(buyer = buyer, status = 'PAID').exists():
        checkout = Checkout.objects.filter(buyer = buyer, status = 'PAID')
        for order in checkout:
            products = Order_Product.objects.filter(checkout = order.id)
            for product in products:
                reviewable = Order_Product.objects.filter(product = product_id).first()
                if reviewable is not None:
                # if Order_Product.objects.filter(product = product_id).exists():
                    context = {
                            'response': 'success'
                        }
                    return Response(context, status=status.HTTP_200_OK)
                else:
                     context ={
                         'response': 'Not Found'
                     }
                     return Response(context, status=status.HTTP_400_BAD_REQUEST)   
    
    else:
        context = {
            'response': 'Not found'
        }
        return Response(context, status=status.HTTP_404_NOT_FOUND)                 

@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def getBuyerOrders(request):
    # print(request.META['HTTP_AUTHORIZATION'])
    products = []
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    if not buyer:
        return Response(
            data={
                "Message": "You are not logged in"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    wishlistProducts = Wishlist.objects.filter(buyer=buyer)
    for order in wishlistProducts:
        allwishlistproducts = Product.objects.filter(id = order.product.id).annotate(wishlist_id=Sum(order.id, output_field=IntegerField())).first()
        products.append(allwishlistproducts)
    data = CustomWishlistSerializer(products, many=True)    
    context = {
        'data': data.data
    }

    return Response(data.data,status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def getShortCodeSMS(request):
    phonenumber = request.data.get("phone_number")

    if Buyer.objects.filter(phone_number = phonenumber).exists():

        context = {
            'response': 'Already Registered'
        }
        return Response(context, status=status.HTTP_400_BAD_REQUEST)
    else:    
        # Initialize SDK
        username = "Mashkys"    # use 'sandbox' for development in the test environment
        api_key = "652230d338f11fd49333722a8acba0161942b5b3efb880caf2fb21958e4fdde4"      # use your sandbox app API key for development in the test environment
        africastalking.initialize(username, api_key)
        random_code = get_random_string(length=6, allowed_chars='123456789')
        appKey = request.data.get("appSignature")
        new_phone_number = f"{254}{phonenumber[-9:]}"
        # print(random_code)

        # Initialize a service e.g. SMS
        sms = africastalking.SMS


        # Use the service synchronously
        response = sms.send("<#> Your MASHKYS code is:" + random_code + ":\n " + appKey , ["+"+new_phone_number], "MASHKYS")
        print(response)
        short_code = ShortCode.objects.create(
            phone_number = phonenumber,
            short_code = random_code,
        )
        context = {
            'response': 'success'
        }
        return Response(context, status=status.HTTP_200_OK)

        # Or use it asynchronously
        # def on_finish(error, response):
        #     if error is not None:
        #         raise error
        #     print(response)

        # sms.send("Hello Message!", ["+2547xxxxxx"], callback=on_finish)

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def getResetCodeSMS(request):
    phonenumber = request.data.get("phone_number")

    if Buyer.objects.filter(phone_number = phonenumber).exists():   
        # Initialize SDK
        username = "Mashkys"    # use 'sandbox' for development in the test environment
        api_key = "652230d338f11fd49333722a8acba0161942b5b3efb880caf2fb21958e4fdde4"      # use your sandbox app API key for development in the test environment
        africastalking.initialize(username, api_key)
        random_code = get_random_string(length=6, allowed_chars='123456789')
        appKey = request.data.get("appSignature")
        new_phone_number = f"{254}{phonenumber[-9:]}"
        print(random_code)
        # Initialize a service e.g. SMS
        sms = africastalking.SMS 


        # Use the service synchronously
        response = sms.send("<#> Your MASHKYS code is:" + random_code + ":\n " + appKey , ["+"+new_phone_number], "MASHKYS")
        print(response)

        short_code = ShortCode.objects.create(
            phone_number = phonenumber,
            short_code = random_code,
        )
        context = {
            'response': 'success'
        }
        return Response(context, status=status.HTTP_200_OK)

        # Or use it asynchronously
        # def on_finish(error, response):
        #     if error is not None:
        #         raise error
        #     print(response)

        # sms.send("Hello Message!", ["+2547xxxxxx"], callback=on_finish)
    else:
        
        context = {
            'response': 'That Number Is Not Registered'
        }
        return Response(context, status=status.HTTP_400_BAD_REQUEST)      


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def verifyCode(request):
    short_code = request.data.get("short_code","")
    phonenumber = request.data.get("phone_number","")

    codes = ShortCode.objects.filter(phone_number = phonenumber)

    if ShortCode.objects.filter(short_code = short_code).exists():
            password = request.data.get("password", "")
            new_buyer = Buyer.objects.create_user(
                # user_ptr_id=new_buyer.id,
                username = phonenumber,
                password= password,
                phone_number=phonenumber,
                is_staff=False
            )

            codes.delete()
            token, _ = Token.objects.get_or_create(user=new_buyer)
            context = {
                'token': token.key,
                'id': new_buyer.id,
                'phonenumber': new_buyer.phone_number
            }
            return Response(context,
                            status=status.HTTP_201_CREATED)
    context = {
        'response': 'Wrong Short Code'
    }
    return Response(context, status=status.HTTP_200_OK)
  

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def resetPin(request):
    short_code = request.data.get("pin")
    phonenumber = request.data.get("phone_number")

    codes = ShortCode.objects.filter(phone_number = phonenumber)
    if ShortCode.objects.filter(short_code = short_code).exists():
            user = Buyer.objects.filter(phone_number = phonenumber).first()
            token, _ = Token.objects.get_or_create(user=user)
            context = {
                'token': token.key,
                'id': user.id,
                'phonenumber': user.phone_number,
            }
            codes.delete()

            return Response(context,
                            status=HTTP_201_CREATED)
    context = {
        'response': 'Wrong Short Code'
    }
    return Response(context, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def getSearchResults(request):
    result = []
    query = request.data.get("stringPojo")
    if Category.objects.filter(name__icontains = query).exists():
        categories = Category.objects.filter(name__icontains = query)
        for order in categories:
            products = Product.objects.filter(category=order.id, status = 'VERIFIED')
            result.append(products)
            # sub_category = Category.objects.filter(parent_id = order.id)
            # for sub in sub_category:
            #     sub_products = Product.objects.filter(category=sub.id, status = 'VERIFIED')
            #     result.append(products)
        data = ProductSerializer(products, many = True)

        return Response(data.data,status=status.HTTP_200_OK)

    elif Brand.objects.filter(name__icontains = query).exists():
        brands = Brand.objects.filter(name__icontains = query).first()
        products = Product.objects.filter(product_brand = brands)
        result.append(products)
        data = ProductSerializer(products, many = True)

        return Response(data.data,status=status.HTTP_200_OK)

    elif Product.objects.filter(name__icontains = query).exists():
        products = Product.objects.filter(name__icontains = query)
        result.append(products)
        data = ProductSerializer(products, many = True)

        return Response(data.data,status=status.HTTP_200_OK)

    else:
        context={
            'messsage':'No Results'
        }    

        return Response(context,status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def updateUserName(request):
    firstname = request.data.get("first_name")
    lastname = request.data.get("last_name")
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    user = User.objects.filter(id=buyer.user_ptr_id).update(
        first_name = firstname,
        last_name = lastname
    )

    # user.first_name=firstname,
    # user.last_name=lastname
    # user.save()
    users = User.objects.filter(id=buyer.user_ptr_id).first()
    
    context = {
                'first_name': users.first_name,
                'last_name': users.last_name
            }

    return Response(context, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def filterProducts(request, category_id):
    filter_max_value = request.data.get("max_filter")
    filter_min_value = request.data.get("min_filter")
    filter_string_value = request.data.get("string")
    filter_name = request.data.get("name")
    # filter_range = request.data.get("range")

    if filter_name == "price":
        if filter_min_value == "0":
            products = Product.objects.filter(category = category_id, unit_cost__lte= filter_max_value)
        else:
            products = Product.objects.filter(category = category_id, unit_cost__lt = filter_max_value, unit_cost__gt = filter_min_value)
        data = ProductSerializer(products, many = True)
        return Response(data.data,status=status.HTTP_200_OK)
    elif filter_name == "brand":
        brand = Brand.objects.filter(name = filter_string_value).first()
        products = Product.objects.filter(category = category_id, brand = brand)
        data = ProductSerializer(products, many = True)
        return Response(data.data,status=status.HTTP_200_OK)

    context={
        'messsage':'No Results'
    }     
    return Response(context, status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def validateVoucher(request):
    voucher_value = request.data.get("voucher")
    # currentTime = datetime.datetime.now()
    currentTime = timezone.now()
    r_token = request.META['HTTP_AUTHORIZATION']
    new_token = r_token.split(' ', 1)[1]
    token = Token.objects.filter(key=new_token).first()
    buyer = Buyer.objects.filter(user_ptr_id=token.user.id).first()
    if not buyer:
        return Response(
            data={
                "Message": "You are not logged in"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if Voucher.objects.filter(code = voucher_value, no_of_users__gt = 0, start_time__lt = currentTime, end_time__gt = currentTime).exists():
        voucher = Voucher.objects.get(code = voucher_value, no_of_users__gt = 0, start_time__lt = currentTime, end_time__gt = currentTime)
        previous_value = voucher.no_of_users
        voucher.no_of_users = previous_value -1
        voucher.save()
        new_voucher_entry = Voucher_Buyer.objects.create(
            buyer = buyer,
            voucher = voucher
        )
        context ={
            'message':'Voucher is valid',
            'amount': voucher.amount,
            'users':voucher.no_of_users
        }
        return Response(context, status=status.HTTP_200_OK)
    else:
        context ={
            'message':'Voucher invalid',
            'amount':'null',
            'users':'null'
        }
        return Response(context, status=status.HTTP_404_NOT_FOUND)        