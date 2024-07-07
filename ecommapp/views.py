import json
from django.shortcuts import render,redirect
from numpy import delete

from ecommapp.constants import PaymentStatus
from .models import SIGN,product,Order
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.http import HttpResponse

# Create your views here.
def home(request):
    return  render(request,"home.html")

def gallery(request):
    return render(request,"gallery.html")

def services(request):
    return render(request,"services.html")

def contact(request):
    return render(request,"contact.html")

def about(request):
    return render(request,"about.html")

def products(request):
    p=product.objects.all()
    return render(request,"products.html",{'records':p})

def signup(request):
    try:
            if request.session['error_message']==1:
                msg1="Please create an account"
                del request.session['error_message']
    except:
        msg1=""            
    return render(request,"signup.html",{'msg1':msg1})

def signup_data(request):
    name=request.POST['name']
    address=request.POST['address']
    email=request.POST['email']
    phone=request.POST['phone']
    username=request.POST['username']
    password=request.POST['password']
    d=SIGN()
    d.name=name
    d.address=address
    d.email=email
    d.phone=phone
    d.username=username
    d.password=password
    d.save()
    return redirect('login')

def login(request):
    try:
            if request.session['error_message']==2:
                msg1="Please enter correct details"
                del request.session['error_message']
    except:
        msg1=""            

    return render(request,"login.html",{'msg1':msg1})

def login_data(request):
     if request.method=='POST':
        usern=request.POST['username']
        password=request.POST['password']

     print(usern)
     print(password)   
        
    
     try:
        signup_obj=SIGN.objects.get(username=usern)
        if((usern==signup_obj.username) and (password==signup_obj.password)):
            arr=[signup_obj.username,signup_obj.name,signup_obj.address,signup_obj.email,signup_obj.phone]
            request.session['user_info']=arr
            return redirect("/")

        else:
            request.session['error_message']=2
            return redirect("login")     
     except:
        request.session['error_message']=1
        return redirect("signup")
     

def logout(request):
    del request.session['user_info']
    return redirect("/")

def single_details(request,slug_id):
    item_obj=product.objects.get(name=slug_id)
    print(item_obj)
    return render(request,"single-details.html",{'item_records':item_obj})

def cart(request):
    btn=request.POST['test']
    print(btn)
    qn=request.POST['quantity']
    slug=request.POST['slug']
    print(qn,slug)
    item_obj=product.objects.get(slug=slug)
    
    if(btn=="buy"):
        print("Buy page")
        total1=int(qn)*int(item_obj.price)
        request.session['total_amount']=total1
        return redirect('/checkout')
    
    else:
        single_item={slug:[item_obj.product_image_set.all()[0].image.url,item_obj.name,item_obj.price,qn]}

        try:
            v=request.session['cart_info']
            f=0
            for x in v:
                if slug in x:
                    h=int(x[slug][-1])
                    h=h+int(qn)
                    x[slug][-1]=str(h)
                    f=1

            if(f==0):
                v.append(single_item)
                request.session['cart_info']=v
                

        except:
            request.session['cart_info']=[single_item]                   

        request.session['cart_count']=len(request.session['cart_info'])
        return redirect('/cart_us')
    
def cart_display(request):
    try:
        carts=request.session['cart_info']
        print(carts)
        request.session['cart_display_count']=True
        gross_value=0

        for i in carts:
            for k,v in i.items():
                gross_value+=int(v[-1])*int(v[-2])
        
        request.session['total_amount']=gross_value
        return render(request,"cart_display.html",{'records':carts})
    except:
        request.session['cart_display_count']=False
        return render(request,"cart_display.html")

def remove_cart(request,slug_id):
    c=0
    v=request.session['cart_info']
    print("=======",v)
    for i in v:
        if slug_id in i:
            print("sluggggggggg",slug_id)
            print("cccccccc=",c)
            break
        else:
            c+=1
        print("c=",c)
    v.pop(c)
    request.session['cart_info']=v
    request.session['cart_count']=len(request.session['cart_info'])
    return redirect('/cart_us')

def checkout(request):
       # razorpay integration
	if request.method == "POST":
		name = request.session['user_info'][1]
		print(name)
		amount = request.session['total_amount']
		print(amount)
		client = razorpay.Client(auth=('rzp_test_oycvuJtS3rWECD', 'jLfQXbhTFXBvMLb5t6RmKuqj'))
		razorpay_order = client.order.create(
            {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
            )
		print(razorpay_order)
		order = Order.objects.create(
        	name=name, amount=amount, provider_order_id=razorpay_order["id"]
        	)
		print(order)
		order.save()
		return render(
			request,
			"payment.html",
			{
				# "callback_url": "http://" + "127.0.0.1:8000" + "/callback/", 
				"callback_url": "http://localhost:8000/callback",
				"razorpay_key": 'rzp_test_oycvuJtS3rWECD.',
				"order": order,
			},
		)
	return render(request, "payment.html")

@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=('rzp_test_oycvuJtS3rWECD', 'jLfQXbhTFXBvMLb5t6RmKuqj'))
        return client.utility.verify_payment_signature(response_data)

    print("Request POST data:", request.POST)

    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        print(payment_id)
        provider_order_id = request.POST.get("razorpay_order_id", "")
        print(provider_order_id)
        signature_id = request.POST.get("razorpay_signature", "")
        print(signature_id)
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        if verify_signature(request.POST):
            order.status = PaymentStatus.SUCCESS
        else:
            order.status = PaymentStatus.FAILURE
        order.save()
        return render(request, "callback.html", context={"status": order.status})
    else:
        payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        provider_order_id = json.loads(request.POST.get("error[metadata]")).get(
            "order_id"
        )
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.status = PaymentStatus.FAILURE
        order.save()
        return render(request, "callback.html", context={"status": order.status})