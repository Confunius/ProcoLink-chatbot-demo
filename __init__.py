import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g, send_file, flash
import shelve
# import dbm.gnu
import sys
import os
from datetime import datetime, timedelta
import time
import stripe
from dataclasses import dataclass, field
# sys.path.remove(main_dir)
import requests
import sendgrid
from sendgrid.helpers.mail import Mail, From, To
#from flask_wtf.recaptcha import RecaptchaField
from markupsafe import Markup


# current_dir = os.path.dirname(os.path.abspath(__file__))
# main_dir = os.path.dirname(current_dir)
# sys.path.append(main_dir)
# Importing Objects
from Objects.transaction.Product import Product  # it does work
from Objects.transaction.onlineCourses import onlineCourse
from Objects.transaction.Order import Order
from Objects.transaction.Review import Review
from Objects.transaction.code import Code
from Objects.transaction.cart import Cart, CartItem
from Objects.transaction.wishlist import Wishlist, WishlistItem
from Objects.CustomerService.Record import Record
from Objects.account.Admin import Admin
from Objects.account.Customer import User
from Objects.account.Forms import DelimitedNumberInput, createUser, createCourse, userLogin, userEditInfo, userChangePassword, userPaymentMethod, createAdmin, adminLogin, editAdminAccount
#from Objects.blog.blog import Post, Comments, Likes

# sys.path.remove(main_dir)


WeiHeng_Domain = "https://congenial-disco-5g444v96pv537v7x-5000.app.github.dev/"
# WeiHeng_Domain = "http://127.0.0.1:5000/"
Public_key = ""
Private_key = ""

cartobj = Cart()
wishlistobj = Wishlist()

Domain = WeiHeng_Domain
Public_key = "6LdgM_8nAAAAAA5r2dkOXO5Fn3tnZaXPODjXLRMs"
Private_key = "6LdgM_8nAAAAADidEavxieoxm7ivfa8mdcP5bdRc"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SENDGRID_API_KEY'] = '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'
app.secret_key = 'your_secret_key_here'  # Replace with your own secret key
app.config['RECAPTCHA_PUBLIC_KEY'] = Public_key
app.config['RECAPTCHA_PRIVATE_KEY'] = Private_key
#app.config['RECAPTCHA_VERIFY_URL'] = 'https://www.google.com/recaptcha/api/siteverify'

# Replace with your own secret key
stripe.api_key = 'sk_test_51NbJAUL0EO5j7e8js0jOonkCjFkHksaoITSyuD8YR34JLHMBkX3Uy4SwejTVr6XAvL8amqm4kMjmXtedg2I1oNTI00wnaqFYJJ'

# Account

def generate_time_for_timeseries():
    return str(datetime.;;;now().replace(minute=0, second= 0, microsecond=0))

def send_verification_email(email):
    sg = sendgrid.SendGridAPIClient(api_key=app.config['SENDGRID_API_KEY'])
    verification_link = f"{Domain}verify_email?email={email}"
    message = Mail(
        from_email=From('siiewweiheng@gmail.com'),
        to_emails=To(email),
        subject='Email Verification',
        html_content=f'Thank you for registering an account for our Healthy Living Website.<br>If this was not done by you, please ignore this email.<br><br>Please click this to <a href="{verification_link}">verify</a> your account.<br><br>Best Regards,<br> FashionHub Accounts Department<br><img src="https://thumbs.dreamstime.com/z/sustainable-fashion-logo-eco-friendly-production-label-icon-badge-clothes-hanger-green-leaves-natural-recycling-215122758.jpg" width="120" height="120"></img>'
    )
    try:
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)


@app.route('/verify_email', methods=['GET'])
def verify_email():
    email = request.args.get('email')
    # Add code to verify the email address and update userVerified column accordingly in your database.
    # For simplicity, we'll just set userVerified to 1 here.
    db = shelve.open('Objects/account/user.db', 'w')
    users_dict = db.get('users', {})

    for user in users_dict.values():
        if user.get_userEmail() == email:
            userVerified = 1
            user.set_userVerified(userVerified)
            db['users'] = users_dict
            db.close()
            return render_template('/Customer/verifiedEmailThankYou.html')

    db.close()
    return "Email verification failed. User not found."


@app.route('/Logout', methods=['GET','POST'])
def Logout():
    session.clear()
    return render_template('/Customer/homepage.html')
# User side
@app.route('/Login', methods=['GET','POST'])
def Login():
    create_user_form = userLogin(request.form)
    if request.method == "POST" and create_user_form.validate():
        user_db_path = 'Objects/account/user.db'
        if not os.path.exists(user_db_path):
            print("we have no user.db")
            db = shelve.open(user_db_path, 'c')
            db['users'] = {}
            db['admins'] = {}
            db.close()
        db = shelve.open(user_db_path, 'w')
        users_dict = db.get('users', {})  # Use a default empty dict if 'users' doesn't exist yet

        email = create_user_form.userEmail.data
        password = create_user_form.userPassword.data

        print(users_dict)
        for key, user_data in users_dict.items():
            print(key, user_data.get_userPassword, user_data.get_userEmail())
            if user_data.get_userEmail() == email and user_data.get_userPassword() == password:
                if user_data.get_userVerified() == 1:
                    session['id'] = key
                    session['userfullname'] = user_data.get_userFullName()
                    session['username'] = user_data.get_userName()
                    session['useremail'] = user_data.get_userEmail()
                    session['useraddress'] = user_data.get_userAddress()
                    session['userpostalcode'] = user_data.get_userPostalCode()
                    session['user_role'] = user_data.get_userRole()
                    session['user_logged_in'] = True
                    db.close()

                    print("User successfully saved.")
                    if session["user_role"] == "teacher":
                        return redirect(url_for('TeacherHomepage'))
                    else:
                        return redirect(url_for('CustomerHomepage'))
                else:
                    #flash("Please verify/create your account.", category="danger")
                    return render_template('/Customer/account/LoginPage.html', form=create_user_form)

        admin_dict = db.get('admins', {})
        print(admin_dict)
        if admin_dict == {}:
            print("we have an empty admin_dict")
            admin = Admin("admin", "admin", "admin", "admin", "siiewweiheng@gmail.com", "admin", "12345678")
            print("admin is created", admin.get_adminEmail(), admin.get_adminPassword())
            users_dict[admin.get_admin_id()] = admin #users_dict[3] = user // user_dict = {1:user, 3:user}
            db['admins'] = users_dict #put everything back
            db.close()

        # Handle admin login here (similar to user login)
        admin_email = create_user_form.userEmail.data #It doesn't matter as it is borrowing the fields not the
                                                    #corresponding assigned "variable" in forms.py Programming essential
        admin_password = create_user_form.userPassword.data

        # Check if the admin credentials are valid (you can implement your admin login logic here)
        for key, admin_data in admin_dict.items():
            if admin_data.get_adminEmail() == admin_email and admin_data.get_adminPassword() == admin_password:
                if admin_data.get_adminVerified() == 'deactivated':
                    #flask.flash("Your account has been deactivated. Please contact an administrator to reactivate your account.", category="danger")
                    return render_template('/Customer/account/LoginPage.html', form=create_user_form)
                else:
                    session['id'] = key
                    session['adminfname'] = admin_data.get_adminFirstName()
                    session['adminlname'] = admin_data.get_adminLastName()
                    session['adminusername'] = admin_data.get_adminUserName()
                    session['adminemail'] = admin_data.get_adminEmail()
                    session['phonenumber'] = admin_data.get_adminPhoneNumber()
                    session['admin_logged_in'] = True
                    db.close()
                    return redirect(url_for('ahome'))


    return render_template('/Customer/account/LoginPage.html', form=create_user_form)


@app.route('/Teachers/CreateAccount')
def TeacherHomepage():
    return render_template('/Teachers/teacherLoggedInHome.html')

@app.route('/teacher/add_course', methods=['GET', 'POST'])
def add_course():
    create_course_form = createCourse(request.form)
    if request.method == "POST":
        db = shelve.open('Objects/transaction/course.db', 'c')
        # course_dict = {}
        # try:
        #     course_dict = db['course']
        # except:
        #     db["course"] = course_dict
        #     print("Error in retrieving course from course.db")

        course = onlineCourse(create_course_form.courseId.data, create_course_form.name.data, create_course_form.videos.data, 
                              create_course_form.price.data, create_course_form.image.data, 
                              create_course_form.studentPurchaseList.data, create_course_form.refundDescription.data, 
                              create_course_form.courseContent.data, create_course_form.requirements.data,
                                create_course_form.description.data, create_course_form.courseForWho.data, 
                                create_course_form.instructor.data)
        db[course.courseId] = course
        # print("dATA", create_course_form.courseId.data, create_course_form.name.data)
        # print("Course is created", course)
        # print("Course Name", course.name)
        course_list = []
        for key in db.keys():
            print("keys: ", key)
            print("values: ", db[key])
            course_list.append(db[key])
            print(course_list)

        db.close()
        for course in course_list:
            print("Course Name", course.name)
            print("Course ID", course.courseId)
            print("Course Price", course.price)
        return render_template('/Teachers/teacherLoggedInHome.html', course_list=course_list, form=create_course_form)

    return render_template('/Teachers/teacherLoggedInHome.html', course_list=course_list, form=create_course_form)

@app.route('/')
def CustomerHomepage():
    try:
        login = session['user_logged_in']
    except KeyError:
        session['user_logged_in'] = False

    return render_template('/Customer/homepage.html')

@app.route('/blog')
def Blog():
    return render_template('/Customer/blog.html')

@app.route('/UserRegistrationPage', methods=['GET', 'POST'])
def UserRegistrationPage():
    create_user_form = createUser(request.form)
    if request.method == "POST":
        db = shelve.open('Objects/account/user.db', 'c')
        users_dict = {}
        try:
            users_dict = db['users'] #user_dict = {1:UserObject, 2:UserObject} #take everything out
        except:
            db["users"] = users_dict
            print("Error in retrieving Users from user.db")

        userPassword = create_user_form.userPassword.data
        userCfmPassword = create_user_form.userCfmPassword.data
        if not userPassword == userCfmPassword:
            # flash("Password and Confirm Password does not match.", category="danger")
            return redirect("/UserRegistration")

        user = User(create_user_form.userFullName.data, create_user_form.userName.data, create_user_form.userPassword.data,
                             create_user_form.userEmail.data, create_user_form.userCfmPassword.data,
                             create_user_form.userAddress.data, create_user_form.userPostalCode.data, create_user_form.userRole.data)
        print("User is created", user)

        users_dict[user.get_user_id()] = user #users_dict[3] = user // user_dict = {1:user, 3:user}
        db['users'] = users_dict #put everything back
        db.close()
        send_verification_email(create_user_form.userEmail.data)
        #flash('A verification email has been sent. Please check your inbox.', category='success')
        session["email_success"] = "A verification email has been sent. Please check your inbox."
        #time.sleep(2)
        #return redirect("/Login")
        return "<script>alert('A verification email has been sent. Please check your inbox.');window.location.href='/Login';</script>"
    return render_template('/Customer/account/CustomerRegistration.html', form=create_user_form)

