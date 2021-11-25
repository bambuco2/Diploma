from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.conf import settings

class Product(models.Model):
    productID = models.BigAutoField(primary_key=True, unique=True)

    name = models.CharField(max_length=300)
    description = models.TextField()
    price = models.FloatField()
    rank = models.FloatField(default=5)

    def __str__(self) -> str:
        return super().__str__()

class Category(models.Model):
    categoryID = models.BigAutoField(primary_key=True, unique=True)

    name = models.CharField(max_length=300)
    urlName = models.CharField(max_length=300, default="defaultValue")
    description = models.TextField()

    def __str__(self) -> str:
        return super().__str__()

class SubCategory(models.Model):
    subCategoryID = models.BigAutoField(primary_key=True, unique=True)
    categoryID = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    urlName = models.CharField(max_length=300, default="defaultValue")

    def __str__(self) -> str:
        return super().__str__()

class ProductInCategory(models.Model):
    productID = models.ForeignKey(Product, on_delete=models.CASCADE)
    categoryID = models.ForeignKey(Category, on_delete=models.CASCADE)
    subCategoryID = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    UniqueConstraint(fields=[productID, categoryID, subCategoryID], name='unique_entry')

    def __str__(self) -> str:
        return super().__str__()

class User(models.Model):
    userID = models.BigAutoField(primary_key=True, unique=True)

    userName = models.CharField(max_length=300, unique=True)
    password = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    surname = models.CharField(max_length=300)

    def __str__(self) -> str:
        return super().__str__()

class Cart(models.Model):
    cartID = models.BigAutoField(primary_key=True, unique=True)
    userID = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return super().__str__()

class ProductInCart(models.Model):
    cartID = models.ForeignKey(Cart, on_delete=models.CASCADE)
    productID = models.ForeignKey(Product, on_delete=models.CASCADE)
    UniqueConstraint(fields=[productID, cartID], name='unique_product_cart')

    quantity = models.IntegerField()

    def __str__(self) -> str:
        return super().__str__()

class PurchaseHistory(models.Model):
    cartID = models.ForeignKey(Cart, on_delete=models.CASCADE)
    productID = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.IntegerField()

    def __str__(self) -> str:
        return super().__str__()
