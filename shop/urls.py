from django.urls import path

from . import views


app_name = 'shop'

urlpatterns = [
    # ex: /shop/
    path('', views.index, name='ProductList'),
    # ex: /shop/5/
    path('<int:product_id>/', views.product_detail_view, name='ProductDetail'),
]
