from django.conf.urls import url
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView, \
   PasswordResetDoneView
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views


app_name = 'Shoppy'
urlpatterns =[
   # path('', views.setcookie),
   path('', views.home, name='shoppy-home'),

   path('register/', views.buyer_register, name='shoppy-buyer-reg'),
   path('seller_register/', views.seller_register, name='shoppy-seller-reg'),
   path('login/', views.user_login, name='shoppy-login'),
   path('logout/', views.logout_view, name='shoppy-logout'),
   path('products_list/<int:category_id>/', views.productsList, name='product_list'),
   path('allcategoryproductsList/', views.allcategoryproductsList, name='allcategoryproductsList'),
   path('user_account/' , views.user_account, name='shoppy-user_account' ),
   path('checkout/' , views.checkout, name='shoppy-view_checkout' ),
   path('search/' , views.search, name="searchbar" ),
   path('placeholder/' , views.placeholder, name="placeholder" ),

   path('howtopay/', views.how_to_pay, name='how_to_pay'),

   path('product_filter/', views.product_filter, name='product_filter'),





   #wishlist
   path('add_to_wishlist/' , views.addToWishlist, name='add_to_wishlist' ),
   path('add_to_wishlist2/<int:product_id>/<str:source>/' , views.addToWishlist2, name='add_to_wishlist2' ),
   path('remove_from_wishlist/<int:wishlist_id>/<str:source>' , views.unWishProduct, name='remove_from_wishlist' ), #delete wishlist/unwished
   path('remove_from_wishlist/all/' , views.unWish_All_Products, name='remove_all_from_wishlist' ), #delete all wishlist/unwished

   #view product details
   path('details/<int:product_id>/', views.productDetails, name='shoppy_product_details'),
         # reviews
         # path('make_reviews/', views.productReview, name='shoppy_product_review'),

   #cart
   path('cart/', views.cart, name='shoppy-cart'),
   path('addto/cart/<str:source>/', views.addCart, name='shoppy-add-cart'),
   # path('addto/cartsession/', views.addCartSession, name='shoppy-add-cartSession'),
   path('deletefrom/cart/<int:order_id>/', views.deleteCartProduct, name='shoppy_delete_cart_product'),

   # checkout
   path('confirmcheckout/', views.confirmCheckout, name='shoppy-checkout'),

   # useraccount password change
   path('user_account/change_password', views.change_password, name='change_password'),

   # password reset

   path('pin_reset/', views.password_resett, name='password_resett'),
   path('getpinShortcode/', views.getShortcode, name='getpinShortcode'),
   path('verifyCode/', views.verifyCode, name='verifyCode'),
   path('verifypassword/', views.verifypassword, name='verifypassword'),
   path('pin_confirm/', views.pin_confirmm, name='password_confirmm'),
   path('new_pin/', views.new_pin, name='new_pin'),




   path('deleteme/', views.deleteme, name= 'deleteme'),
   path('check_voucher_if_it_exists/', views.check_voucher_if_it_exists, name= 'check_voucher_if_it_exists'),


   path('all_buyers_orders/', views.all_buyers_orders, name= 'all_buyers_orders'),
   path('all_buyers_order_products/<str:reference_code>', views.all_buyers_order_products, name= 'all_buyers_order_products'),
   path('orders_payment_opions/<int:checkout_id>', views.orders_payment_opions, name= 'orders_payment_opions'),





]