@app.route('/EditCustomerAccount/<int:id>/', methods=['GET', 'POST']) #refer to usersettings "href"
def EditCustomerAccount(id):
    edit_user_form = userEditInfo(request.form)
    if request.method == 'POST' and edit_user_form.validate():
        db = shelve.open('Objects/account/user.db', 'c')
        users_dict = {}
        try:
            users_dict = db['users']  # user_dict = {1:UserObject, 2:UserObject} #take everything out
        except:
            db["users"] = users_dict
            print("Error in retrieving Users from user.db")

        tempUser = users_dict[id]
        tempUser.set_userFullName(edit_user_form.userFullName.data)
        tempUser.set_userName(edit_user_form.userName.data)
        tempUser.set_userEmail(edit_user_form.userEmail.data)
        tempUser.set_userAddress(edit_user_form.userAddress.data)
        tempUser.set_userPostalCode(edit_user_form.userPostalCode.data)

        session['userfullname'] = tempUser.get_userFullName()
        session['username'] = tempUser.get_userName()
        session['useremail'] = tempUser.get_userEmail()
        session['useraddress'] = tempUser.get_userAddress()
        session['userpostalcode'] = tempUser.get_userPostalCode()

        users_dict[id] = tempUser
        db['users'] = users_dict
        db.close()
        return redirect(url_for('UserProfile'))
    else:
        db = shelve.open('Objects/account/user.db', 'r')
        users_dict = db['users']
        db.close()

        user = users_dict.get(id)
        edit_user_form.userFullName.data = user.get_userFullName()
        edit_user_form.userName.data = user.get_userName()
        edit_user_form.userEmail.data = user.get_userEmail()
        edit_user_form.userAddress.data = user.get_userAddress()
        edit_user_form.userPostalCode.data = user.get_userPostalCode()
        return render_template('Customer/account/editinfo.html', form=edit_user_form)

@app.route('/CustomerChangePassword/<int:id>/', methods=['GET', 'POST'])
def CustomerChangePassword(id):
    edit_user_form = userChangePassword(request.form)
    if request.method == 'POST' and edit_user_form.validate():
        db = shelve.open('Objects/account/user.db', 'c')
        users_dict = {}
        try:
            users_dict = db['users']  # user_dict = {1:UserObject, 2:UserObject} #take everything out
        except:
            db["users"] = users_dict
            print("Error in retrieving Users from Objects/account/user.db")

        tempUser = users_dict[id]
        tempUser.set_userPassword(edit_user_form.userPassword.data)
        tempUser.set_userCfmPassword(edit_user_form.userCfmPassword.data)

        users_dict[id] = tempUser
        db['users'] = users_dict
        db.close()

        return redirect(url_for('UserProfile'))
    else:
        db = shelve.open('Objects/account/user.db', 'r')
        users_dict = db['users']
        db.close()

        user = users_dict.get(id)
        edit_user_form.userPassword.data = user.get_userPassword()
        edit_user_form.userCfmPassword.data = user.get_userCfmPassword()
        return render_template('Customer/account/changepw.html', form=edit_user_form)

@app.route('/UserDeletion/<int:user_id>', methods=['POST'])
def user_deletion(user_id):
    db = shelve.open('Objects/account/user.db', 'w')
    users_dict = db.get('users', {})

    # Check if the user_id exists in the users_dict
    if user_id in users_dict:
        users_dict.pop(user_id)
        db['users'] = users_dict
        db.close()
        session.clear()
        return redirect(url_for('listCustomerAccounts'))
    else:
        db.close()
        return "User not found."

@app.route('/UserDeactivation/<int:user_id>', methods=['POST'])
def user_deactivation(user_id):
    db = shelve.open('Objects/account/user.db', 'w')
    users_dict = db.get('users', {})

    # Check if the user_id exists in the users_dict
    if user_id in users_dict:
        # Set the user status to 'deactivated' (or any other value to represent deactivation)
        user = users_dict[user_id]
        user.set_userVerified("deactivated")  # Update the status to "deactivated"
        db['users'] = users_dict
        db.close()
        session.clear()
        return render_template('/Customer/homepage.html')
    else:
        db.close()
        return "User not found."

@app.route('/AdminDeletion/<int:admin_id>', methods=['POST'])
def admin_deletion(admin_id):
    db = shelve.open('Objects/account/user.db', 'w')
    admins_dict = db.get('admins', {})

    # Check if the admin_id exists in the admins_dict
    if admin_id in admins_dict:
        admins_dict.pop(admin_id)
        db['admins'] = admins_dict
        db.close()
        session.clear()
        return redirect(url_for('listAdminAccounts'))
    else:
        db.close()
        return "Admin not found."

@app.route('/AdminDeactivation/<int:admin_id>', methods=['POST'])
def admin_deactivation(admin_id):
    db = shelve.open('Objects/account/user.db', 'w')
    admins_dict = db.get('admins', {})

    # Check if the admin_id exists in the admins_dict
    if admin_id in admins_dict:
        # Set the admin status to 'deactivated' (or any other value to represent deactivation)
        admin = admins_dict[admin_id]
        admin.set_adminVerified("deactivated")  # Update the status to "deactivated"
        db['admins'] = admins_dict
        db.close()
        session.clear()
        return redirect(url_for('listAdminAccounts'))
    else:
        db.close()
        return "Admin not found."

@app.route('/payment_methods/<int:id>', methods = ['GET', 'POST'])
def PaymentMethod(id):
    create_user_payment = userPaymentMethod(request.form)
    if request.method == "POST" and create_user_payment.validate():
        address = create_user_payment.userAddress.data
        email = create_user_payment.userEmail.data
        name = create_user_payment.userFullName.data

        expiry_date = create_user_payment.userCardExp.data
        number = create_user_payment.userCardNumber.data
        cvc = create_user_payment.userCardSec.data


        print("retrieved expry date", expiry_date)
        expiry_list = expiry_date.split('/')
        print("expiry_list", expiry_list)
        exp_month = expiry_list[0]
        print("expiry_month", exp_month)
        exp_year = expiry_list[1] 
        print('expriry year', exp_month)

        stripe.PaymentMethod.create(
            type="card",
            billing_details = {
                "address": address,
                "email": email,
                "name": name
            },
            card = {
                "exp_month": exp_month,
                "exp_year": exp_year,
                "number": number,
                "cvc": cvc
            },
        )
        db = shelve.open('Objects/account/user.db', 'r')
        users_dict = db['users']
        db.close()

        user = users_dict.get(id)
        create_user_payment.userFullName.data = user.get_userFullName()
        create_user_payment.userName.data = user.get_userName()
        create_user_payment.userEmail.data = user.get_userEmail()
        create_user_payment.userAddress.data = user.get_userAddress()
        create_user_payment.userPostalCode.data = user.get_userPostalCode()

    return render_template('/Customer/account/payment.html', form=create_user_payment)

@app.route('/UserHomepage')
def UserHomepage():
    if not os.path.exists(user_db_path):
        print("we have no user.db")
        db = shelve.open(user_db_path, 'c')
        db['users'] = {}
        db['admins'] = {}
        db.close()

    return render_template('/Customer/homepage.html')
# Account
@app.route('/UserProfile')
def UserProfile():
    edit_user_form = userEditInfo(request.form)
    if request.method == 'POST' and edit_user_form.validate():
        db = shelve.open('Objects/account/user.db', 'c')
        users_dict = {}
        try:
            users_dict = db['users']  # user_dict = {1:UserObject, 2:UserObject} #take everything out
        except:
            db["users"] = users_dict
            print("Error in retrieving Users from user.db")

        tempUser = users_dict[session['id']]
        tempUser.set_userFullName(edit_user_form.userFullName.data)
        tempUser.set_userName(edit_user_form.userName.data)
        tempUser.set_userEmail(edit_user_form.userEmail.data)
        tempUser.set_userAddress(edit_user_form.userAddress.data)
        tempUser.set_userPostalCode(edit_user_form.userPostalCode.data)

        session['userfullname'] = tempUser.get_userFullName()
        session['username'] = tempUser.get_userName()
        session['useremail'] = tempUser.get_userEmail()
        session['useraddress'] = tempUser.get_userAddress()
        session['userpostalcode'] = tempUser.get_userPostalCode()

        users_dict[id] = tempUser
        db['users'] = users_dict
        db.close()
        return redirect(url_for('UserProfile'))
    else:
        db = shelve.open('Objects/account/user.db', 'r')
        users_dict = db['users']
        db.close()

        user = users_dict.get(session['id'])
        edit_user_form.userFullName.data = user.get_userFullName()
        edit_user_form.userName.data = user.get_userName()
        edit_user_form.userEmail.data = user.get_userEmail()
        edit_user_form.userAddress.data = user.get_userAddress()
        edit_user_form.userPostalCode.data = user.get_userPostalCode()
    return render_template('/Customer/account/usersettings.html', form=edit_user_form)

@app.route('/OrderStatus')
def OrderStatus():
    return render_template('/Customer/account/orderstatus.html')

@app.route('/OrderHistory')
def OrderHistory():
    combined_list = []
    products_for_order = []

    with shelve.open('Objects/transaction/order.db') as order_db:
        with shelve.open('Objects/transaction/product.db') as product_db:
            for key in order_db:
                orderobj = order_db.get(key)
                if orderobj.user_id == session['id']:
                    products_for_order = [product_db.get(pid) for pid in orderobj.product_id]
                    combined_list.append({
                        "order": orderobj,
                        "products": products_for_order
                    })
    for product in products_for_order:
        print(product.__dict__)
    return render_template('/Customer/account/orderhistory.html', combined_list=combined_list)

@app.route('/addtowishlist/<product_id>')
def AddToWishList(product_id):
    with shelve.open('Objects/transaction/product.db') as productdb:
        product = productdb[product_id]
        for item in wishlistobj.wishlist_items:
            print("item's product id matching with product id", item.product_id, product_id)
            if item.product_id == product_id:
                return redirect(url_for('product_info', product_id=product.product_id, error="product_alr_in_wishlist"))

        wishlistobj.add_to_wishlist(WishlistItem(session['id'], product_id, product.name, product.list_price, product.image))
    return redirect(url_for('wishList'))



@app.route('/Wishlist')
def wishList():
    return render_template('/Customer/account/wishlist.html', wishlist=wishlistobj.wishlist_items)

@app.route('/CustomerAccountDelete')
def CustomerAccountDelete():
    return render_template('/Customer/account/accountdelete.html')

@app.route('/sustainability')
def sustainability():
    return render_template('/Customer/sustainability.html')

# Transaction

@app.route('/product')
def products():
    product_list = []
    db_path = 'Objects/transaction/product.db'
    review_db_path = 'Objects/transaction/review.db'
    try:
        db = shelve.open(db_path, 'r')
        review_db = shelve.open(review_db_path, 'r')

        # Get the filter options from request parameters
        category_filter = request.args.get('category')
        rating_filter = request.args.get('rating')

        for key in db:
            product = db[key] #retrieve a COPY of data at key (raise KeyError if no such key) 
            product_reviews = [review for review in review_db.values(
            ) if review.product_id == product.product_id]
            num_reviews = len(product_reviews)
            if num_reviews > 0:
                total_rating = sum(review.rating for review in product_reviews)
                average_rating = total_rating / num_reviews
            else:
                average_rating = 0

            # Round the average_rating to display in stars
            rounded_rating = round(average_rating)

            # Add the average_rating and num_reviews to the product object
            product.average_rating = rounded_rating
            product.num_reviews = num_reviews

            # Apply filters if they are selected
            if category_filter and category_filter not in product.category:
                continue

            if rating_filter and int(rating_filter) > rounded_rating:
                continue

            product_list.append(product)

        db.close()
        review_db.close()
    except:
        product_list = []

    # Create a list of unique categories from the product_list
    categories = list(set(product.category for product in product_list))

    # Sort the lists by alphabetical order
    sorted_product_list = sorted(product_list, key=lambda product: product.name)
    sorted_categories = sorted(categories)

    return render_template('/Customer/transaction/Product.html', product_list=sorted_product_list, count=len(product_list), categories=sorted_categories)



