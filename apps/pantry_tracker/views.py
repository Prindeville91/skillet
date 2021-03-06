from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from datetime import datetime, timezone
from .models import *
import re, bcrypt

#Where we start. If logged in will redirect to dash
#If not logged in - redirect to log in/register view
def landing(request):
    if 'user_id' in request.session:
        return redirect('/dashboard')
    else:
        return render(request,"landing.html")

#Logout wipes the session out, dumps user back to landing
def logout(request):

    request.session.clear()
    return redirect('/')

#This is the view for showing a login window with the form
#By default, this will be the first thing a new user sees
def login(request):
    return render(request, 'login.html')

#View for processing the actual user login
def loginUser(request):
    if request.method == 'POST':
        errors = User.objects.login_validator(request.POST)
        if len(errors):
            for tag, error in errors.items():
                messages.error(request, error, extra_tags = tag)
            return redirect('/login')
        else:
            email = request.POST['loginEmail']
            user = User.objects.get(email=email)
            request.session['user_id'] = user.id
            access_level = user.access_level
            #check if the user logging in is the admin
            if access_level == 9 or access_level == 7:
                return redirect('/admin_dash')
            else:
                return redirect('/dashboard')
    return redirect('/dashboard') 

#Render registration form
def register(request):
    return render(request, 'register.html')

