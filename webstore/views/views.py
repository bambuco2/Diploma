from typing import Match
from django.shortcuts import redirect, render
from webstore.algorithm.cmplementaryOfSimilarProducts import ComplementaryOfSimilarProducts
from webstore.algorithm.complementaryProducts import ComplementaryProducts
from webstore.algorithm.productBasedComparison import ProductBasedComparison
from webstore.algorithm.userBasedComparison import UserBasedComparison
from webstore.algorithm.userItemBasedFiltering import UserItemBasedFiltering
from webstore.models import JointProductPurchase, Product, ProductInCart, ProductInCategory, ProductWithTag, PurchaseHistory, SubCategory, User, Category
from webstore.algorithm.mostPopular import MostPopular

# Create your views here.
loggedUser = None
selectedProduct = None
class LoggedUser:
    logged = False
    def __init__(self, userID, userName, password, name, surname):
        self.userID = userID
        self.userName = userName
        self.password = password
        self.name = name
        self.surname = surname
        self.logged = True

#Prepare all dictionaries
categories_dict = {"category" : Category.objects.filter()}
categories_dict["logged"] = False
subCategories_dict = {}
subCategories_dict["logged"] = False
products_dict = {}
productsInCart_dict = {}
product_dict = {}
login_dict = {}
categories_dict["algorith"] = 0
subCategories_dict["algorith"] = 0
products_dict["algorith"] = 0
product_dict["algorith"] = 0
login_dict["algorith"] = 0
productsInCart_dict["algorith"] = 0

#Create subcategory dictionary with category and subcategory info
for category in Category.objects.filter():
    name = category.urlName.split("-")
    subCategories_dict[name[0]] = []
for subCategory in SubCategory.objects.filter():
    cat = (Category.objects.filter(categoryID = subCategory.categoryID_id))
    name = cat[0].urlName.split("-")
    subCategories_dict[name[0]].append(subCategory)

#Renders Home.html based on whether user is in session or not
def home(request):
    if(loggedUser is not None and loggedUser.logged):
        return render(request, "webstore/homeLogged.html", categories_dict)
    return render(request, "webstore/home.html", categories_dict)

#Cheks username and password, starts user session, renders Home.html
def login(request):
    global loggedUser
    global categories_dict
    global subCategories_dict
    global products_dict
    global product_dict
    global login_dict
    global productsInCart_dict
    if loggedUser is not None:
        return redirect("home")
    if request.method == "POST" and "username" in request.POST and "password" in request.POST:
        username = request.POST["username"]
        password = request.POST["password"]
        if username and password:
            user = (User.objects.filter(userName = username, password = password))
            if user:
                loggedUser = LoggedUser(user[0].userID, user[0].userName, user[0].password, user[0].name, user[0].surname)
                categories_dict["logged"] = True
                subCategories_dict["logged"] = True
                products_dict["logged"] = True
                product_dict["logged"] = True
                productsInCart_dict["logged"] = True
                login_dict["attempted"] = False
                return redirect("home")
            else:
                login_dict["attempted"] = True
        else:
                login_dict["attempted"] = True
        return render(request, "webstore/login.html", login_dict)
    else:
        return render(request, "webstore/login.html", login_dict)

#End user session, resets all dictionaries and renders Login.html
def logout(request):
    global loggedUser
    global categories_dict
    global subCategories_dict
    global products_dict
    global product_dict
    global login_dict
    global productsInCart_dict
    loggedUser = None
    categories_dict["logged"] = False
    subCategories_dict["logged"] = False
    products_dict["logged"] = False
    product_dict["logged"] = False
    login_dict["attempted"] = False
    productsInCart_dict["logged"] = False
    return redirect("login")

#Finds a specific URL based on selected category, subcategory or product and renders HTML
def products(request):
    global selectedProduct
    selectedProduct = None
    if("subcategory" in request.GET.keys()):
        fillProducts(request.GET['subcategory'])
        return render(request, "webstore/subcategory.html", products_dict)
    elif("product" in request.GET.keys()):
        fillProduct(request.GET["product"])
        return render(request, "webstore/product.html", product_dict)
    else:
        categoryID = findCategoryID(request.path.replace('/', ''))
        recommendProduct(3, categoryID, None)
        if(request.path == "/household-appliances/"):
            return render(request, "webstore/categories/household-appliances.html",subCategories_dict)
        elif(request.path == "/fashion/"):
            return render(request, "webstore/categories/fashion.html", subCategories_dict)
        elif(request.path == "/fitness/"):
            return render(request, "webstore/categories/fitness.html", subCategories_dict)
        elif(request.path == "/yard-tools/"):
            return render(request, "webstore/categories/yard-tools.html", subCategories_dict)
        elif(request.path == "/audio-video/"):
            return render(request, "webstore/categories/audio-video.html", subCategories_dict)
        return render(request, "webstore/categories/products.html", subCategories_dict)

