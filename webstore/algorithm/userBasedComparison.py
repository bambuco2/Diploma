from webstore.models import PurchaseHistory, UserRatedProduct, Product, User
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

#Algorithm comparing users and finding which ones resemble the most using cosine similarity measuring method
class UserBasedComparison:
    def __init__(self, k, categoryID, subCategoryID, loggedUser):
        self.k = k
        self.categoryID = categoryID
        self.subCategoryID = subCategoryID
        self.loggedUser = loggedUser
        self.userList = []
    
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
        userList = []
        for user in User.objects.filter():
            if(PurchaseHistory.objects.filter(cartID_id = user.userID).count()>0):
                userList.append(user)
        self.userList = userList
        userProductData = np.zeros((len(userList),Product.objects.filter().count()))
        row = 0
        for user in userList:
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
        for user in self.userList:
            if(user.userID == self.loggedUser.userID):
                continue
            if(similarityArray[0][row] >= currentSimilarityRatio):
                currentSimilarityRatio = similarityArray[0][row]
                currentUser = user
            row+=1
        return currentUser
    
    def calculate(self):
        productList = []
        userProductData = self.createDataTable()
        currentUserData = self.createLoggedUserDataTable()
        similarityArray = cosine_similarity(currentUserData,userProductData)
        mostSimilarUser = self.findMostSimilar(similarityArray)

        for purchasedProduct in PurchaseHistory.objects.filter(cartID_id = mostSimilarUser.userID):
            productList.append(Product.objects.filter(productID = purchasedProduct.productID_id)[0])
        
        if(len(productList)>self.k):
            return productList[:self.k]
        return productList
