from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Collection , Review ,OrderItem , Cart ,CartItem
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter , OrderingFilter
from rest_framework.viewsets import ModelViewSet , GenericViewSet
from rest_framework.mixins import ListModelMixin , CreateModelMixin , RetrieveModelMixin , DestroyModelMixin 
from rest_framework.pagination import PageNumberPagination
from .serializers import ProductSerializer, CollectionSerializer , ReviewSerializer , CartSerializer ,CartItemSerializer , AddCartItemSerializer , UpdateCartItemSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .filters import ProductFilter

# in view set we join logic of multiple related views into a single class. 
# This can help reduce code duplication and make it easier to manage related views. For example, instead of having separate classes for listing products, creating products, retrieving product details, updating products, and deleting products, we can combine all of these actions into a single ProductViewSet class. This can make our code more organized and easier to maintain, especially as our application grows in complexity. Additionally, view sets can provide built-in functionality for common actions like pagination, filtering, and authentication, which can further simplify our code and improve the overall user experience of our API.
class ProductViewSet(ModelViewSet):
    
    queryset= Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields= ['unit_price' , 'last_update']
    pagination_class = PageNumberPagination
    # def get_queryset(self):
    # #  Go to the database and grab every single product we have. Put them in a box called queryset."
     # #   is a dictionary that holds anything typed after the ? in the URL.
    #    collection_id= self.request.query_params.get("collection_id")
    # #   However, what you wrote here uses self.request.query_params. 
    # # This looks for variables at the very end of the URL, after a question mark ?.
    #    if collection_id is not None:
    #        queryset= queryset.filter(collection_id=collection_id)

    #    return queryset

    def get_serializer_context(self):
        return {'request' : self.request}   
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({"error": "Product cannot be deleted because it is associated with an order item."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        return super().destroy(request, *args, **kwargs)
    # def delete(self, request, pk):
    #     product = get_object_or_404(Product, pk=pk)
    #     if product.orderitems.count() > 0:
    #         return Response({"error": "Product cannot be deleted because it is associated with an order item."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     product.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

class CollectionViewSet(ModelViewSet):

    queryset = Collection.objects.annotate(products_count=Count('product'))
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        collection = get_object_or_404(Collection.objects.annotate(products_count=Count('product')), pk=pk)
        if collection.product_set.count() > 0:
            return Response({"error": "Collection cannot be deleted because it includes one or more products."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
     
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])
    # In your Review model, you likely have a ForeignKey pointing to a Product. 
    # By default, Django creates a database column for this called product_id
    # self.kwargs is a dictionary that Django uses to store variables it extracts from the URL.
    # Imagine a user goes to http://yourwebsite.com/products/8/reviews/ to see the reviews for product number 8. Here is exactly what happens in that single line of code:
   # Django looks at the URL and grabs the 8.
   # It stores it in self.kwargs like this: {'product_pk': 8}.
# Your code asks for that number using self.kwargs["product_pk"] The line of code essentially transforms into this behind the scenes:
# Python
# return Review.objects.filter(product_id=8)
# Django queries the database, fetches only the reviews attached to Product #8, and returns them to the user.

    def get_serializer_context(self):
        return {'product_id' : self.kwargs['product_pk']}
# The URL defines the name product_pk.
# The ViewSet reads product_pk from the URL.
# The ViewSet creates a dictionary, invents a new key called product_id, and assigns the number to it.
# The Serializer reads the self.context dictionary looking for the product_id key you created.
class CartViewSet(CreateModelMixin , ListModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    # idk how to filter out it but agr admin side sy dekhi jaye 
    # to sbki list bhi show kr skty hain 
    queryset = Cart.objects.prefetch_related("items__product").all()
    serializer_class= CartSerializer

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method== "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer
    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}
    def get_queryset(self):
         return CartItem.objects\
    .filter(cart_id=self.kwargs["cart_pk"])\
    .select_related("product")

# @api_view(["GET", "POST"])
# # Treat this function as an API endpoint. Accept JSON, return JSON,
# # and give me a nice browsable API interface in my browser
# def collection_list(request):
#    if request.method == "GET":
#        query_set = Collection.objects.annotate(products_count=Count('product'))
#        serializer = CollectionSerializer(query_set, many=True)
#        return Response(serializer.data)
#    elif request.method == "POST":
#        serializer = CollectionSerializer(data=request.data)
#        serializer.is_valid(raise_exception=True)
#        collection = serializer.save()
#        # Re-fetch with annotation to show products_count in response
#     #    collection = Collection.objects.annotate(products_count=Count('product')).get(pk=collection.pk)
#     #    serializer = CollectionSerializer(collection)
#        return Response(serializer.data, status=status.HTTP_201_CREATED)

# @api_view(["GET", "PUT" , "DELETE"])
# def collection_detail(request, pk):
#     collection = get_object_or_404(Collection.objects.annotate(products_count=Count('product')), pk=pk)
#     if request.method == "GET":
#       serializer = CollectionSerializer(collection)
#       return Response(serializer.data)
#     elif request.method == "PUT":
#       #   product = get_object_or_404(Product, pk=pk)
#     #   deserialization process is to convert the incoming data (request.data) into a Python object that can be used to update the existing product instance.
#         serializer = CollectionSerializer(collection, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         # Re-fetch with annotation to show products_count in response
#         collection = Collection.objects.annotate(products_count=Count('product')).get(pk=collection.pk)
#         serializer = CollectionSerializer(collection)
#         return Response(serializer.data)
#     elif request.method == "DELETE":
#         # if product.orderitems.count() > 0:
#         #     return Response({"error": "Product cannot be deleted because it is associated with an order item."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
 