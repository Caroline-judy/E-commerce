from django.shortcuts import render,redirect
from ecommerceapp.models import Contact,Product,OrderUpdate,Orders
from django.contrib import messages
from django.core.exceptions import ValidationError
from math import ceil
from ecommerceapp import keys
from django.conf import settings
MERCHANT_KEY=keys.MK
import json
from django.views.decorators.csrf import  csrf_exempt
from PayTm import Checksum

# Create your views here.
def index(request):
    allProds = []
    catprods = Product.objects.values('category','id')
    print(catprods)
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds}

    return render(request,"index.html",params)

    
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        desc = request.POST.get("desc")
        pnumber = request.POST.get("pnumber")

        myquery = Contact(name=name, email=email, desc=desc, phonenumber=pnumber)

        # Attempt to save and handle potential validation errors
        try:
            myquery.full_clean()  # Validate the instance before saving
            myquery.save()
            messages.info(request, "We will get back to you soon...")
        except ValidationError as e:
            # This will capture the specific error messages
            if 'phonenumber' in e.message_dict:
                messages.error(request, "Invalid phone number. Please enter exactly 10 digits.")
            else:
                messages.error(request, "There was an error with your submission. Please check your input.")

        return render(request, "contact.html")

    return render(request, "contact.html")

   
    
def about(request):
    return render(request, "about.html")


def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')

    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2','')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        Order = Orders(items_json=items_json,name=name,amount=amount, email=email, address1=address1,address2=address2,city=city,state=state,zip_code=zip_code,phone=phone)
        print(amount)
        Order.save()
        update = OrderUpdate(order_id=Order.order_id,update_desc="the order has been placed")
        update.save()
        thank = True
# # PAYMENT INTEGRATION

        id = Order.order_id
        oid=str(id)+"Sakhi"
        param_dict = {

            'MID':keys.MID,
            'ORDER_ID': oid,
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'paytm.html', {'param_dict': param_dict})

    return render(request, 'checkout.html')

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
            a=response_dict['ORDERID']
            b=response_dict['TXNAMOUNT']
            rid=a.replace("Sakhi","")
           
            print(rid)
            filter2= Orders.objects.filter(order_id=rid)
            print(filter2)
            print(a,b)
            for post1 in filter2:

                post1.oid=a
                post1.amountpaid=b
                post1.paymentstatus="PAID"
                post1.save()
            print("run agede function")
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'paymentstatus.html', {'response': response_dict})



from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Orders, OrderUpdate

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    currentuser = request.user.username
    items = Orders.objects.filter(email=currentuser)
    rid = ""

    # Check if items are available
    if items.exists():
        for i in items:
            print(i.oid)
            myid = i.oid
            rid = myid.replace("Sakhi", "")
            print(rid)

        # Ensure rid is set before fetching status
        if rid:
            status = OrderUpdate.objects.filter(order_id=int(rid))
            for j in status:
                print(j.update_desc)
        else:
            status = []  # No status if rid is not set
    else:
        status = []  # No items found for the user

    context = {"items": items, "status": status}
    return render(request, "profile.html", context)







from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Subscriber
from django.core.mail import send_mail
from django.conf import settings

def send_welcome_email(email):
    subject = 'Welcome to Sakhi!'
    message = 'Thank you for subscribing to our newsletter! You will receive updates from us.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print(f"Error sending email: {e}")

@login_required
def subscribe(request):
    user_email = request.user.email  # Get the logged-in user's email
    is_subscribed = Subscriber.objects.filter(email=user_email).exists()

    if not is_subscribed:
        Subscriber.objects.create(email=user_email)  # Automatically subscribe the user
        send_welcome_email(user_email)  # Send welcome email
        return redirect('subscribe_success')  # Redirect to the success page

    return render(request, 'subscribe.html', {'is_subscribed': is_subscribed})

def subscribe_success(request):
    return render(request, 'subscribe_success.html')  # Render the success template



def blog(request):
    return render(request, 'blog.html')