@app.route('/product/<product_id>')
def product_info(product_id):
    error = request.args.get('error')
    error_message=None
    if error == "stock_limit_exceeded":
        error_message = "You've exceeded the available stock for this product."
    elif error == "product_alr_in_wishlist":
        error_message = "Product already in wishlist."

    review_list = []
    pdb_path = 'Objects/transaction/product.db'
    db_path = 'Objects/transaction/review.db'

    try:
        pdb = shelve.open(pdb_path, 'r')
        if product_id in pdb.keys():
            productobj = pdb[product_id]
        pdb.close()
    except:
        productobj = None

    try:
        db = shelve.open(db_path, 'r')
        for key in db:
            review = db[key]
            if review.product_id == product_id:
                review_list.append(review)

        db.close()
    except:
        review_list = []

    # Calculate average rating
    total_rating = sum(review.rating for review in review_list)
    total_reviews = len(review_list)
    average_rating = total_rating / total_reviews if total_reviews > 0 else 0

    # Round the average rating up to the nearest whole number
    rounded_rating = round(average_rating)

    # Create a list of unique colors from the productobj object.
    color_options = ', '.join(productobj.color_options)

    # Create a list of unique sizes from the productobj object.
    size_options = ', '.join(productobj.size_options)

    return render_template('/Customer/transaction/ProductInfo.html', productobj=productobj,
                            review_list=review_list, count=len(review_list), rounded_rating=rounded_rating,
                              size_options=size_options, color_options=color_options, error_message=error_message)

# for courses
@app.route('/course', methods=['POST', 'GET'])
def courses():
    coursesList = []
    db_path = 'Objects/transaction/course.db'
    review_db_path = 'Objects/transaction/review.db'

    try:
        db = shelve.open(db_path, 'r')
        review_db = shelve.open(review_db_path, 'r')

        # Get the filter options from request parameters
        category_filter = request.args.get('category')
        rating_filter = request.args.get('rating')

        for key in db:
            course = db[key]
            course_reviews = [review for review in review_db.values(
            ) if review.product_id == course.courseId]
            num_reviews = len(course_reviews)

            if num_reviews > 0:
                total_rating = sum(review.rating for review in course_reviews)
                average_rating = total_rating / num_reviews
            else:
                average_rating = 0

            # Round the average_rating to display in stars
            rounded_rating = round(average_rating)

            # Add the average_rating and num_reviews to the product object
            course.average_rating = rounded_rating
            course.num_reviews = num_reviews

            # Apply filters if they are selected
            if category_filter and category_filter not in course.category:
                continue

            if rating_filter and int(rating_filter) > rounded_rating:
                continue

            coursesList.append(course)

        db.close()
        review_db.close()
    except:
        coursesList = []
    #return redirect(url_for('onlineCourse', courseId=courseId))
    return render_template('/Customer/transaction/Course.html', course_list=coursesList, count=len(coursesList))


@app.route('/course/<course_id>')
def course_info(course_id):
    # error = request.args.get('error')
    # error_message=None
    # if error == "stock_limit_exceeded":
    #     error_message = "You've exceeded the available stock for this product."
    # elif error == "product_alr_in_wishlist":
    #     error_message = "Product already in wishlist."

    review_list = []
    cdb_path = 'Objects/transaction/course.db'
    # db_path = 'Objects/transaction/review.db'

    try:
        cdb = shelve.open(cdb_path, 'r')
        if course_id in cdb.keys():
            courseobj = cdb[course_id]
        cdb.close()
    except:
        courseobj = None

    # try:
    #     db = shelve.open(db_path, 'r')
    #     for key in db:
    #         review = db[key]
    #         if review.product_id == course_id:
    #             review_list.append(review)

    #     db.close()
    # except:
    #     review_list = []

    # Calculate average rating
    total_rating = sum(review.rating for review in review_list)
    total_reviews = len(review_list)
    average_rating = total_rating / total_reviews if total_reviews > 0 else 0

    # Round the average rating up to the nearest whole number
    rounded_rating = round(average_rating)


    return render_template('/Customer/transaction/CourseInfo.html', courseobj=courseobj,
                            )

#create course
@app.route('/admin/courses')
def course_admin():
    course_list = []
    course_dict = {}
    db_path = 'Objects/transaction/course.db'
    if not os.path.exists(db_path):
        placeholder_data = [
            {
                "courseId": "C1",
                "videos": "https://www.youtube.com/watch?v=XFjzTttyrv8",
                "image": "http://www.healthtransformation.net/wp-content/uploads/2015/12/Human-Body-and-Mind-3D-Illustration.jpg",
                "price": 15,
                "studentPurchaseList": [],
                "refundDescription": "30 days maximum",
                'name': 'Duality of Body and Mind',
                "courseContent": { 

                    'Basic Nutrition Module 1 - Getting started': {
                        'video':'https://youtu.be/eVBWHnHEX6I?si=PWb9nw5dN0fztcZV',
                        'article':'https://www.nutrition.gov/about-us#:~:text=Nutrition.gov%20is%20a%20USDA,and%20food%20safety%20for%20consumers',
                        'image': 'https://247wallst.com/wp-content/uploads/2020/04/imageForEntry9-bbt.jpg',
                        'quiz': {
                            1: {
                                'Question 1': 'Name an example of an fruit','options': ['a) Apple','b) Fish', 'c) Ginger', 'd) Carrot'],'correct_answer': 'a'
                            },

                            2: {
                                'Question 2': 'Which of the following food we have to eat sparingly?', 'options': ['a) French Fries','b) BBQ Chicken', 'c) A plate of chicken bolognese', 'd) Koko Crunch'],
                                'correct_answer': 'a'
                                },

                            3: {
                                'Question 3': 'What cannot be considered as a measuring tool in your serving size?', 'options': ['a) Hands','b) Measuring Cup', 'c) Measuring Cylinder', 'd) Measuring Spoon'],
                                'correct_answer': 'c'
                            }
                        }
                    },
                    'What is Mental Health? Module 2': {
                        'video':'https://www.youtube.com/embed/G0zJGDokyWQ?si=rKBjzmha55fR9Ov9',
                        'article':'https://www.cdc.gov/mentalhealth/learn/index.htm',
                        'image': 'http://www.pickthebrain.com/blog/wp-content/uploads/2014/01/mental-fitness.jpg',
                        'quiz': {
                            1: {
                                'Question 1': 'Name one example of mental disorder', 'options': ['a) Fatigue','b) Excitement', 'c) Anxiety', 'd) Sadness'],
                                'correct_answer': 'c'
                            },

                            2: {
                                'Question 2': 'Which one is not an example of States of Positive Mental Health?', 'options': ['a) Thriving','b) Content', 'c) Fufilled', 'd) Depression'],
                                'correct_answer': 'd'
                            },

                            3: {
                                'Question 3': 'What happens if you do not treat mental disorders?', 'options': ['a) You will be happier','b) You will definitely age gracefully', 'c) You will have increased disability', 'd) None of the above'],
                                'correct_answer': 'c'
                            }

                            }
                    }, 
                    'Motivation and What Really Drives Human Behavior? Module 3': {
                        'video':'https://www.youtube.com/watch?v=IhEcX3226pM',
                        'article':'https://positivepsychology.com/motivation-human-behavior/',
                        'image':'https://1.bp.blogspot.com/-w7NNijz2U_o/VZhnyAGnYKI/AAAAAAAAAHU/CMXUZbX4itk/s1600/school-of-psychology-2.jpg',
                        'quiz': {
                            1: {
                                'Question 1': 'What is the 3 ideal solutions to solve complex things coming from your background?', 'options': ['a) Change your behavior, Comparing your personal truth with others positively, Behave your way to success','b) Stop rewarding bad behavior, Comparing your personal truth with others positively, Behave your way to success', 'c) Change your behavior, Stop rewarding bad behavior, Comparing your personal truth with others positively', 'd) Change your behavior, Stop rewarding bad behavior, Behave your way to success'],
                                'correct_answer': 'd'
                            },

                            2: {
                                'Question 2': 'What is a possible way to improve your results in life?', 'options': ['a) Fix your personal truth','b) Researching more on a topic', 'c) Change your social circle', 'd) Fix your personal weakness'],
                                'correct_answer': 'a'
                            },

                            3: {
                                'Question 3': 'What is Drive Motivation?', 'options': ['a) When you want to do something.','b) When talking about motivation, the topic of goals inevitably comes up.', 'c) When the sympathetic nervous system produces epinephrine and norepinephrine, it creates energy for action.', 'd) None of the above'],
                                'correct_answer': 'c'
                            }

                            }
                    },
                    'How To Set SMART Goals for Better Health and Wellness? Module 4': {
                        'video':'https://www.youtube.com/watch?v=IzuGj8hKGTc',
                        'article':'https://www.noomii.com/articles/13906-smart-goal-method',
                        'image':'http://www.boardandlife.com/wp-content/uploads/2019/10/why-is-goal-setting-important-organizations.jpg',
                        'quiz': {
                            1: {
                                'Question 1': 'Which one is the acronym for SMART Goals?', 'options': ['a) Measurable','b) Monetary', 'c) Meaningful', 'd) Mortified'],
                                'correct_answer': 'a'
                            },

                            2: {
                                'Question 2': 'What is an example Achievable Goal?', 'options': ['a) Should I eat 3 vegetables a day?','b) I will eat 2 vegetables a day, 2 times a week.', 'c) I will eat 200 vegetables a day, 2 times a week.', 'd) I will go to the gym 30 times a day.'],
                                'correct_answer': 'b'
                            },

                            3: {
                                'Question 3': 'How to create a SMART Goal Map?', 'options': ['a) Identify your long-term vision','b) Develop work-life balance', 'c) Creating a scehdule', 'd) None of the above'],
                                'correct_answer': 'a'
                            }

                            }
                    }
                 },
                 "requirements": "Compulsory to attend at least one module",
                 "description": "Here in this course, we will cover 2 different areas related to both the human body and the human mind! With 4 modules, this comprehensive course leaves no stone unturned! This course includes quizzes, videos and articles. introduction: 20 mins, module 1 : 30 mins, module 2 : 15 mins, module 3 : 25 mins, module 4 : 30 mins, total time taken: 2 hours",
                 "courseForWho": "For anyone aged above 12 years old",
                 "instructor": "Chen Wei Jie"     
            }
        ]

        db = shelve.open(db_path, 'c')
        for data in placeholder_data:
            course = onlineCourse(
                data["courseId"],
                data["name"],
                data["videos"],
                data["price"],
                data["image"],
                data["studentPurchaseList"],
                data["refundDescription"],
                data["courseContent"],
                data["requirements"],
                data["description"],
                data["courseForWho"],
                data["instructor"],
                )
            db[course.courseId] = course
        db.close()

    course_list = []
    db = shelve.open(db_path, 'r')
    # open the db and retrieve the dictionary
    for course_id, course_obj in db.items():
        course_list.append(course_obj)
    db.close()
    # prints out all the products and their info
    for course in course_list:
        print(course.courseId, course.videos, course.price, course.name, course.studentPurchaseList, course.refundDescription, course.courseContent, course.requirements, course.description, course.courseForWho, course.instructor)
        print("Course ID: ", course.courseId, "\n", "Product video: ", course.videos, "\n", "\n", "Course Price: ", course.price, "\n", "Course Name", course.name, "\n", "Student Purchase List: ", course.studentPurchaseList, "\n", "Refund Description: ", course.refundDescription, "\n", "Course Content: ", course.courseContent, "\n", "Requirements: ", course.requirements, "\n", "Description:", course.description, "\n", "Course For Who:", course.courseForWho, "\n", "Instructor: ", course.instructor)
    course_form = createCourse(request.form)
    return render_template('/Teachers/teacherLoggedInHome.html', course_list=course_list, count=len(course_list), form=course_form)


