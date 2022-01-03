from webstore.models import Product, JointProductPurchase
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

#Algorithm finds which products are usually bought together and bases it's recommendation from that
class ComplementaryProducts:
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
    
    def calculate(self):
        productList = []
        complimentaryProductsList = self.findComplimentaryProducts()
        productList = self.findMostCommonComplimentaryProducts(complimentaryProductsList)
        return productList[:self.k]
