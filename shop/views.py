from urllib.parse import urlencode

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from .models import Product
from .forms import GoogleMapForm
from .filters import ProductFilter
from account.models import Account


# Create your views here.
def index(request):
    all_products = Product.objects.all().order_by('-pub_date')
    product_filter = ProductFilter(request.GET, queryset=all_products)
    product_list = product_filter.qs
    contacts = Account.objects.all()

    paginator = Paginator(product_list, 2)
    page = request.GET.get('page', 1)

    gt = request.GET.copy()
    if 'page' in gt:
        del gt['page']

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'shop/index.html', {
        'filter': product_filter,
        'products': products,
        'contacts': contacts,
        'params': urlencode(gt),
        'page_request_var': paginator,
    })


def product_detail_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    form = GoogleMapForm(initial={
        'address': product.address,
        'geolocation': product.geolocation,
    })
    form.fields['geolocation'].widget.attrs['disabled'] = True
    form.fields['address'].widget.attrs['readonly'] = True
    image_models = product.images.all()
    return render(request, 'shop/product_detail.html', {
        'object': product,
        'form': form,
        "image_models": image_models,
    })


"""
class IndexProductListView(ListView):
    model = Product
    ordering = ['-pub_date']
    template_name = 'shop/index.html'

    def get_context_data(self, **kwargs):
        queryset = ''
        context = super(IndexProductListView, self).get_context_data()

        context['products'] = Product.objects.all()

        product_list = Product.objects.all()
        product_filter = ProductFilter(self.kwargs, queryset=product_list)
        context['filter'] = product_filter

        paginator = Paginator(context['products'], 3)
        page_request_var = "page"
        page = self.request.GET.get(page_request_var)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)

        context['products'] = queryset
        context['page_request_var'] = page_request_var
        return context
"""