#Process registration
def registerUser(request):
    if request.method == 'POST':
        errors = User.objects.registrator_validator(request.POST)
        if len(errors):
            for tag, error in errors.items():
                messages.error(request, error, extra_tags = tag)
            return redirect('/register')
        else:
            #new addition, for establishing admins
            #admins will be able to promote others
            if User.objects.all().count()==0:
                access_level = 9
            elif 'access_level' in request.POST:
                access_level=request.POST['access_level']
            else:
                access_level = 1
            #Make an empty pantry for the new user
            pantry = Pantry.objects.create()

            user = User.objects.create(first_name = request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'], password=bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()),access_level=access_level, pantry=pantry)

            GroceryList.objects.create(user=user)
            request.session['user_id'] = user.id
            
            if user.access_level==9 or user.access_level==7:
                return redirect('/admin_dash')
    return redirect('/dashboard')

def user_delete(request,id):
    user = User.objects.get(id=id)
    if user.access_level == 1:
        user.delete()
    else:
        print('!-'*88)
        print("Can't delete admins!!!")
    return redirect('/admin_dash')

#User main page - all the content except profile editing
def dashboard(request):
    request.session['location']="/dashboard"
    if 'user_id' not in request.session:
        return redirect('/')
    user=User.objects.get(id=request.session['user_id'])
    id = request.session['user_id']
    request.session['diets'] = []
    name=user.first_name+" "+user.last_name
    list_to_show = []
    if 'grocery_list' not in request.session:
        request.session['grocery_list']={}
    for item in request.session['grocery_list']:
        prod = Product.objects.get(id=item)
        qty = request.session['grocery_list'][item]
        temp = {
            'id':item,
            'name':prod.name,
            'quantity':qty,
        }
        list_to_show.append(temp)

    pantrylist=[]
    for product in user.pantry.product.order_by('name'):
        shelfLife = Product.objects.get(id = product.id).shelf_life
        if shelfLife == 0:
            time=0
        else:
            today = datetime.now(timezone.utc)
            boughtItemOn = product.created_at
            timeOnShelf = today - boughtItemOn
            timeToSpoil=shelfLife-timeOnShelf.days
            if timeToSpoil<1:
                time=-1
            else:
                time=timeToSpoil
        temp={
            'name':product.name,
            'id':product.id,
            'img':product.image,
            'quantity':product.quantity,
            'category':product.product_category,
            'time': time,
        }
        pantrylist.append(temp)
    
    dietlist=[]
    for diet in user.diets.all():
        dietlist.append(diet.preference)
    joined=User.objects.get(id = id).created_at
    joined=joined.strftime("%B %d, %Y")
    context = {
        'username':name,
        'access_level': user.access_level,
        'pantrylist':pantrylist,
        'grocerylist':list_to_show,
        'joined': joined,
        'dietlist':dietlist,
    }
    return render(request, 'dashboard.html',context)
#**********************************************************

# Take user to the page for profile editing
def editProfile(request,id):
    if 'user_id' not in request.session:
        return redirect('/')
    request.session['location']="/editProfile"
    user=User.objects.get(id=id)
    dietlist=[]
    for y in Diet.objects.all():
        if y in user.diets.all():
            check='checked'
        else:
            check=''
        temp = {
            'diet':y.preference,
            'id':y.id,
            'checked':check
        }
        dietlist.append(temp)
    context = {
        'user':{
            'first_name':user.first_name,
            'last_name':user.last_name,
            'email':user.email,
            'id':id,
        },
        'dietlist':dietlist
    }
    return render(request,"edit.html", context)

# Processes whatever changes the users submits
def update_profile(request,id):
    request.session['errors']={}
    if request.method=="POST":
        errors = User.objects.updator_validator(request.POST)
        if len(errors):
            for tag, error in errors.items():
                messages.error(request, error, extra_tags = tag)
            route = '/editProfile/' + str(request.session['user_id'])
            return redirect(route)
        else:
            user = User.objects.get(id=request.session['user_id'])
            user.first_name=request.POST['first_name']
            user.last_name=request.POST['last_name']
            user.email=request.POST['email']
            for diet in Diet.objects.all():
                print("<>"*40)
                print(diet.id)
                if str(diet.id) in request.POST and diet not in user.diets.all():
                    print(diet.preference)
                    print("The diet is being added to the user")
                    user.diets.add(diet)
                elif str(diet.id) not in request.POST and diet in user.diets.all():
                    print(diet.preference)
                    print ("The diet is being removed from the user")
                    user.diets.remove(diet)
                else:
                    print("No change")
                print("*"*80)
            user.save()
            print("$"*80)
            print(request.POST)
    return redirect('/dashboard') 

#**********************************************************

def admin_dash(request):
    if 'user_id' not in request.session:
        return redirect('/')
    request.session['location']="/admin_dash"
    u=User.objects.get(id=request.session['user_id'])
    if u.access_level == 1:
        return redirect('/dashboard')
    userlist = []
    for user in User.objects.all():
        temp = {
            'id': user.id,
            'first_name':user.first_name,
            'last_name':user.last_name,
            'email':user.email,
            'access_level':user.access_level,
            'pantry':user.pantry.id,
        }
        userlist.append(temp)
    productlist=[]
    vendor=User.objects.first().pantry.product.all()
    for product in vendor:
        temp = {
            'id': product.id,
            'name':product.name,
            'desc':product.description,
            'quantity':product.quantity,
            'unit':product.measure,
            'shelf_life':product.shelf_life,
            'price':product.price,
            'owner':product.pantry.user.first().first_name,
        }
        productlist.append(temp)
    recipelist=[]
    for recipe in Recipe.objects.all():
        #this is you, the admin
        author = recipe.author.first_name + " " + recipe.author.last_name
        temp = {
            'id': recipe.id,
            'name':recipe.name,
            'desc':recipe.desc,
            'author': author,
            'author_id':recipe.author.id
        }
    context = {
        'userlist':userlist,
        'productlist':productlist,
        'recipelist':recipelist,
        'adminname':u.first_name
    }
    return render(request,"admin-templates/admin-dash.html",context)

def add_product(request):
    if request.method == 'POST':
        errors = {}
        if len(errors):
            print(errors)
        else:
            price=request.POST['price']
            Product.objects.create(name=request.POST['name'], description=request.POST['desc'],measure=request.POST['unit'],shelf_life=request.POST['shelf_life'],quantity=1, price=price, pantry=Pantry.objects.get(id=1),image='flour.jpg')
            #NOTE!! This is making products in Andy's pantry. SUBJECT TO CHANGE
    return redirect('/admin_dash')

def recipe_builder(request):
    if 'user_id' not in request.session:
        return redirect('/')
    request.session['location']="/recipe_builder"
    if 'recipe' not in request.session:
        request.session['recipe']={
            'name':'',
            'desc':'',
            'components':{}
        }
    complist = []
    for comp in request.session['recipe']['components']:
        p=Product.objects.get(id=comp)
        q=request.session['recipe']['components'][comp]
        temp = {
            'id':comp,
            'name':p.name,
            'unit':p.measure,
            'quantity':q
        }
        complist.append(temp)

    if 'recipe_search' not in request.session:
        request.session['recipe_search']=''
    productlist=[]
    p = User.objects.get(id=1).pantry.product
    for product in p.filter(name__contains=request.session['recipe_search']):
        temp = {
            'id': product.id,
            'name':product.name,
            'desc':product.description,
            'unit':product.measure,
            'shelf_life':product.shelf_life,
            'price':product.price
        }
        productlist.append(temp)
    context = {
        'complist':complist,
        'productlist':productlist
    }
    return render(request,"admin-templates/recipe_editor.html",context)

#**********************************************************
#prepares components to go into the recipe
def add_to_recipe(request):
    if request.method == 'POST':
        product_id=request.POST['id']
        quantity=int(request.POST['quantity'])
        if product_id not in request.session['recipe']['components']:
            request.session['recipe']['components'][product_id]=quantity
        else:
            request.session['recipe']['components'][product_id]+=quantity
        request.session['recipe']=request.session['recipe']
    return redirect('/recipe_builder')

#decrease the amount of current component in the recipe
def recip_decr(request,id):
    request.session['recipe']['components'][id]-=1
    count=request.session['recipe']['components'][id]
    request.session['recipe']=request.session['recipe']
    if count==0:
        request.session['recipe']['components'].pop(id,None)
    return redirect('/recipe_builder')

#increase the amount of current component in the recipe
def recip_incr(request,id):
    request.session['recipe']['components'][id]+=1
    request.session['recipe']=request.session['recipe']
    return redirect('/recipe_builder')

#remove the current component in the recipe
def recip_remove(request,id):
    request.session['recipe']['components'].pop(id,None)
    request.session['recipe']=request.session['recipe']
    return redirect('/recipe_builder')
#**********************************************************

#response to the search filter
def recipe_search(request):
    if request.method=='POST':
        request.session['recipe_search']=param=request.POST['recipe_search']
    return redirect('/recipe_builder')

#ditch the filter, show every product available
def recipe_search_clear(request):
    request.session['recipe_search']=""
    return redirect('/recipe_builder')

#clear out everything, but keep the session to start again
def recipe_clear(request):
    request.session['recipe']={
            'name':'',
            'desc':'',
            'components':{}
        }
    return redirect('/recipe_builder')

def complete_recipe(request):
    return redirect('/admin_dash')

#**********************************************************
#render shopping list page
def shopping_list(request,id):
    request.session['location']="grocery"
    if 'user_id' not in request.session:
        return redirect('/')
    #set up a blank filter
    if 'shop_search' not in request.session:
        request.session['shop_search']=''
    if 'grocery_list' not in request.session:
        request.session['grocery_list']={}
    list_to_show = []
    for item in request.session['grocery_list']:
        prod = Product.objects.get(id=item)
        qty = request.session['grocery_list'][item]
        temp = {
            'id':item,
            'name':prod.name,
            'quantity':qty,
        }
        list_to_show.append(temp)
    #Make a list for 'buying options'
    shopping_options = []
    user=User.objects.get(id=id)
    vendor = User.objects.get(id=1).pantry
    for product in vendor.product.filter(name__contains=request.session['shop_search']):
        temp = {
            'id': product.id,
            'name':product.name,
            'product_category':product.product_category,
            'measure':product.measure,
            'shelf_life':product.shelf_life,
            'price':product.price
        }
        shopping_options.append(temp)
    context={
        'username':user.first_name,
        'grocerylist':list_to_show,
        'shopping_options':shopping_options,
    }
    return render(request,"grocery.html",context)

def add_groceries(request):
    #May need update with p_id as integer
    if request.method == 'POST':
        p_id = request.POST['id']
        p_quant = int(request.POST['quantity'])
        if p_id in request.session['grocery_list']:
            request.session['grocery_list'][p_id]+=p_quant
        else:
            request.session['grocery_list'][p_id]=p_quant
        request.session['grocery_list']=request.session['grocery_list']
        # else:
        #     product.pk=None
        #     product.pantry=shopping_list
        #     product.save()
    if request.session['location']=="grocery":    
        route = 'shopping_list/'+str(request.session['user_id'])
    else:
        route = request.session['location']
    return redirect(route)
def grocery_search(request):
    if request.method=='POST':
        request.session['shop_search']=request.POST['shopping_search']
    route = 'shopping_list/'+str(request.session['user_id'])
    return redirect(route)

def shop_search_clear(request):
    request.session['shop_search']=""
    if request.session['location']=="grocery":
        route = 'shopping_list/'+str(request.session['user_id'])
    else:
        route = request.session['location']
    return redirect(route)

def grocery_incr(request,id):
    request.session['grocery_list'][id]+=1
    request.session['grocery_list']=request.session['grocery_list']
    if request.session['location']=="grocery":
        route = 'shopping_list/'+str(request.session['user_id'])
    else:
        route = request.session['location']
    return redirect(route)

def grocery_decr(request,id):
    request.session['grocery_list'][id]-=1
    if request.session['grocery_list'][id]==0:
        request.session['grocery_list'].pop(id,None)
    request.session['grocery_list']=request.session['grocery_list']
    if request.session['location']=="grocery":
        route = 'shopping_list/'+str(request.session['user_id'])
    else:
        route = request.session['location']
    return redirect(route)

def grocery_remove(request,id):
    request.session['grocery_list'].pop(id,None)
    request.session['grocery_list']=request.session['grocery_list']
    if request.session['location']=="grocery":
        route = 'shopping_list/'+str(request.session['user_id'])
    else:
        route = request.session['location']
    return redirect(route)

def done_shopping(request,id):
    user=User.objects.get(id=request.session['user_id'])
    pan = Pantry.objects.get(user=user)
    prod = Product.objects.get(id=id)
    prod.pk = None
    prod.quantity = prod.quantity * request.session['grocery_list'][id]
    prod.pantry=pan
    prod.save()
    request.session['grocery_list'].pop(id,None)
    request.session['grocery_list']=request.session['grocery_list']
    if request.session['location']=="grocery":
        route = 'shopping_list/'+str(request.session['user_id'])
    else:
        route = request.session['location']
    return redirect(route)

def reduce_in_pantry(request,id):
    user = User.objects.get(id=request.session['user_id'])
    pantry = Pantry.objects.get(user=user)
    product = pantry.product.get(id=id)
    print("%"*80)
    print(product.quantity)
    product.quantity=product.quantity-1
    print(product.quantity)
    product.save()
    if product.quantity == 0:
        product.delete()
    return redirect('/dashboard')

def remove_from_pantry(request,id):
    user = User.objects.get(id=request.session['user_id'])
    pantry = Pantry.objects.get(user=user)
    product = pantry.product.get(id=id)
    product.delete()
    return redirect('/dashboard')