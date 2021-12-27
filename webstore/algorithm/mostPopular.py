from webstore.models import Product, ProductInCategory, PurchaseHistory

#Most popular recommendation algorithm, finds most popular products within category or subcategory
class MostPopular:
    def __init__(self, k, categoryID, subCategoryID):
        self.k = k
        self.categoryID = categoryID
        self.subCategoryID = subCategoryID

    def sortByPurchaseNumber(self, productList):
        return productList['number']

    def sortFunction(self):
        purchasedProducts = {}
        productList = []

        for purchasedProduct in PurchaseHistory.objects.filter():
            if(purchasedProduct.productID_id in purchasedProducts):
                purchasedProducts[purchasedProduct.productID_id] =purchasedProducts[purchasedProduct.productID_id] + purchasedProduct.quantity
            else:
                purchasedProducts[purchasedProduct.productID_id] = purchasedProduct.quantity
        for product in purchasedProducts.keys():
            productList.append({'productID' : product, 'number' : purchasedProducts[product]})
        return sorted(productList, key=self.sortByPurchaseNumber)
    
    def calculate(self):
        productList = []
        productListSorted = []
        purchasedProducts = self.sortFunction()

        if(self.categoryID is not None):
            for product in ProductInCategory.objects.filter(categoryID_id = self.categoryID):
                productList.append(Product.objects.filter(productID = product.productID_id)[0])
        elif(self.subCategoryID is not None):
            for product in ProductInCategory.objects.filter(subCategoryID_id = self.subCategoryID):
                productList.append(Product.objects.filter(productID = product.productID_id)[0])
        else:
            return None
        
        for product in purchasedProducts:
            product = Product.objects.filter(productID = product['productID'])[0]
            if(product in productList):
                productListSorted.append(product)
        return productListSorted[:self.k]