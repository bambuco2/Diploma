from webstore.models import Product, JointProductPurchase, ProductWithTag, Tag
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

#Algorithm finds which products are usually bought together and bases it's recommendation from that
class ComplementaryOfSimilarProducts:
    def __init__(self, k, categoryID, subCategoryID, selectedProduct):
        self.k = k
        self.categoryID = categoryID
        self.subCategoryID = subCategoryID
        self.selectedProduct = selectedProduct

    #Returns a list of most frequent products in ComplimentaryProducts list
    def findMostCommonComplimentaryProducts(self, complimentaryProductsList):
        mostCommonList = []
        mostCommonDict = {}
        productList = []
        for complimentaryProduct in complimentaryProductsList:
            if(complimentaryProduct in mostCommonDict.keys()):
                mostCommonDict[complimentaryProduct] = mostCommonDict[complimentaryProduct] + 1
            else:
                mostCommonDict[complimentaryProduct] = 1
        for complimentaryProduct in complimentaryProductsList:
            if((complimentaryProduct, mostCommonDict[complimentaryProduct]) not in mostCommonList):
                mostCommonList.append((complimentaryProduct, mostCommonDict[complimentaryProduct]))
        mostCommonList.sort(key=lambda x:x[1], reverse=True)
        for productID, count in mostCommonList:
            productList.append(Product.objects.filter(productID = productID)[0])
        return productList

    #Finds products that are usually bought together with the selected product
    def findComplimentaryProducts(self):
        complimentaryProductList = []
        query = JointProductPurchase.objects.filter(productID_id = self.selectedProduct.productID)
        if(query.exists()):
            productsID = query[0].relatedProducts.split(",")[:-1]
            for productID in productsID:
                complimentaryProductList.append(productID)
        return complimentaryProductList
    
    #Creates a numpy data table with product tags, price and rank for selected product
    def createDataForCurrentProduct(self):
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
    
    #Creates a numpy data table with product tags, price and rank for other products in JointProductPurchase table
    def createDataForProducts(self):
        productsDataTable = np.zeros((JointProductPurchase.objects.filter().count(),Tag.objects.filter().count()+2))
        row = 0
        for product in JointProductPurchase.objects.filter():
            product = Product.objects.filter(productID = product.productID_id)[0]
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
    
    #Returns the most similar product to the selected product using cosine similarity method
    def findSimilarProducts(self):
        similarProductsList = []
        currentProductData = self.createDataForCurrentProduct()
        productData = self.createDataForProducts()
        similarityArray = cosine_similarity(currentProductData,productData)
        count = 0
        for product in JointProductPurchase.objects.filter():
            similarProductsList.append((product.productID_id, similarityArray[0][count]))
            count+=1
        similarProductsList.sort(key=lambda x:x[1], reverse=True)
        return similarProductsList[0][0]
    
    def calculate(self):
        productList = []
        self.selectedProduct = Product.objects.filter(productID = self.findSimilarProducts())[0]
        complimentaryProductsList = self.findComplimentaryProducts()
        productList = self.findMostCommonComplimentaryProducts(complimentaryProductsList)
        return productList[:self.k]