#688 - 822

@app.route('/review/<product_id>', methods=['POST'])
def add_review(product_id):
    db_path = 'Objects/transaction/review.db'

    # Retrieve the form data
    customer_name = request.form['customer_name']
    rating = int(request.form['rating'])
    review_comment = request.form['review_comment']
    try:
        db = shelve.open(db_path, 'w')  # Open the review.db in read-write mode
    except:
        db = shelve.open(db_path, 'c')

    # Generate a new review_id by finding the highest review_id and incrementing it by 1
    max_review_id = 0
    if db:
        # Check if the db is not empty before calculating the max_review_id
        max_review_id = max((int(review_id[1:]) for review_id in db.keys(
        ) if review_id.startswith('R')), default=0)

    new_review_id = "R" + str(max_review_id + 1)
    # user_id = session['id']
    user_id = 0

    # Create a new Review object
    review = Review(new_review_id, product_id, user_id,
                    customer_name, rating, review_comment)

    # Save the review to the review_db
    db[new_review_id] = review
    db.close()

    return redirect(url_for('product_info', product_id=product_id))



@app.context_processor
def cart_items_processor():
    num_items_in_cart = sum(item.quantity for item in cartobj.get_cart_items())
    return {'num_items_in_cart': num_items_in_cart}


@app.context_processor
def wishlist_items_processor():
    num_items_in_wishlist = len(wishlistobj.wishlist_items)
    return {'num_items_in_wishlist': num_items_in_wishlist}


@app.route('/product', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']

    # Fetch the product details from the database
    db_path = 'Objects/transaction/product.db'
    db = shelve.open(db_path, 'r')
    product = db.get(product_id)
    default_quantity = 1
    default_color = None
    default_size = None
    if product.color_options != [] or product.size_options != []:
        default_color = product.color_options[0]
        default_size = product.size_options[0]
    db.close()

    quantity = int(request.form.get('quantity', default_quantity))
    size = default_size
    color = default_color
    if product.color_options != [] or product.size_options != []:     
        size = request.form.get('size', default_size)
        color = request.form.get('color', default_color)

    # Fetch the current quantity of the product in the cart
    current_quantity_in_cart = 0
    for item in cartobj.get_cart_items():
        if item.product_id == product_id:
            current_quantity_in_cart = item.quantity
            break

    # Check the total desired quantity against the stock
    if current_quantity_in_cart + quantity > product.stock:
        # Handle the scenario where desired quantity exceeds available stock
        quantity = product.stock - current_quantity_in_cart
        return redirect(url_for('product_info', product_id=product.product_id, error="stock_limit_exceeded"))
# Create an item object with the product details and the selected quantity
    item = CartItem(product_id=product.product_id, name=product.name,
                    price=product.list_price, quantity=quantity, size=size, color=color, stock=product.stock)

    # Add the item to the cart
    cartobj.add_to_cart(item)

    return redirect(url_for('cart'))


@app.route('/update_cart_item/<cart_item_id>', methods=['POST'])
def update_cart_item(cart_item_id):
    action = request.form.get('action')
    new_size = request.form.get('size')  # Get the selected size from the form
    new_color = request.form.get('color')

    cart_items = cartobj.get_cart_items()

    # Find the cart item with matching product_id
    for cart_item in cart_items:
        if cart_item.product_id == cart_item_id:
            if action == 'increment':
                cart_item.quantity += 1
            elif action == 'decrement' and cart_item.quantity > 1:
                cart_item.quantity -= 1
            cart_item.size = new_size  # Update the size for the cart item
            cart_item.color = new_color

    return redirect(url_for('cart'))


@app.route('/delete_cart_item/<cart_item_id>', methods=['POST'])
def delete_cart_item(cart_item_id):
    cart_items = cartobj.get_cart_items()

    # Find the cart item with matching product_id
    for cart_item in cart_items:
        if cart_item.product_id == cart_item_id:
            cart_items.remove(cart_item)

    return redirect(url_for('cart'))


@app.route('/updateshippingforexpcheckout', methods=['POST'])
def updateshippingforexpcheckout():
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400
    try:
        data = request.get_json()
        if data is None:
            # Handle error here, e.g. return a response with a 400 status code
            return "Bad Request", 400
        shipping = data.get('shipping')
        if shipping is None:
            # Handle error here, e.g. return a response with a 400 status code
            return "Bad Request", 400
        session["shipping"] = shipping
        payment_intent_id = session["payment_intent_id"]
        new_total_cost = int(
            float(calculate_total_cost(cartobj.cart_items, shipping)) * 100)
        shipping_cost = 5 if shipping == "Standard Delivery" else 10
        print(shipping_cost)
        intent = stripe.PaymentIntent.modify(
            payment_intent_id,
            amount=new_total_cost
        )
        return jsonify({
            'clientSecret': intent['client_secret'],
            'amount': new_total_cost,
            'shipping_cost': shipping_cost
        })
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 400


@app.route('/cart')
def cart():
    cart_items = cartobj.get_cart_items()
    db_path = 'Objects/transaction/product.db'
    db = shelve.open(db_path, 'r')
    num_items_in_cart = sum(item.quantity for item in cart_items)

    # Combine rows with the same item name, price, quantity, and size
    combined_items = {}
    for item in cart_items:
        product = db.get(item.product_id)
        size_options = product.size_options
        color_options = product.color_options
        key = (item.name, item.price, item.size, item.color,
               tuple(size_options), tuple(color_options))
        existing_item = combined_items.get(key)
        if existing_item:
            existing_item.quantity += item.quantity
        else:
            item.size_options = size_options
            item.color_options = color_options
            combined_items[key] = item

    # update the cart_obj with the combined items
    cartobj.cart_items = list(combined_items.values())

    # Convert the dictionary of combined items back to a list
    combined_cart_items = list(combined_items.values())

    cart_total = cartobj.get_cart_total()

    session_cart_items = []
    for item in cart_items:
        session_cart_items.append(item.to_dict())

    session['intent_metadata'] = session_cart_items
    session['code_dict'] = {}
    session['shipping'] = 5

    return render_template('Customer/transaction/Cart.html', cart_items=combined_cart_items, cart_total=cart_total, num_items_in_cart=num_items_in_cart)


@app.route('/payment', methods=['GET'])
def display_payment():
    cart_items = cartobj.get_cart_items()
    line_items = []
    db_file = 'Objects/transaction/promo.db'
    allow_promo = os.path.isfile(db_file)
    for item in cart_items:
        print(item.name, find_product(item.name)[0])
        if item.color != None and item.size != None:
            line_item = {
                'price': find_product(item.name, item.color, item.size)["default_price"],
                'quantity': item.quantity,
                'adjustable_quantity': {"enabled": True, "minimum": 1, "maximum": 99},
            }
        else:
            line_item = {
                'price': find_product(item.name)[0]["default_price"],
                'quantity': item.quantity,
                'adjustable_quantity': {"enabled": True, "minimum": 1, "maximum": 99},
            }

        line_items.append(line_item)
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=Domain + 'thankyou',
            cancel_url=Domain + 'product',
            automatic_tax={'enabled': True},
            allow_promotion_codes=allow_promo,
            shipping_address_collection={
                'allowed_countries': ['SG'],
            },
            shipping_options=[{
                'shipping_rate_data': {
                    'display_name': 'Standard Delivery',
                    'type': 'fixed_amount',
                    'fixed_amount': {
                        'amount': 500,
                        'currency': 'sgd',
                    },
                    'delivery_estimate': {
                        'minimum': {
                            'unit': 'day',
                            'value': 1
                        },
                        'maximum': {
                            'unit': 'day',
                            'value': 3
                        },
                    },
                },
            },
                {
                'shipping_rate_data': {
                    'display_name': 'Express Delivery',
                    'type': 'fixed_amount',
                    'fixed_amount': {
                        'amount': 1000,
                        'currency': 'sgd',
                    },
                    'delivery_estimate': {
                        'minimum': {
                            'unit': 'hour',
                            'value': 6
                        },
                        'maximum': {
                            'unit': 'day',
                            'value': 1
                        },
                    },
                },
            }],
        )
        session['checkout_session_id'] = checkout_session.id
        code_dict = {}
        for code in stripe.PromotionCode.list()["data"]:
            code_data = {}
            code_data["code_id"] = code["id"]
            code_data["times_redeemed"] = code["times_redeemed"]
            code_dict[code["id"]] = code_data
        session["code_dict"] = code_dict
        if code_data["times_redeemed"] < 2:
            print(
                f"promo code 20OFF has {code_data['times_redeemed']} times redeemed")

    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.route('/totalcostcalculator')
def calculate_total_cost(cart_items, delivery_option):
    subtotal = 0
    for item in cart_items:
        subtotal += item.price * item.quantity
    shipping_costs = 5 if delivery_option == 'Standard Delivery' else 10

    total_cost = subtotal + shipping_costs
    return total_cost


@app.route('/create_intent', methods=['POST'])
def create_intent():
    cart = session['intent_metadata']
    cart_json = json.dumps(cart)

    session.pop('intent_metadata', None)
    amount = int(float(calculate_total_cost(
        cartobj.cart_items, 'Standard Delivery')) * 100)
    intent = stripe.PaymentIntent.create(
        amount=amount,  # Stripe expects the amount in cents
        currency='sgd',
        automatic_payment_methods={
            'enabled': True,
        },
        # shipping = {
        #     "address": "Nanyang Polytechnic",
        #     "name": "Mr Alvin",
        #     "phone": "12345678"
        # },
        metadata={
            'cart': cart_json,
        }
    )

    session['payment_intent_id'] = intent['id']
    return jsonify({
        'clientSecret': intent['client_secret'],
        'amount': amount
    })


