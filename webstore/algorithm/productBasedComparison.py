from numpy.core.fromnumeric import sort
from webstore.models import Product, Tag, ProductWithTag
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

#Algorithm comparing products and finding which ones resemble the most using cosine similarity measuring method
class ProductBasedComparison:
    def __init__(self, k, categoryID, subCategoryID, selectedProduct):
        self.k = k
        self.categoryID = categoryID
        self.subCategoryID = subCategoryID
        self.selectedProduct = selectedProduct
    
    #Creates data table about products
    def createDataTable(self):
        productsDataTable = np.zeros((Product.objects.filter().count()-1,Tag.objects.filter().count()+2))
        row = 0
        for product in Product.objects.filter():
            if(product.productID == self.selectedProduct.productID):
                continue
            column = 0
            productsDataTable[row][column] = int(product.price)
            column+=1
            productsDataTable[row][column] = int(product.rank)
            column+=1
            for tag in Tag.objects.filter():
                if(ProductWithTag.objects.filter(productID_id = product.productID, tagID_id = tag.tagID).exists()):
                    productsDataTable[row][column] = 1
                column+=1
            row+=1
        return productsDataTable

    #Creates data table about selected product
    def createSelectedProductDataTable(self):
        selectedProductDataTable = np.zeros((1,Tag.objects.filter().count()+2))
        column = 0

        selectedProductDataTable[0][column] = int(self.selectedProduct.price)
        selectedProductDataTable[0][column+1] = int(self.selectedProduct.rank)
        column = 2
        for tag in Tag.objects.filter():
            if(ProductWithTag.objects.filter(productID_id = self.selectedProduct.productID, tagID_id = tag.tagID).exists()):
                selectedProductDataTable[0][column] = 1
            column+=1
        return selectedProductDataTable

    #Sorts products by most similar in ascending order and return the sorted product list
    def findMostSimilar(self, similarityArray):
        column = 0
        productList = []
        sortedProductList = []
        for product in Product.objects.filter():
            if(product.productID == self.selectedProduct.productID):
                continue
            productList.append((product.productID, similarityArray[0][column]))
            column+=1
        productList.sort(key=lambda x:x[1])
        for productID, productSimilarityScore in productList:
            sortedProductList.append(Product.objects.filter(productID = productID)[0])
        return sortedProductList
    
    def calculate(self):
        productList = []
        productData = self.createDataTable()
        currentProductData = self.createSelectedProductDataTable()
        similarityArray = cosine_similarity(currentProductData,productData)
        productList = self.findMostSimilar(similarityArray)
        if(len(productList) < self.k):
            return productList
        
        return productList[-self.k:]