#Fills products_dict with all products belonging in a specific subcategory
def fillProducts(subCategoryName):
    global products_dict
    products_dict["product"] = []
    subcategoryID = None
    subcategoryID = findSubcategoryID(subCategoryName)
    if(subcategoryID is None):
        raise Exception("subcategory not found!")
    for productInCategory in ProductInCategory.objects.filter():
        if(productInCategory.subCategoryID_id == subcategoryID):
            products_dict["product"].append(Product.objects.filter(productID = productInCategory.productID_id)[0])
    recommendProduct(3, None, subcategoryID)

#Finds and returns ID of subcategory
def findSubcategoryID(subcategoryName):
    subCategoryID = None
    for subcategory in SubCategory.objects.filter():
        if(subcategory.urlName == subcategoryName):
            subCategoryID = subcategory.subCategoryID
            break
    return subCategoryID

def findSubcategoryIDWithProductID(productID):
    subcategoryID = ProductInCategory.objects.filter(productID_id = productID)[0].subCategoryID_id
    return subcategoryID

#Finds and returns ID of category
def findCategoryID(categoryName):
    categoryID = None
    for category in Category.objects.filter():
        if(category.urlName == categoryName):
            categoryID = category.categoryID
            break
    return categoryID

def findCategoryIDWithProductID(productID):
    return ProductInCategory.objects.filter(productID_id = productID)[0].categoryID_id

#Fills product_dict with a specific product
def fillProduct(productID):
    global product_dict
    global selectedProduct
    product = Product.objects.filter(productID = productID)
    if(product):
        product_dict["product"] = product[0]
        product_dict["selectedProduct"] = product[0]
        selectedProduct = product[0]
    else:
        product_dict["product"] = None
        product_dict["selectedProduct"] = None
    subCategoryID = findSubcategoryIDWithProductID(productID)
    categoryID = findCategoryIDWithProductID(productID)
    recommendProduct(3, categoryID, subCategoryID)

#Handles showing cart.html and adding/removing specific product to users cart
def cart(request):
    global productsInCart_dict
    productsInCart_dict["CheckoutFinish"] = False
    if(loggedUser is not None):
        #User adds or remove from shopping cart
        if request.method == "POST":
            if("productID" in request.POST):
                if("Remove" in request.POST):
                    removeProductFromCart(loggedUser.userID, request.POST["productID"])
                else:
                    addProductToCart(loggedUser.userID, request.POST["productID"])
            elif("Checkout" in request.POST):
                if(checkoutCart(loggedUser.userID)):
                    productsInCart_dict["CheckoutFinish"] = True
        fillCart(loggedUser.userID)
        return render(request, "webstore/cart.html", productsInCart_dict)
    else:
        return render(request, "webstore/login.html")

#Checks if product is already in a users cart
def isProductInCart(userID, productID):
    if(ProductInCart.objects.filter(cartID_id = userID, productID_id = productID).exists()):
        return True
    return False

#Fills productsInCart_dict with products in a users cart
def fillCart(userID):
    global productsInCart_dict
    productsInCart_dict["product"] = []
    productsInCart_dict["size"] = 0
    for productInCart in ProductInCart.objects.filter(cartID_id = userID):
        productsInCart_dict["product"].append(productInCart)
        productsInCart_dict["size"]+=1
    return True

#Removes product from shopping cart
def removeProductFromCart(userID, productID):
    product = ProductInCart.objects.filter(cartID_id = userID, productID_id = productID)
    if(product.exists()):
        product[0].delete()
        return True    
    return False

#Adds product to shopping cart if already exists increase quantity
def addProductToCart(userID, productID):
    if(not isProductInCart(userID, productID)):
        product = ProductInCart(quantity="1", cartID_id=userID, productID_id=productID)
        product.save()
    #Product already in shopping cart, increase quantity
    else:
        product = ProductInCart.objects.filter(cartID_id = userID, productID_id = productID)
        product.update(quantity=product[0].quantity+1)
    return True

#Adds/alters jointProductPurchase table
def handleJointPurchase(jointPurchaseProducts):
    for product in jointPurchaseProducts:
        count=0
        primaryProductID = product
        jointProductPurchaseString = ""
        for productID in jointPurchaseProducts:
            if(productID is not primaryProductID):
                jointProductPurchaseString = jointProductPurchaseString + str(productID) + ","
            count+=1
        if(JointProductPurchase.objects.filter(productID_id=primaryProductID).exists()):
            jointProductPurchaseString = JointProductPurchase.objects.filter(productID_id=primaryProductID)[0].relatedProducts + jointProductPurchaseString
            JointProductPurchase.objects.filter(productID_id=primaryProductID).update(relatedProducts = jointProductPurchaseString)
        else:
            purchase = JointProductPurchase(productID_id=primaryProductID, relatedProducts=jointProductPurchaseString)
            purchase.save()
    return None

