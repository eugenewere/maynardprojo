from django.urls import path
from django.conf.urls import include, url
from androidAuthApi import views
from rest_framework.authtoken import views as authviews


urlpatterns = [
    path('login/',views.login),
    path('users/', views.UserList.as_view()),
    path('user/details/<int:pk>/', views.UserDetail.as_view()),
    path('api-token-auth/', authviews.obtain_auth_token),
    path('signup/',views.signup2),
    path('login/',views.login),
    path('category/',views.CategoryList.as_view()),
    path('unfilteredcategory/',views.UnfilteredCategoryList.as_view()),
    path('product/',views.ProductList.as_view()),
    path('wishlist/',views.WishList.as_view()),
    path('region/',views.RegionList.as_view()),
    path('product/category/',views.ProductDetails.as_view()),
    path('allProducts/',views.AllProductList.as_view()),
    path('orders/',views.getBuyerOrderHistory),
    path('pendingOrdersProducts/<int:checkout_id>/',views.getPendingPaymentProducts),
    path('addtocart/<int:product_id>/',views.addtocart),
    path('removefromcart/<int:order_id>/',views.removefromcart),
    path('updatecart/<int:order_id>/',views.updatecart),
    path('getcartproducts/',views.getcartproducts),
    path('getcartvariants/<int:order_id>/',views.getCartVariant),
    path('addtowishlist/<int:product_id>/',views.addtowishlist),
    path('getwishlistproducts/',views.getwishlistproducts),
    path('removefromwishlist/<int:wishlist_id>/',views.removefromwishlist),
    path('getproducts/',views.getproducts),
    path('getSimilarProducts/<int:category_id>/',views.getProductsFromCategoryId),
    path('getSpecificProduct/<int:product_id>/',views.getSpecificProduct),
    path('getProductImages/<int:product_id>/',views.getProductImages),
    path('getfeaturedproducts/',views.getfeaturedproducts),
    path('checkout/',views.checkout),
    path('variant_options/<int:product_id>/',views.getvariantoptions),
    path('adverts/',views.CarouselAdverts.as_view()),
    path('reviews/<int:product_id>/',views.getReview),
    path('getShortCode/',views.getShortCodeSMS),
    path('getResetShortCode/',views.getResetCodeSMS),
    path('verifyCode/',views.verifyCode),
    path('resetPin/',views.resetPin),
    path('addCartVariant/<int:order_id>/',views.addCartVariant),
    path('rateProduct/<int:product_id>/',views.addReview),
    path('reviewStatus/<int:product_id>/',views.getReviewStatus),
    path('getQueryResults/',views.getSearchResults),
    path('updateUserNames/',views.updateUserName),
    path('filterProducts/<int:category_id>/',views.filterProducts),
    path('verifyVoucher/',views.validateVoucher),
    path('getBrands/', views.getBrands),







]

