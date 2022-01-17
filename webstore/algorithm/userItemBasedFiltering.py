from webstore.models import PurchaseHistory, UserRatedProduct, Product, User, Tag, ProductWithTag
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

#Algorithm compares users based on previous purchases and than filters items of those users based on tags
class UserItemBasedFiltering:
    def __init__(self, k, categoryID, subCategoryID, loggedUser, selectedProduct):
        self.k = k
        self.categoryID = categoryID
        self.subCategoryID = subCategoryID
        self.loggedUser = loggedUser
        self.selectedProduct = selectedProduct


    #Create data set for currently logged user
    def createLoggedUserDataTable(self):
        loggedUserData = np.zeros((1,Product.objects.filter().count()))
        
        column = 0
        for product in Product.objects.filter():
            if(PurchaseHistory.objects.filter(cartID_id = self.loggedUser.userID, productID_id = product.productID).exists()):
                loggedUserData[0][column] = 1
            if(UserRatedProduct.objects.filter(userID_id = self.loggedUser.userID, productID_id = product.productID).exists()):
                loggedUserData[0][column] = 2
            if(PurchaseHistory.objects.filter(cartID_id = self.loggedUser.userID, productID_id = product.productID).exists() and 
            UserRatedProduct.objects.filter(userID_id = self.loggedUser.userID, productID_id = product.productID).exists()):
                loggedUserData[0][column] = 3
            column+=1
        return loggedUserData

    #Create ND array of users and which products they bought/rated
    #1-user bought the product, 2-user rated the product, 3-user bought and rated the product
    def createDataTable(self):
        userProductData = np.zeros((User.objects.filter().count()-1,Product.objects.filter().count()))
        row = 0
        for user in User.objects.filter():
            if(user.userID == self.loggedUser.userID):
                continue
            column = 0
            for product in Product.objects.filter():
                if(PurchaseHistory.objects.filter(cartID_id = user.userID, productID_id = product.productID).exists()):
                    userProductData[row][column] = 1
                if(UserRatedProduct.objects.filter(userID_id = user.userID, productID_id = product.productID).exists()):
                    userProductData[row][column] = 2
                if(PurchaseHistory.objects.filter(cartID_id = user.userID, productID_id = product.productID).exists() and 
                UserRatedProduct.objects.filter(userID_id = user.userID, productID_id = product.productID).exists()):
                    userProductData[row][column] = 3
                column+=1
            row+=1
        return userProductData

    #Finds and returns the most similar user to the selected user
    def findMostSimilar(self, similarityArray):
        row = 0
        currentUser = None
        currentSimilarityRatio = 0
        for user in User.objects.filter():
            if(user.userID == self.loggedUser.userID):
                continue
            if(similarityArray[0][row] >= currentSimilarityRatio):
                currentSimilarityRatio = similarityArray[0][row]
                currentUser = user
            row+=1
        return currentUser

    #Finds and return a list of k most similar products
    def findMostSimilarProduct(self, similarityArray, mostSimilarUserID):
        productList = []
        sortedProductList = []
        count = 0
        for product in PurchaseHistory.objects.filter(cartID_id = mostSimilarUserID):
            productList.append((product.productID_id, similarityArray[0][count]))
            count+=1
        
        productList.sort(reverse=True, key=lambda x:x[1])
        count = 0
        for productID, similarity in productList:
            sortedProductList.append(Product.objects.filter(productID = productID)[0])
            if(count == self.k):
                break
        return sortedProductList

    #Compares purchase histories of current and similar user, return a list of most similar products
    def comparePurchaseHistories(self, similarUserProductList, mostSimilarUserID):
        selectedProductDataTable = np.zeros((1,Tag.objects.filter().count()+2))
        column = 0

        selectedProductDataTable[0][column] = int(self.selectedProduct.price)
        selectedProductDataTable[0][column+1] = int(self.selectedProduct.rank)
        column = 2
        for tag in Tag.objects.filter():
            if(ProductWithTag.objects.filter(productID_id = self.selectedProduct.productID, tagID_id = tag.tagID).exists()):
                selectedProductDataTable[0][column] = 1
            column+=1
        
        productsDataTable = np.zeros((PurchaseHistory.objects.filter(cartID_id = mostSimilarUserID).count(),Tag.objects.filter().count()+2))
        row = 0
        for product in PurchaseHistory.objects.filter(cartID_id = mostSimilarUserID):
            if(product.productID_id == self.selectedProduct.productID):
                continue
            column = 0
            product = Product.objects.filter(productID = product.productID_id)[0]
            productsDataTable[row][column] = int(product.price)
            column+=1
            productsDataTable[row][column] = int(product.rank)
            column+=1
            for tag in Tag.objects.filter():
                if(ProductWithTag.objects.filter(productID_id = product.productID, tagID_id = tag.tagID).exists()):
                    productsDataTable[row][column] = 1
                column+=1
            row+=1
        similarityArray = cosine_similarity(selectedProductDataTable,productsDataTable)
        productList = self.findMostSimilarProduct(similarityArray, mostSimilarUserID)
        return productList

    def calculate(self):
        productList = []
        similarUserProductList = []

        userProductData = self.createDataTable()
        currentUserData = self.createLoggedUserDataTable()
        similarityArray = cosine_similarity(currentUserData,userProductData)
        mostSimilarUser = self.findMostSimilar(similarityArray)

        for purchasedProduct in PurchaseHistory.objects.filter(cartID_id = mostSimilarUser.userID):
            similarUserProductList.append(Product.objects.filter(productID = purchasedProduct.productID_id)[0])
        
        productList = self.comparePurchaseHistories(similarUserProductList, mostSimilarUser.userID)

        return productList
