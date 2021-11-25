from django.shortcuts import redirect, render
from webstore.models import Product, ProductInCategory, SubCategory, User, Category

# Create your views here.
loggedUser = None
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
product_dict = {}
login_dict = {}

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
    if loggedUser is not None:
        return redirect("home")
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            user = (User.objects.filter(userName = username, password = password))
            if user:
                loggedUser = LoggedUser(user[0].userID, user[0].userName, user[0].password, user[0].name, user[0].surname)
                categories_dict["logged"] = True
                subCategories_dict["logged"] = True
                products_dict["logged"] = True
                product_dict["logged"] = True
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
    loggedUser = None
    categories_dict["logged"] = False
    subCategories_dict["logged"] = False
    products_dict["logged"] = False
    product_dict["logged"] = False
    login_dict["attempted"] = False
    return render(request, "webstore/login.html")

#Finds a specific URL based on selected category, subcategory or product and renders HTML
def products(request):
    if("subcategory" in request.GET.keys()):
        fillProducts(request)
        return render(request, "webstore/subcategory.html", products_dict)
    elif("product" in request.GET.keys()):
        fillProduct(request.GET["product"])
        return render(request, "webstore/product.html", product_dict)
    else:
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
def fillProducts(request):
    global products_dict
    products_dict["product"] = []
    subcategoryID = None
    for subcategory in SubCategory.objects.filter():
        if(subcategory.urlName == request.GET['subcategory']):
            subcategoryID = subcategory.subCategoryID
            break
    if(subcategoryID is None):
        raise Exception("subcategory not found!")
    for productInCategory in ProductInCategory.objects.filter():
        if(productInCategory.subCategoryID_id == subcategoryID):
            products_dict["product"].append(Product.objects.filter(productID = productInCategory.productID_id)[0])

#Fills product_dict with a specific product
def fillProduct(productID):
    global product_dict
    product = Product.objects.filter(productID = productID)
    if(product):
        product_dict["product"] = product[0]
    else:
        product_dict["product"] = None