@app.route('/thankyou')
def thankyou():

    # Retrieve cart items and promo code discount (if applicable) from the cart object
    product_db_path = 'Objects/transaction/product.db'
    order_db_path = 'Objects/transaction/order.db'
    checkout_info = stripe.checkout.Session.retrieve(
        session['checkout_session_id'])
    # checkout_line_items = stripe.checkout.Session.list_line_items(checkout_info['id'])
    subtotal = float(checkout_info['amount_subtotal']/100)
    total_cost = float(checkout_info['amount_total']/100)
    order_id = checkout_info['payment_intent']
    # payment_intent = stripe.PaymentIntent.retrieve(order_id)
    shipping_costs = float(checkout_info['shipping_cost']['amount_total']/100)
    shipping_rate_id = checkout_info['shipping_cost']['shipping_rate']
    delivery_option = stripe.ShippingRate.retrieve(shipping_rate_id)[
        'display_name']
    shipping_details_dict = checkout_info['shipping_details']
    shipping_address = f"{shipping_details_dict['address']['line1']}, {shipping_details_dict['address']['line2']}, {shipping_details_dict['address']['country']}"

    # Create new code_dict after purchase
    code_dict = {}
    for code in stripe.PromotionCode.list()["data"]:
        code_data = {}
        code_data["code_id"] = code["id"]
        code_data["code"] = code["code"]
        code_data["times_redeemed"] = code["times_redeemed"]
        code_data["percent_off"] = code["coupon"]["percent_off"]
        code_dict[code["id"]] = code_data

    # retrieve times_redeemed before purchase
    old_code_dict = session["code_dict"]
    promo_code_discount_pct = 0
    promo_code = ""

    for old_code_id, old_code_data in old_code_dict.items():
        old_times_redeemed = old_code_data["times_redeemed"]
        # check times_redeemed after purchase to see if there are any increases
        for code_id, code_data in code_dict.items():
            if code_id == old_code_id:
                new_times_redeemed = code_data["times_redeemed"]
                if new_times_redeemed > old_times_redeemed:
                    promo_code_discount_pct = code_data["percent_off"]/100
                    promo_code = code_data["code"]
                    print(
                        f"promo_code chosen: {code_data['code']}'s new_times_redeemed {new_times_redeemed} > old_times_redeemed {old_times_redeemed} ")
                else:
                    promo_code_discount_pct = 0
    print(
        f"code_discount: {promo_code_discount_pct}, promo_code: {promo_code}")
    if promo_code_discount_pct == 0:
        promo_code_discount = 0
        promo_code = 'N/A'
        print("No promo code applied")
    else:
        promo_code_discount = promo_code_discount_pct * subtotal

    # Close sessions
    session.pop('checkout_session_id', None)
    session.pop('code_dict', None)
    cart_items = cartobj.cart_items
    cartobj.cart_items = []

    # Create product_dict and a list of product_ids
    product_dict = {}
    with shelve.open(product_db_path) as product_db:
        for key in product_db:
            product = product_db[key]
            product_dict[key] = product
            # decrement stock from product_db
            for item in cart_items:
                if item.product_id == product.product_id:
                    product.stock -= item.quantity
                    product_db[product.product_id] = product
    product_id_list = []
    size = []
    color = []
    quantity = []
    for item in cart_items:
        product_id_list.append(item.product_id)
        size.append(item.size)
        color.append(item.color)
        quantity.append(item.quantity)
    # Create new order object
    # user_id = session['id']
    user_id = 1
    order_date = datetime.now().date()
    order_status = "processing"
    order = Order(order_id, user_id, product_id_list, size, color,
                  quantity, order_date, delivery_option, promo_code, order_status)
    with shelve.open(order_db_path) as db:
        db[order_id] = order

    return render_template('Customer/transaction/Thankyou.html', cart_items=cart_items, subtotal=subtotal,
                           promo_code_discount=promo_code_discount, shipping_costs=shipping_costs,
                           total_cost=total_cost, delivery_option=delivery_option,
                           shipping_address=shipping_address, product_dict=product_dict,
                           order_id=order_id)


@app.route('/cancel_and_refund/<order_id>', methods=['GET'])
def cancel_and_refund(order_id):
    # Fetch the order_id from the session or some other mechanism
    db_path = 'Objects/transaction/order.db'

    if order_id:
        # Open the shelve database
        db = shelve.open(db_path, 'w')
        # Delete the order from the database
        orderobj = db[order_id]
        orderobj.order_status = "cancelled"
        try:
            stripe.Refund.create(
                payment_intent=order_id,
            )
            orderobj.order_status = "refunded"
        except:
            print("Refund failed")

        db[order_id] = orderobj
        # Close the shelve database
        db.close()

    return render_template('Customer/transaction/CancelRefund.html')


# Customer Service

# Get the current date and format it
today = datetime.today()
formatted_date = today.strftime("%d/%m/%Y")

with shelve.open("Objects/CustomerService/custservice_deleted_records.db") as custservice_deleted_records_db:
    deleted_record_ids = custservice_deleted_records_db.get('deleted_record_ids', set())

with shelve.open("Objects/CustomerService/custservice_deleted_records_admin.db") as custservice_deleted_records_admin_db:
    deleted_record_admin_ids = custservice_deleted_records_admin_db.get('deleted_record_ids', set())

def check_and_delete_records():
    with shelve.open("Objects/CustomerService/service_records.db", writeback=True) as service_records_db:
        formatted_date = datetime.today()
        for record_id, record in service_records_db.items():
            last_save_date = datetime.strptime(record.last_save, "%d/%m/%Y")  # Correct the format here
            difference = formatted_date - last_save_date
            if difference > timedelta(days=30):
                print(f"Deleting record: {record_id}")
                deleted_record_ids.add(record_id)
                with shelve.open("Objects/CustomerService/custservice_deleted_records.db") as custservice_deleted_records_db:
                    custservice_deleted_records_db['deleted_record_ids'] = deleted_record_ids
                del service_records_db[record_id]

check_and_delete_records()

def get_total_record_count():
    with shelve.open("Objects/CustomerService/service_records.db") as service_records_db:
        # Get the count of current records
        current_count = len(service_records_db)

    with shelve.open("Objects/CustomerService/custservice_deleted_records.db") as custservice_deleted_records_db:
        # Get the count of deleted records
        deleted_count = len(custservice_deleted_records_db.get(
            'deleted_record_ids', set()))

    # Calculate the total count by adding current and deleted records
    total_count = current_count + deleted_count
    return total_count


@app.route('/FAQ')
def FAQ():
    with shelve.open("Objects/CustomerService/faqs.db") as db:
        faqs = db.get("faqs", [])
    return render_template('/Customer/custservice/FAQ.html', faqs=faqs)


@app.route('/get_csv')
def get_csv():
    csv_file_path = 'Objects/CustomerService/profanity_en.csv'
    return send_file(csv_file_path, as_attachment=True)


@app.route('/CustomerService')
def CustomerService():
    return render_template('/Customer/custservice/CustomerService.html')


@app.route('/ServiceRecord')
def ServiceRecord():
    with shelve.open("Objects/CustomerService/service_records.db", writeback=True) as service_records_db:
        return render_template('/Customer/custservice/ServiceRecord.html', service_records=service_records_db, user_id = session["id"])


@app.route('/record_detail/<record_id>')
def record_detail(record_id):
    # Find the record with the given record_id
    with shelve.open("Objects/CustomerService/service_records.db", writeback=True) as service_records_db:
        record = service_records_db.get(record_id)
        if record is None:
            return jsonify({'error': 'Record not found'}), 404

        subject = record.subject
        chat = record.chat
        date = record.date
        status = record.status
        auto = record.auto

        last_save = record.last_save
        user_id = record.user_id

        # Parse the string as a list of dictionaries
        chat_list = json.loads(chat)
        # Initialize lists to store senders and contents
        senders = []
        contents = []

        # Loop through the list of dictionaries to retrieve the sender and content
        for entry in chat_list:
            sender = entry['sender']
            content = entry['content']
            senders.append(sender)
            contents.append(content)

        return render_template('Customer/custservice/record_detail.html', record=record, senders=senders, contents=contents,
                               subject=subject, date=date, status=status, auto=auto, user_id=user_id, last_save = last_save)


@app.route('/save_service_record', methods=['POST'])
def save_service_record():
    # Get the data from the request
    data = request.get_json()
    global deleted
    record_id = data.get('record_id')

    if not record_id and record_id not in deleted_record_ids:
        # If record_id is not provided, it means we are creating a new record
        total_records = get_total_record_count()
        record_id = f"record_{total_records + 1}"
        with shelve.open("Objects/CustomerService/service_records.db", writeback=True) as service_records_db:
            # Create a new Record object and add it to the service_records_db dictionary
            record = Record(
                record_id=record_id,
                date=data['dateInitiated'],
                chat=data['chatHistory'],
                subject=data['subject'],
                status=data['status'],
                auto=data['auto'],
                user_id=session["id"],
                last_save=data['last_save']
            )
            service_records_db[record_id] = record
    else:
        # If record_id is provided, it means we are updating an existing record
        with shelve.open("Objects/CustomerService/service_records.db", writeback=True) as service_records_db:
            # Check if the record_id exists in the service_records_db dictionary
            if record_id in service_records_db:
                # Update the existing record
                record = service_records_db[record_id]
                record.date = data['dateInitiated']
                record.chat = data['chatHistory']
                record.subject = data['subject']
                record.status = data['status']
                record.auto = data['auto']
                record.user_id = session["id"]
                record.last_save = data['last_save']
            elif record_id not in service_records_db:
                return jsonify({'error': 'Record not found'}), 404

    # Print the updated chat information for regular service_records_db
    with shelve.open("Objects/CustomerService/service_records.db", writeback=True) as service_records_db:
        record = service_records_db.get(record_id)

    # If this is an admin record, save it to the admin database as well
    if record_id:
        with shelve.open("Objects/CustomerService/service_records_admin.db", writeback=True) as service_records_admin_db:
            # Check if the record_id already exists in the service_records_admin_db dictionary
            if record_id in service_records_admin_db:
                # Update the existing admin record
                record_admin = service_records_admin_db[record_id]
                record_admin.date = data['dateInitiated']
                record_admin.chat = data['chatHistory']
                record_admin.subject = data['subject']
                record_admin.status = data['status']
                record_admin.auto = data['auto']
                record_admin.user_id = "Admin"
                record_admin.last_save = data['last_save']
            elif record_id not in service_records_admin_db and record_id not in deleted_record_admin_ids:
                # Create a new admin Record object and add it to the service_records_admin_db dictionary
                total_records = get_total_record_count()
                record_id = f"record_{total_records}"
                record_admin = Record(
                    record_id=record_id,
                    date=data['dateInitiated'],
                    chat=data['chatHistory'],
                    subject=data['subject'],
                    status=data['status'],
                    auto=data['auto'],
                    user_id= "Admin",
                    last_save=data['last_save']
                )
                service_records_admin_db[record_id] = record_admin

        # Print the updated chat information for admin service_records_admin_db
        with shelve.open("Objects/CustomerService/service_records_admin.db", writeback=True) as service_records_admin_db:
            record_admin = service_records_admin_db.get(record_id)
            print("Updated Chat for service_records_admin_db:", record_admin.chat)

    # Return a success response
    return jsonify({'message': 'Record saved successfully'})


