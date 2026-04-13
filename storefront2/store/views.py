from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpRequest
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Collection
from rest_framework import status
from .serializers import ProductSerializer, CollectionSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Count

@api_view(["GET", "POST"])
# Treat this function as an API endpoint. Accept JSON, return JSON,
# and give me a nice browsable API interface in my browser
def product_list(request):
   if request.method == "GET":
       query_set = Product.objects.select_related('collection').all()
#  Because you are grabbing data from a related table, 
# select_related grabs the Product and the Collection in one single database trip
#  instead of doing it hundreds of times
       serializer = ProductSerializer(query_set, many=True, context= {'request': request})
   # To build this link, DRF needs to know the domain name of your website.
   #  That is exactly why you had to pass context={'request': request} 
   # in your views! It uses the request data to figure out the base URL
   #  to build the link.
       return Response(serializer.data)
   elif request.method == "POST":
       serializer = ProductSerializer(data=request.data)
       serializer.is_valid(raise_exception=True)
       print(serializer.validated_data)
       serializer.save()
       return Response(serializer.data, status=status.HTTP_201_CREATED  )
   
# Create your views here

@api_view(["GET", "PUT" , "DELETE"])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Go to the database and get this specific product. If it doesn't exist, stop everything
    #  immediately and tell the user '404 Not Found'."
    if request.method == "GET":
       serializer = ProductSerializer(product, context={'request': request})
       return Response(serializer.data)
    elif request.method == "PUT":
      #   product = get_object_or_404(Product, pk=pk)
    #   deserialization process is to convert the incoming data (request.data) into a Python object that can be used to update the existing product instance.
        serializer = ProductSerializer(product, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == "DELETE":
        if product.orderitems.count() > 0:
            return Response({"error": "Product cannot be deleted because it is associated with an order item."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET", "POST"])
# Treat this function as an API endpoint. Accept JSON, return JSON,
# and give me a nice browsable API interface in my browser
def collection_list(request):
   if request.method == "GET":
       query_set = Collection.objects.annotate(products_count=Count('product'))
       serializer = CollectionSerializer(query_set, many=True)
       return Response(serializer.data)
   elif request.method == "POST":
       serializer = CollectionSerializer(data=request.data)
       serializer.is_valid(raise_exception=True)
       collection = serializer.save()
       # Re-fetch with annotation to show products_count in response
    #    collection = Collection.objects.annotate(products_count=Count('product')).get(pk=collection.pk)
    #    serializer = CollectionSerializer(collection)
       return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET", "PUT" , "DELETE"])
def collection_detail(request, pk):
    collection = get_object_or_404(Collection.objects.annotate(products_count=Count('product')), pk=pk)
    if request.method == "GET":
      serializer = CollectionSerializer(collection)
      return Response(serializer.data)
    elif request.method == "PUT":
      #   product = get_object_or_404(Product, pk=pk)
    #   deserialization process is to convert the incoming data (request.data) into a Python object that can be used to update the existing product instance.
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Re-fetch with annotation to show products_count in response
        collection = Collection.objects.annotate(products_count=Count('product')).get(pk=collection.pk)
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == "DELETE":
        # if product.orderitems.count() > 0:
        #     return Response({"error": "Product cannot be deleted because it is associated with an order item."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
 