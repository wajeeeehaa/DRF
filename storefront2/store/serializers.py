from rest_framework import serializers
from decimal import Decimal
from store.models import Product, Collection

class CollectionSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=200)
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
    products_count = serializers.IntegerField(read_only=True)

class ProductSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=200)
    # price = serializers.DecimalField(max_digits=10, decimal_places=2, source='unit_price')
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'unit_price','inventory','tax_price', 'collection']
    # description = serializers.CharField(max_length=1000)
    tax_price = serializers.SerializerMethodField(method_name='calculate_tax')
# ways to represent the relationship between product and collection
# first one is to use primary key related field as primary key realted fiels is id so its gonns show this
 # collection= serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
# second one is to use string related field as string related field is title so its gonns show this
# PrimaryKeyRelatedField: This is the simplest. It just outputs the ID (3). 
# It is fast, but the frontend has to figure out what collection 3 is.
# StringRelatedField: Instead of an ID, this looks at your Collection
#  model, finds the __str__ method you wrote, and outputs that text (e.g., "Summer Clothes").
# HyperlinkedRelatedField: This is what you used! It builds a full clickable URL (e.g., http://127.0.0.1:8000/collections/3/).
    # collection= serializers.HyperlinkedRelatedField(queryset=Collection.objects.all(), view_name='collection-detail')

    def calculate_tax(self, product):
       # Handle both object (GET) and dict (POST) cases
       if isinstance(product, dict):
           return product['unit_price'] * Decimal(0.1)
       return product.unit_price * Decimal(0.1)
    # information about how to access data in the serializer
# On GET (reading): You receive the model instance → use .attribute
# On POST/PUT (writing): You receive the validated_data dict → use ['key']
# def validate(self, data):
#     if data["password"] != data["confirm_password"]:
#         return serializers.ValidationError("Password fields didn't match.")
#     return data 
# from above function it will return error or dictionary 

# def create(self, validated_data):
    # unpacking the dictionary to create a product
    # why do we need to unpack the dictionary? because the create method
    #  of the model serializer expects individual keyword arguments,
    #  not a single dictionary. By unpacking the dictionary using 
    # **validated_data, we are passing each key-value pair 
    # in the dictionary as a separate argument to the create method. 
    # This allows the create method to properly initialize a new instance 
    # of the model with the provided data.
    # product = Product.objects.create(**validated_data)
    # product.other = 1
    # product.save()
    # return product

# def update(self , instance, validated_data):
#     instance.unit_price = validated_data.get('unit_price')
#     instance.save()
#     return instance
    