@app.route('/delete_record/<record_id>', methods=['DELETE'])
def delete_record(record_id):
    # Check if the record_id exists in the service_records dictionary
    with shelve.open("Objects/CustomerService/service_records.db", writeback=True) as service_records_db:
        if record_id in service_records_db:
            # If the record exists, delete it from the dictionary
            deleted_record_ids.add(record_id)
            with shelve.open("Objects/CustomerService/custservice_deleted_records.db") as custservice_deleted_records_db:
                custservice_deleted_records_db['deleted_record_ids'] = deleted_record_ids
            del service_records_db[record_id]
            return jsonify({'message': 'Record deleted successfully'})
        else:
            # If the record_id does not exist, return an error message
            return jsonify({'error': 'Record not found'}), 404
# Admin side


@app.route('/admin')
def ahome():
    if session['admin_logged_in'] == True:
        orders_data = {
        'product_names': ['Product A', 'Product B', 'Product C'],
        'order_counts': [5, 3, 7]  # Number of orders for each product
    }
        return render_template('/Admin/AdminLoggedInHomepage.html', data=orders_data)
    else:
        return redirect(url_for('Login'))

@app.route('/orders-visualization')
def orders_visualization():
    # Fetch your orders data here. This is just a placeholder.
    orders_data = {
        'product_names': ['Product A', 'Product B', 'Product C'],
        'order_counts': [5, 3, 7]  # Number of orders for each product
    }
    return render_template('orders_visualization.html', data=orders_data)

@app.route('/admin/homepage')
def ahomepage():
    return render_template('/Admin/LoginPage.html')


# Account
@app.route('/adminCreation', methods=['GET', 'POST'])
def AdminRegistrationPage():
    create_admin_form = createAdmin(request.form)
    if request.method == "POST" and create_admin_form.validate():
        # if not request.form.get("user_id")\
        #     or not request.form.get("userName")\
        #     or not request.form.get("userEmail")\
        #     or not request.form.get("userPassword")\
        #     or not request.form.get("userCfmPassword"):
        #         flash("All fields are required to sign up")
        db = shelve.open('Objects/account/user.db', 'c')
        admin_dict = {}
        try:
            admin_dict = db['admins'] #admin_dict = {1:AdminObject, 2:AdminObject} #take everything out
        except:
            db["admins"] = admin_dict
            print("Error in retrieving Users from Objects/account/user.db")

        adminPassword = create_admin_form.adminPassword.data
        adminCfmPassword = create_admin_form.adminCfmPassword.data
        if not adminPassword == adminCfmPassword:
            # flash("Passwords Don't match", category="danger")
            return redirect("/CustomerRegistration")

        admin = Admin( create_admin_form.adminFirstName.data, create_admin_form.adminLastName.data,
                             create_admin_form.adminUserName.data, create_admin_form.adminPassword.data,
                             create_admin_form.adminEmail.data, create_admin_form.adminCfmPassword.data,
                             create_admin_form.adminPhoneNumber.data)

        admin_dict[admin.get_admin_id()] = admin
        db['admins'] = admin_dict #put everything back

        db.close()

        return redirect("/Login")
    return render_template('/Admin/account/AdminRegistration.html', form=create_admin_form)

@app.route('/AdminProfile')
def AdminProfile():
    return render_template('/Admin/account/adminProfile.html')

@app.route('/EditAdminAccount/<int:id>/', methods=['GET', 'POST']) #refer to usersettings "href"
def EditAdminAccount(id):
    edit_admin_form = editAdminAccount(request.form)
    if request.method == 'POST' and edit_admin_form.validate():
        db = shelve.open('Objects/account/user.db', 'c')
        admin_dict = {}
        try:
            admin_dict = db['admins']  # user_dict = {1:UserObject, 2:UserObject} #take everything out
        except:
            db["admins"] = admin_dict
            print("Error in retrieving Users from Objects/account/user.db")

        tempAdmin = admin_dict[id]
        tempAdmin.set_adminFirstName(edit_admin_form.adminFirstName.data)
        tempAdmin.set_adminLastName(edit_admin_form.adminLastName.data)
        tempAdmin.set_adminEmail(edit_admin_form.adminEmail.data)
        tempAdmin.set_adminPhoneNumber(edit_admin_form.adminPhoneNumber.data)

        session['adminfname'] = tempAdmin.get_adminFirstName()
        session['adminlname'] = tempAdmin.get_adminLastName()
        session['adminemail'] = tempAdmin.get_adminEmail()
        session['phonenumber'] = tempAdmin.get_adminPhoneNumber()

        admin_dict[id] = tempAdmin
        db['admins'] = admin_dict
        db.close()

        return redirect(url_for('AdminProfile'))
    else:
        db = shelve.open('Objects/account/user.db', 'r')
        admin_dict = db['admins']
        db.close()

        admin = admin_dict.get(id)
        edit_admin_form.adminFirstName.data = admin.get_adminFirstName()
        edit_admin_form.adminLastName.data = admin.get_adminLastName()
        edit_admin_form.adminEmail.data = admin.get_adminEmail()
        edit_admin_form.adminPhoneNumber.data = admin.get_adminPhoneNumber()
        return render_template('Admin/account/editAdminProfile.html', form=edit_admin_form)

@app.route('/listCustomerAccounts')
def listCustomerAccounts():
    users_dict = {}
    db = shelve.open('Objects/account/user.db', 'r')
    users_dict = db['users']
    db.close()
    users_list = []
    for key in users_dict:
        user = users_dict[key]
        users_list.append(user)
    return render_template('/Admin/account/ListCustomerAccount.html', count=len(users_list), usersList=users_list)

@app.route('/listAdminAccounts')
def listAdminAccounts():
    admins_dict = {}
    db = shelve.open('Objects/account/user.db', 'r')
    admins_dict = db['admins']
    db.close()
    admins_list = []
    for key in admins_dict:
        admin = admins_dict[key]
        admins_list.append(admin)
    return render_template('/Admin/account/ListAdminAccount.html', count=len(admins_list), adminsList=admins_list)


# Transaction
@app.route('/view_order/<order_id>')
def view_order(order_id):
    # Retrieve the order details from the database based on order_id
    db = shelve.open('Objects/transaction/order.db', 'r')
    order = db.get(order_id)
    db.close()

    # Render the view modal with the order details
    return render_template('view_order.html', order=order)


@app.route('/delete_order/<order_id>', methods=['POST'])
def delete_order(order_id):
    # Open the shelve database
    db = shelve.open('Objects/transaction/order.db', 'w')

    # Check if the order_id exists in the database
    if order_id in db:
        # Delete the order from the database
        del db[order_id]
        db.close()

    # Redirect back to the order page
    return redirect(url_for('order'))


@app.route('/admin/order')
def order():
    order_list = []
    db_path = 'Objects/transaction/order.db'
    if not os.path.exists(db_path):
        db = shelve.open(db_path, 'c')
        db.close()

    db = shelve.open(db_path, 'r')
    for key in db:
        order = db.get(key)
        order_list.append(order)
    db.close()
    return render_template('/Admin/transaction/order.html', order_list=order_list, count=len(order_list))


@app.route('/admin/add_product', methods=['POST'])
def add_product():
    name = request.form['name'].strip().title()
    color_options = request.form.get('color_options').split(',')
    # Remove leading/trailing spaces
    color_options = [option.strip() for option in color_options]
    size_options = request.form.get('size_options').split(',')
    size_options = [option.strip() for option in size_options]
    cost_price = float(request.form['cost_price'])
    list_price = float(request.form['list_price'])
    stock = max(int(request.form['stock']), 0)
    description = request.form['description'].strip()
    image = request.form['image'].strip()
    category = request.form['category'].strip()
    print(name, color_options, size_options, cost_price, list_price, stock, description, image, category)

    # Update the product_dict with the new product
    db = shelve.open('Objects/transaction/product.db', 'w')
    # Add stripe product
    max_id = 0
    for key in db:
        key = key[1:]
        if int(key) > max_id:
            max_id = int(key)
    product_id = "P" + str(max_id + 1)

    product = Product(product_id, name, color_options, size_options, cost_price,
                      list_price, stock, description, image, category)
    # stripe payment
    for color in product.color_options:
        for size in product.size_options:
            try:
                stripe_details = stripe.Product.create(
                    name=f"{product.name} | {color} | {size}",
                    default_price_data={
                        "unit_amount": int(float(list_price) * 100),
                        "currency": "sgd",
                    },
                    images=[product.image],
                )
                stripe.Product.modify(
                    stripe_details["id"],
                    url=Domain+"/product/"+product.productid,
                )
            except Exception as e:
                print(
                    f"Failed to create product {product.product_id}: {str(e)}")
    product_id = product.product_id
    db[product_id] = product
    db.close()

    # Redirect back to the product page
    return redirect(url_for('product_admin'))


@app.route('/admin/update_product/<product_id>', methods=['POST'])
def update_product(product_id):
    # Retrieve the form data
    name = request.form['name'].strip().title()
    color_options = request.form.get('color_options').split(',')
    color_options = [option.strip() for option in color_options]
    size_options = request.form.get('size_options').split(',')
    size_options = [option.strip() for option in size_options]
    cost_price = float(request.form['cost_price'])
    list_price = float(request.form['list_price'])
    stock = max(int(request.form['stock']), 0)
    description = request.form['description'].strip()
    image = request.form['image'].strip()
    category = request.form['category'].strip()

    # Update the product in the database
    db = shelve.open('Objects/transaction/product.db', 'w')

    if product_id in db:
        productobj = db[product_id]
        productobj.name = name
        productobj.color_options = color_options
        productobj.size_options = size_options
        productobj.cost_price = cost_price
        productobj.list_price = list_price
        productobj.stock = stock
        productobj.description = description
        productobj.image = image
        productobj.category = category
        db[product_id] = productobj

    # Find the base product
    base_product = find_product(name)

    base_product = base_product[0]  # Assuming find_product returns a list

    # Save the old default price ID
    old_default_price_id = base_product['default_price']
    # Create a new price for the base product
    default_price = stripe.Price.create(
        product=base_product['id'],
        unit_amount=int(float(list_price) * 100),
        currency="sgd",
    )

    stripe.Product.modify(base_product['id'], default_price=default_price['id'])

    # Now you should be able to archive the old default price
    stripe.Price.modify(old_default_price_id, active=False)

    # Now handle the product variants
    for color in color_options:
        for size in size_options:
            # Check if the variant already exists
            variant_product = find_product(name, color, size)

            if len(variant_product) == 0:
                # Create a new price for the variant
                variant_price = stripe.Price.create(
                    product=variant_product['id'],
                    unit_amount=int(float(list_price) * 100),
                    currency="sgd",
                )

                # Save the old default price ID for the variant
                old_default_price_id = variant_product['default_price']

                stripe.Product.modify(
                    variant_product['id'], default_price=variant_price['id'])

                # Now you should be able to archive the old default price for the variant
                stripe.Price.modify(old_default_price_id, active=False)

    db.close()

    # Redirect back to the product page
    return redirect(url_for('product_admin'))


