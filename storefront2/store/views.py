from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpRequest
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Collection
from rest_framework import status
from .serializers import ProductSerializer, CollectionSerializer
from django.shortcuts import get_object_or_404

@api_view(["GET", "POST"])
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
      #  serializer.is_valid(raise_exception=True)
      #  serializer.save()
      #  return Response(serializer.data, status=201)
       return Response(serializer.data, status=status.HTTP_201_CREATED  )
# Create your views here

@api_view(["GET", "PUT"])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
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

@api_view()
def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    serializer = CollectionSerializer(collection)
    return Response(serializer.data)
 