#Handles checkout logic, writes into purchase history DB table
def checkoutCart(userID):
    jointPurchaseProducts = []
    for product in ProductInCart.objects.filter(cartID_id = userID):
        purchase = PurchaseHistory(quantity=product.quantity, cartID_id=userID, productID_id=product.productID_id)
        jointPurchaseProducts.append(product.productID_id)
        purchase.save()
        removeProductFromCart(userID, product.productID_id)
    if(len(jointPurchaseProducts)>1):
        handleJointPurchase(jointPurchaseProducts)
    return True

#Uses the specific algorithm to recommend K-number of products and fills products_dict, product_dict
def recommendProduct(k, categoryID, subCategoryID):
    global products_dict
    global product_dict
    products_dict["recommended"] = []
    product_dict["recommended"] = []
    subCategories_dict["recommended"] = []

    algorithm = selectAlgorithm(k, categoryID, subCategoryID)
    productList = algorithm.calculate()

    if(subCategoryID is not None):
        for prod in productList:
            if(prod not in products_dict["recommended"]):
                products_dict["recommended"].append(prod)
            if(prod not in product_dict["recommended"]):
                product_dict["recommended"].append(prod)
    elif(categoryID is not None):
        for prod in productList:
            if(prod not in subCategories_dict["recommended"]):
                subCategories_dict["recommended"].append(prod)
    else:
        return False
    return True

#Selects and returns the right algorithm object
def selectAlgorithm(k, categoryID, subCategoryID):
    if(products_dict["algorith"] == 0):
        algorithm = MostPopular(k, categoryID, subCategoryID)
    elif(products_dict["algorith"] == 1 and loggedUser is not None):
        algorithm = UserBasedComparison(k, categoryID, subCategoryID, loggedUser)
    elif(products_dict["algorith"] == 2 and selectedProduct is not None):
        algorithm = ProductBasedComparison(k, categoryID, subCategoryID, selectedProduct)
    elif(products_dict["algorith"] == 3 and selectedProduct is not None):
        algorithm = ComplementaryProducts(k, categoryID, subCategoryID, selectedProduct)
    elif(products_dict["algorith"] == 4 and selectedProduct is not None):
        algorithm = ComplementaryOfSimilarProducts(k, categoryID, subCategoryID, selectedProduct)
    elif(products_dict["algorith"] == 5 and selectedProduct is not None and loggedUser is not None):
        algorithm = UserItemBasedFiltering(k, categoryID, subCategoryID, loggedUser, selectedProduct)
    else:
        algorithm = MostPopular(k, categoryID, subCategoryID)
    return algorithm

#Handles algorithm selection UI and logic
def algorithm(request):
    global categories_dict
    global subCategories_dict
    global products_dict
    global product_dict
    global login_dict
    global productsInCart_dict
    if(request.POST['algorithm'] == "popular"):
        categories_dict["algorith"] = 0
        subCategories_dict["algorith"] = 0
        products_dict["algorith"] = 0
        product_dict["algorith"] = 0
        login_dict["algorith"] = 0
        productsInCart_dict["algorith"] = 0
    elif(request.POST['algorithm'] == "user"):
        categories_dict["algorith"] = 1
        subCategories_dict["algorith"] = 1
        products_dict["algorith"] = 1
        product_dict["algorith"] = 1
        login_dict["algorith"] = 1
        productsInCart_dict["algorith"] = 1
    elif(request.POST['algorithm'] == "itemToItem"):
        categories_dict["algorith"] = 2
        subCategories_dict["algorith"] = 2
        products_dict["algorith"] = 2
        product_dict["algorith"] = 2
        login_dict["algorith"] = 2
        productsInCart_dict["algorith"] = 2
    elif(request.POST['algorithm'] == "complimentary"):
        categories_dict["algorith"] = 3
        subCategories_dict["algorith"] = 3
        products_dict["algorith"] = 3
        product_dict["algorith"] = 3
        login_dict["algorith"] = 3
        productsInCart_dict["algorith"] = 3
    elif(request.POST['algorithm'] == "similar"):
        categories_dict["algorith"] = 4
        subCategories_dict["algorith"] = 4
        products_dict["algorith"] = 4
        product_dict["algorith"] = 4
        login_dict["algorith"] = 4
        productsInCart_dict["algorith"] = 4
    elif(request.POST['algorithm'] == "deepRecs"):
        categories_dict["algorith"] = 5
        subCategories_dict["algorith"] = 5
        products_dict["algorith"] = 5
        product_dict["algorith"] = 5
        login_dict["algorith"] = 5
        productsInCart_dict["algorith"] = 5
    return redirect(request.META['HTTP_REFERER'])