@app.route('/admin/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    # Open the shelve database
    db = shelve.open('Objects/transaction/product.db', 'w')

    # Check if the product_id exists in the database
    if product_id in db:
        # Delete the product from the database
        product = db[product_id]
        product_name = product.name
        stripe_product_list = find_product(product_name)
        # for item in stripe_product_list:
        #     stripe.Product.delete(item["id"])
        del db[product_id]
        db.close()

    # Redirect back to the product page
    return redirect(url_for('product_admin'))


def join_and_filter(list_):
    """This function joins a list of strings with commas and spaces, but with 'and' before the last item. This would be used
    to display the color_options."""
    if len(list_) > 1:
        return ', '.join(list_[:-1]) + ' and ' + list_[-1]
    elif list_:
        return list_[0]
    else:
        return ''


app.jinja_env.filters['join_and'] = join_and_filter


@app.route('/admin/product')
def product_admin():
    product_list = []
    product_dict = {}
    db_path = 'Objects/transaction/product.db'
    if not os.path.exists(db_path):
        placeholder_data = [
            {
                "product_id": "P1",
                "name": "Women's Tri-Blend T-Shirt",
                "color_options": ["Red", "Black"],
                "size_options": ["S", "M"],
                "cost_price": 15,
                "list_price": 25,
                "stock": 54,
                "description": "Elevate your workout style with our Women’s Tri-Blend T-Shirt. Crafted for both comfort and performance, this shirt is a must-have for fitness enthusiasts. Its soft, breathable fabric ensures you stay cool during your workouts, while the flattering design keeps you looking chic. Priced at just $25, it's an affordable addition to your fitness wardrobe.",
                "image": "https://m.media-amazon.com/images/I/81NkOeFp8yL._AC_SL1500_.jpg",
                "category": "Fitness Apparel"
            },
            {
                "product_id": "P2",
                "name": "Men's Tri-Blend T Shirt",
                "color_options": ["Grey", "White"],
                "size_options": ["M", "L"],
                "cost_price": 15,
                "list_price": 25,
                "stock": 45,
                "description": "Introducing our Men’s Tri-Blend T-Shirt - the perfect fusion of style and functionality. Priced at $25, this shirt offers unbeatable value for your fitness attire. With its premium fabric and comfortable fit, it's your go-to choice for workouts and beyond.",
                "image": "https://m.media-amazon.com/images/I/61lU+iSVXQL._AC_SY741_.jpg",
                "category": "Fitness Apparel"
            },
            {
                "product_id": "P3",
                "name": "Motivational 1L Sports Water Bottle",
                "cost_price": 10,
                "list_price": 15,
                "stock": 13,
                "description": "Stay hydrated and motivated with our Motivational 1L Sports Water Bottle. With inspiring quotes to fuel your fitness journey, this bottle is your constant companion. Priced affordably, it's a reminder to keep pushing towards your goals.",
                "image": "https://m.media-amazon.com/images/I/81sRIW9C0xL._AC_SL1500_.jpg",
                "category": "Fitness Apparel"
            },
            {
                "product_id": "P4",
                "name": "OPTIMUM NUTRITION Gold Standard 100% Whey Protein Powder 2LB",
                "cost_price": 60,
                "list_price": 75,
                "stock": 30,
                "description": "Fuel your muscles with the best - OPTIMUM NUTRITION Gold Standard Whey Protein. With 24 grams of protein per serving, it's the gold standard for muscle recovery and growth. Get it now and maximize your fitness gains.",
                "image": "https://m.media-amazon.com/images/I/61TKrit75mL._AC_SL1500_.jpg",
                "category": "Nutritional Supplements"
            },
            {
                "product_id": "P5",
                "name": "OPTIMUM NUTRITION Micronized Create Monohydrate Powder, Unflavored, Keto Friendly, 1.32LB",
                "cost_price": 65,
                "list_price": 80,
                "stock": 25,
                "description": "Boost your workout performance with OPTIMUM NUTRITION Creatine Monohydrate. This unflavored, keto-friendly powder is a game-changer for strength and endurance. Elevate your fitness regimen with this essential supplement.",
                "image": "https://m.media-amazon.com/images/I/71kQRMrkPdL._AC_SL1500_.jpg",
                "category": "Nutritional Supplements"
            },
            {
                "product_id": "P6",
                "name": "Gratitude: A Day and Night Reflection Journal (90 Days)",
                "cost_price": 10,
                "list_price": 15,
                "stock": 13,
                "description": "A Day and Night Reflection Journal will help you center your day around positive feelings and gratitude. It’s the perfect place to record and celebrate anything that you are grateful for and to preserve important memories. This 90-day journal gives you a path to creating a habit of daily gratitude that you can carry with you throughout your life. Cultivating gratitude is one of the most potent and important mindfulness exercises, and thankfulness has proven to have a positive effect on a person's mental health and general well-being.<br>Each page of the journal includes space to record expressions of gratitude, personal affirmations, memories of positive interactions, and commentaries on the significance of it all. The journal is intended for those who want to foster deep reflection as well as for those who simply want to discover the effects of thankfulness. Having filled the journal with statements of gratitude, you will end up with a personal trove of wonderful reflections, which can be a source of positive inspiration at any time.",
                "image": "https://m.media-amazon.com/images/I/71TDknMziYL.jpg",
                "category": "Wellness Journal"
            },
            {
                "product_id": "P7",
                "name": "SMART Goal Journal",
                "cost_price": 10,
                "list_price": 15,
                "stock": 52,
                "description": "Achieve your fitness goals with our SMART Goal Journal. Set specific, measurable, attainable, relevant, and time-bound goals. Stay on track and watch your progress soar.",
                "image": "https://m.media-amazon.com/images/I/313fVsC25oL.jpg",
                "category": "Wellness Journal"
            },
            {
                "product_id": "P8",
                "name": "Nutrition Logbook",
                "cost_price": 10,
                "list_price": 15,
                "stock": 132,
                "description": "Track your nutrition with our Nutrition Logbook. Whether you're counting macros or simply eating mindfully, this logbook is your tool for nutritional success.",
                "image": "https://m.media-amazon.com/images/I/710XGSnEAzL.jpg",
                "category": "Wellness Journal"
            },
            {
                "product_id": "P9",
                "name": "FLYBIRD Adjustable Dumbbells, 25/30/50/55lb",
                "cost_price": 150,
                "list_price": 250,
                "stock": 23,
                "description": "Transform your home into a personal gym with FLYBIRD Adjustable Dumbbells. These versatile weights allow you to tailor your workouts to your fitness level. Say goodbye to expensive gym memberships.",
                "image": "https://m.media-amazon.com/images/I/71T31CPFA+L._AC_SL1500_.jpg",
                "category": "Home Gym"
            },
            {
                "product_id": "P10",
                "name": "Wall Mounted - Pullup Bar",
                "cost_price": 10,
                "list_price": 15,
                "stock": 25,
                "description": "Take your upper body strength to new heights with our Wall Mounted Pull-up Bar. Easy to install at home, it's the perfect addition to your fitness space. Get ready to conquer those pull-ups.",
                "image": "https://m.media-amazon.com/images/I/41SJeg-B01L._AC_SL1024_.jpg",
                "category": "Home Gym"
            },
        ]
        # stripe payment
        for product in placeholder_data:
            # if the keys cost_price and list_price are in product.
            print(list(product.keys()))
            print("color_options" in list(product.keys()))
            if "color_options" in list(product.keys()) and "size_options" in list(product.keys()):
                for color in product["color_options"]:
                    for size in product["size_options"]:
                        try:
                            stripe.Product.create(
                                name=f"{product['name']} | {color} | {size}",
                                default_price_data={
                                    "unit_amount": int(product["list_price"] * 100),
                                    "currency": "sgd",
                                },
                                images=[product["image"]],
                            )
                        except Exception as e:
                            print(
                                f"Failed to create product {product['product_id']}: {str(e)}")
            else:
                try:
                    stripe.Product.create(
                        name=product['name'],
                        default_price_data={
                            "unit_amount": int(product["list_price"] * 100),
                            "currency": "sgd",
                        },
                        images=[product["image"]],
                    )
                except Exception as e:
                    print(
                        f"Failed to create product {product['product_id']}: {str(e)}")

        db = shelve.open(db_path, 'c')
        for data in placeholder_data:
            if "color_options" in list(data.keys()) and "size_options" in list(data.keys()):

                product = Product(
                    data["product_id"],
                    data["name"],
                    data["color_options"],
                    data["size_options"],
                    float(data["cost_price"]),
                    float(data["list_price"]),
                    data["stock"],
                    data["description"],
                    data["image"],
                    data["category"],
                )
                db[product.product_id] = product
            else:
                product = Product(
                data["product_id"],
                data["name"],
                None,
                None,
                float(data["cost_price"]),
                float(data["list_price"]),
                data["stock"],
                data["description"],
                data["image"],
                data["category"],
                )
                db[product.product_id] = product
        db.close()

    db = shelve.open(db_path, 'r')
    # open the db and retrieve the dictionary
    for key in db:
        # key is product ID
        product = db[key]
        product_dict[key] = product
    db.close()
    for key in product_dict:
        product = product_dict.get(key)
        product_list.append(product)
    # prints out all the products and their info
    for product in product_list:
        print(product.product_id, product.name, product.color_options, product.size_options, product.cost_price, product.list_price, product.stock, product.description, product.image, product.category)
        print("Product_ID: ", product.product_id, "\n", "Product Name: ", product.name, "\n", "Color Options: ", product.color_options, "\n", "Size Options: ", product.size_options, "\n", "Cost Price: ", product.cost_price, "\n", "List Price: ", product.list_price, "\n", "Stock: ", product.stock, "\n", "Description: ", product.description, "\n", "Image: ", product.image, "\n", "Category: ", product.category, "\n")
    return render_template('/Admin/transaction/product.html', product_list=product_list, count=len(product_list))
def find_product(name, color=None, size=None):
    matching_products = []
    stripe_product_dict = stripe.Product.list(limit=100)["data"]
    for product in stripe_product_dict:
        product_name = product["name"]
        if color and size:
            # if color and size are specified, check for exact match
            # print(f"Checking if {name} | {color} | {size} is {product_name}")
            if product_name == f"{name} | {color} | {size}":
                return product
        else:
            # if color and size are not specified, check if the product name matches
            if name in product_name:
                matching_products.append(product)
    return matching_products


@app.route('/admin/delete_review/<review_id>', methods=['POST'])
def delete_review(review_id):
    db_path = 'Objects/transaction/review.db'
    db = shelve.open(db_path, 'w')
    try:
        del db[str(review_id)]
    except KeyError:
        pass
    db.close()
    return redirect(url_for('review'))


@app.route('/admin/review')
def review():
    review_list = []
    db_path = 'Objects/transaction/review.db'
    if not os.path.exists(db_path):
        placeholder_reviews = [
            {
                "review_id": "R1",
                "product_id": "P1",
                "user_id": 1,
                "author": "John Doe",
                "rating": 4,
                "description": "Great product! Love it.",
            },
            {
                "review_id": "R2",
                "product_id": "P1",
                "user_id": 2,
                "author": "Jane Smith",
                "rating": 5,
                "description": "Excellent quality and fast delivery.",
            },
            {
                "review_id": "R3",
                "product_id": "P2",
                "user_id": 3,
                "author": "Mike Johnson",
                "rating": 3,
                "description": "Decent product, but could be better.",
            },
            {
                "review_id": "R4",
                "product_id": "P2",
                "user_id": 4,
                "author": "Sarah Lee",
                "rating": 5,
                "description": "Absolutely amazing! Highly recommended.",
            },
            {
                "review_id": "R5",
                "product_id": "P3",
                "user_id": 5,
                "author": "Chris Williams",
                "rating": 4,
                "description": "Nice product for the price.",
            },
        ]

        # Save the placeholder reviews to the review.db database
        db_path = 'Objects/transaction/review.db'
        db = shelve.open(db_path, 'c')
        for data in placeholder_reviews:
            review = Review(
                data["review_id"],
                data["product_id"],
                data["user_id"],
                data["author"],
                data["rating"],
                data["description"],
            )
            db[str(review.review_id)] = review
        db.close()

    db = shelve.open(db_path, 'r')
    # Assuming reviews are stored in the 'review' shelve
    review_list = list(db.values())
    db.close()

    return render_template('Admin/transaction/review.html', review_list=review_list, count=len(review_list))


@app.route('/admin/code')
def promocode():
    code_list = []
    db_path = 'Objects/transaction/promo.db'

    if not os.path.exists(db_path):
        db = shelve.open(db_path, 'c')
        db.close()

    db = shelve.open(db_path, 'r')
    for key in db:
        code = db[key]
        code_list.append(code)
    db.close()
    return render_template('/Admin/transaction/promocode.html', code_list=code_list, count=len(code_list))


@app.route('/admin/add_promo', methods=['POST'])
def add_promo():
    if request.method == 'POST':
        code = request.form['code']
        discount = float(request.form['discount'])
        end_date = request.form['end_date']
        date = datetime.strptime(str(end_date), '%Y-%m-%d')
        db = shelve.open('Objects/transaction/promo.db', 'w')
        unix_timestamp = int(time.mktime(date.timetuple()))
        if code not in db:
            coupon = stripe.Coupon.create(
                percent_off=discount,
                duration='once',
                redeem_by=unix_timestamp,
            )
            promocode = stripe.PromotionCode.create(
                coupon=coupon['id'],
                code=code,
            )
            promo = Code(code, discount, end_date,
                         coupon['id'], promocode['id'])
            db[promo.code] = promo
        db.close()
    return redirect(url_for('promocode'))


@app.route('/admin/update_code/<code>', methods=['POST'])
def update_code(code):
    if request.method == 'POST':
        discount = float(request.form['discount'])
        end_date = request.form['end_date']
        date = datetime.strptime(str(end_date), '%Y-%m-%d')
        unix_timestamp = int(time.mktime(date.timetuple()))
        db = shelve.open('Objects/transaction/promo.db', 'w')
        stripe.Coupon.delete(db[code].coupon_id)
        coupon = stripe.Coupon.create(
            percent_off=discount,
            duration='once',
            redeem_by=unix_timestamp,
        )
        promocode = stripe.PromotionCode.create(
            coupon=coupon['id'],
            code=code,
        )
        promo = Code(code, discount, end_date, coupon['id'], promocode['id'])
        db[promo.code] = promo
        db.close()
    return redirect(url_for('promocode'))


@app.route('/admin/delete_code/<code>', methods=['POST'])
def delete_code(code):
    db = shelve.open('Objects/transaction/promo.db', 'w')
    if code in db:
        stripe.Coupon.delete(db[code].coupon_id)
        del db[code]
    db.close()
    return redirect(url_for('promocode'))

# Customer Service


@app.route('/RecordDetailAdmin/<record_id>')
def RecordDetailAdmin(record_id):
    # Find the record with the given record_id
    with shelve.open("Objects/CustomerService/service_records_admin.db", writeback=True) as service_records_admin_db:
        record = service_records_admin_db.get(record_id)
        if record is None:
            return jsonify({'error': 'Record not found'}), 404

        subject = record.subject
        chat = record.chat
        date = record.date
        status = record.status
        auto = record.auto
        last_save = record.last_save

        # Parse the string as a list of dictionaries
        chat_list = json.loads(chat)
        # Initialize lists to store senders and contents
        senders = []
        contents = []

        # Loop through the list of dictionaries to retrieve the sender and content
        for entry in chat_list:
            sender = entry['sender']
            content = entry['content']
            senders.append(sender)
            contents.append(content)

        return render_template('/Admin/custservice/RecordDetailAdmin.html', record=record, senders=senders, contents=contents,
                               subject=subject, date=date, status=status, auto=auto)


@app.route('/ServiceRecordAdmin')
def ServiceRecordAdmin():
    with shelve.open("Objects/CustomerService/service_records_admin.db", writeback=True) as service_records_admin_db:
        return render_template('/Admin/custservice/ServiceRecordAdmin.html', service_records=service_records_admin_db)


@app.route('/delete_record_admin/<record_id>', methods=['DELETE'])
def delete_record_admin(record_id):
    # Check if the record_id exists in the service_records dictionary
    with shelve.open("Objects/CustomerService/service_records_admin.db", writeback=True) as service_records_admin_db:
        if record_id in service_records_admin_db:
            # If the record exists, delete it from the dictionary
            deleted_record_admin_ids.add(record_id)
            with shelve.open("Objects/CustomerService/custservice_deleted_records_admin.db") as custservice_deleted_records_admin_db:
                custservice_deleted_records_admin_db['deleted_record_admin_ids'] = deleted_record_admin_ids
            del service_records_admin_db[record_id]
            return jsonify({'message': 'Record deleted successfully'})
        else:
            # If the record_id does not exist, return an error message
            return jsonify({'error': 'Record not found'}), 404


def get_faqs_from_shelve():
    with shelve.open("Objects/CustomerService/faqs.db") as db:
        return db.get("faqs", [])


def save_faqs_to_shelve(faqs):
    with shelve.open("Objects/CustomerService/faqs.db") as db:
        db["faqs"] = faqs


@app.route('/FAQAdmin', methods=['GET', 'POST'])
def FAQAdmin():
    if request.method == 'POST':
        # Get the new section, question, and answer from the form submitted
        new_section = request.form['new_section']
        new_question = request.form['new_question']
        new_answer = request.form['new_answer']

        # Retrieve the FAQs from the shelve database
        faqs = get_faqs_from_shelve()

        # Find the section in the existing FAQs or add a new one
        for section_data in faqs:
            if section_data['section'] == new_section:
                section_data['questions'].append(new_question)
                section_data['answers'].append(new_answer)
                break

        # Save the updated FAQs back into the shelve database
        save_faqs_to_shelve(faqs)

    # Retrieve the FAQs from the shelve database
    faqs = get_faqs_from_shelve()

    return render_template('/Admin/custservice/FAQAdmin.html', faqs=faqs)

@app.route('/update_faq', methods=['POST'])
def update_faq():
    # Handle form submission for updating question and answer
    section_to_update = request.form['update_section']
    index = int(request.form['update_index'])
    updated_question = request.form['update_question']
    updated_answer = request.form['update_answer']
    faqs = get_faqs_from_shelve()
    # Update the question and answer in the list under the specified section
    for section in faqs:
        if section['section'] == section_to_update:
            section['questions'][index] = updated_question
            section['answers'][index] = updated_answer
    save_faqs_to_shelve(faqs)

    # Redirect back to the FAQAdmin page after updating the question and answer
    return redirect(url_for('FAQAdmin', faqs=faqs))


@app.route('/delete_faq', methods=['POST'])
def delete_faq():
    section = request.form['section']
    index = int(request.form['index'])
    # Retrieve the FAQs from the shelve database
    faqs = get_faqs_from_shelve()

    # Delete the question and answer from the FAQs list using the section and index
    for section_data in faqs:
        if section_data['section'] == section:
            del section_data['questions'][index]
            del section_data['answers'][index]
            break
    save_faqs_to_shelve(faqs)

    return redirect(url_for('FAQAdmin', faqs=faqs))
    # FAQ data
# FAQ data
faqs = [
    {
        "section": "Order Issues",
        "questions": ["How to check my order status?", "Why didn't I get an email about my order being shipped?",
                      "How long will shipping take for my order?", "I'm having technical difficulties on the Transaction Processing Page. What should I do?", "Can I modify my order after the transaction is completed?"],

        "answers": ["You will receive the shipping inform email within 1 business day after the order is shipped",
                    "There may be delays with the shipping", "Shipping usually takes about 1-3 days", "Please ensure your browser is updated, clear your cookies and cache, and try again. If the problem persists, contact our customer support for assistance.",
                    "If you need to make changes to your order after completing the transaction, please contact our customer service through our customer service page immediately. We'll do our best to accommodate your request, but changes cannot be guaranteed once the order enters the fulfillment process."]
    },
    {
        "section": "Promotions",
        "questions": ["I have a promo code. Where can I enter it?"],
        "answers": ["On our checkout page, below the order summary, you can enter your promo code there. Click apply to see your updated total. Note that the discount applies to the subtotal, not the delivery."]
    },
    {
        "section": "Account",
        "questions": ["Do you store my payment details for future transactions?"],
        "answers": ["No, we prioritize your security. We do not store any sensitive payment details on our servers. Some customers may opt for tokenized storage through our payment gateways for easier checkouts in the future via link authentication, but this is entirely voluntary."]
    },
    {
        "section": "Delivery",
        "questions": ["What are the available locations for shipping?", "How do you deliver your products?"],
        "answers": ["We only ship to Singapore for now, but we are planning on expanding our services to other countries soon!", "As a sustainability brand, we only deliver our products using carbon neutral methods like electric vehicles."]
    },
    {
        "section": "Refund",
        "questions": ["Do you offer refunds?", "What are the conditions for a refund to occur"],
        "answers": ["Yes, we do offer refunds. Once you complete an order, you can press on the 'Cancel & Refund' button, and the money will be sent back to you by Stripe. However, we do not accept refunds after the order is shipped.", "The conditions are that the order has not been shipped or if we have made a mistake."]
    },
    {
        "section": "General",
        "questions": ["Is it safe to enter my credit card details?", "Do you store my payment details for future transactions?", "Why can't I change the country in the checkout page?"],
        "answers": ["Absolutely. Our e-commerce website utilizes the Stripe API for payment processing. Stripe is a globally recognized payment solution that prioritizes security:"
                    "End-to-End Encryption: Stripe ensures that your card details are encrypted from the moment you enter them. This information is sent directly to Stripe and never touches our servers."
                    "PCI DSS Compliance: Stripe is certified as a PCI Level 1 Service Provider, the most stringent level of certification available. This ensures that they maintain and adhere to the highest security standards in the payment industry."
                    "Advanced Fraud Detection: Stripe employs advanced machine learning algorithms to detect and prevent fraudulent transactions, providing an extra layer of protection for your payments."
                    "Tokenization: When you enter your card details, Stripe replaces sensitive information with tokens. This means that even if someone were to intercept this data, they wouldn't be able to decipher your actual card details."
                    "For more details on Stripe's security measures, you can visit their security page.",
                    "No, we prioritize your security. We do not store any sensitive payment details on our servers. Some customers may opt for tokenized storage through our payment gateways for easier checkouts in the future via link authentication, but this is entirely voluntary.",
                    "We're sorry, but we only ship to Singapore for the time being. We may expand to international borders in the future, thank you for your support!"]

    } ]
if get_faqs_from_shelve() == '':
    save_faqs_to_shelve(faqs)

# Teacher


if __name__ == '__main__':    app.run(debug=True)
	