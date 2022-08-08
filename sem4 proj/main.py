from flask import Flask, render_template, request, redirect,url_for, logging,flash,session
import os
from flask_mysqldb import MySQL
import yaml
import json
# from data import Articles
# from wtforms import Form, BooleanField, StringField, PasswordField, validators
# from passlib.hash import sha256_crypt
# from functools import wraps
from datetime import date
from flask import request
from datetime import datetime
import requests 

app = Flask(__name__)

picFolder = os.path.join('static', 'pics')
print(picFolder)
app.config['UPLOAD_FOLDER'] = picFolder

db = yaml.load(open('db.yaml'),Loader=yaml.FullLoader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

# @app.route('/',methods = ['GET', 'POST'])
# def orderszz():
#     if request.method == 'POST':
#         userDetails=request.form
#         order_id = userDetails['orderid']
#         customer_id = userDetails['customerid']
#         advance = userDetails['Advance']
#         status = userDetails['Status']
#         item_id = userDetails['Itemid']
#         quantity=userDetails['Quantity']
#         del_date=userDetails['ExpectedDeliveryDate']
#         place_date=userDetails['PlacementDate']
#         cur = mysql.connection.cursor()
#         item_list=item_id.split(',')
#         quantity_list=quantity.split(',')
#         cur.execute("INSERT INTO orders(order_id,customer_id,advance,status,del_date,place_date) VALUES(%s, %s, %s, %s, %s,%s)",(order_id,customer_id,advance,status,del_date,place_date))
#         for i in range(len(item_list)):
#             cur.execute("INSERT INTO orders_norm(order_id,item_id,quantity,customer_id) VALUES (%s, %s, %s)",(order_id,item_list[i],quantity_list[i],customer_id))
        
#         mysql.connection.commit()
#         cur.close()
        
#         return redirect(url_for('users'))
  
#     return render_template('order.html')


# @app.route('/users')
# def users():
#     cur = mysql.connection.cursor()
#     resultValue = cur.execute("SELECT  orders.order_id,orders.customer_id,orders.advance,orders.status,orders.del_date,orders.place_date, GROUP_CONCAT(orders_norm.item_id SEPARATOR ', '),GROUP_CONCAT(orders_norm.quantity SEPARATOR ', ') from  orders inner join orders_norm on orders.order_id=orders_norm.order_id group by orders_norm.order_id")
#     if resultValue > 0:
#         userDetails = cur.fetchall()
#         return render_template('users.html',userDetails=userDetails)




@app.route('/',methods = ['GET', 'POST'])
def login():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if request.method == 'POST':
        userDetails=request.form
        pwd=userDetails['pwd']
        phone=userDetails['phone']
        optradio=userDetails['optradio']
        cur = mysql.connection.cursor()
        
        if(optradio == "manager"):
            resultValue =cur.execute("SELECT * from man_person where pri_phone=%s and password=%s",(phone,pwd))
            if resultValue > 0:
                userDetails = cur.fetchall()
                session['logged_in'] = True
                # flash('You are now logged in', 'success')
                return redirect('dashboard')
            else:
                flash("Invalid Manager's Phone Number / password.")
                # error = 'Invalid Manager Phone Number / password.'
                return render_template('login.html')
        elif(optradio == "employee"):
            resultValue =cur.execute("SELECT * from emp_person where pri_phone=%s and password=%s",(phone,pwd)) 
            if resultValue > 0:
                session['logged_in'] = True
                userDetails = cur.fetchall()
                # flash('You are now logged in', 'success')
                print(phone)
                data=json.dumps({"phone":phone, "pwd":pwd})
                print(data)
                return redirect("http://localhost:5000/emp_dashboard", code=307)
                # requests.post("http://localhost:5000/emp_dashboard", json=data,headers={"ContentType":"application/json"})
                # print(r)
                # return redirect('emp_dashboard')
                # return render_template('emp_dashboard.html',userDetails=userDetails,user_image1=pic1)
            else: 
                flash("Invalid Employee's Phone Number / password.")
                return render_template('login.html')
        else:
            return 'Wrong entry1'
        mysql.connection.commit()
        cur.close()
        
    return render_template('login.html')

#Check if User is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized! Please login', 'danger')
            return redirect(url_for('/'))
    return wrap


# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect("http://localhost:5000/", code=302)

# @app.route('/empdashboard',methods = ['GET', 'POST'])
# def empdashboard():
#     return render_template('EmployeeModule.html')

@app.route('/dashboard',methods = ['GET', 'POST'])
def dashboard():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        return render_template('Manager.html',user_image1=pic1)
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/emp_dashboard',methods = ['GET', 'POST'])
def emp_dashboard():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    print(session)
    print("redirect data",request.form)
    data=request.form
    # print(data["phone"])
    # if 'logged_in' in session:
    cur = mysql.connection.cursor()
    # print(request)
    # data = json.loads(request.get_json())

    # print(data)
    cur.execute("SELECT * from emp_person where pri_phone=%s and password=%s",(data["phone"],data["pwd"]))
    userDetails=cur.fetchall()
    print(userDetails)
    return render_template('emp_dashboard.html',userDetails=userDetails,user_image1=pic1)
    # else:
    #     return redirect("http://localhost:5000/", code=302)
# show all employee details

@app.route('/emp_details',methods = ['GET', 'POST'])
def emp_details():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        cur = mysql.connection.cursor()
        resultValue=cur.execute("SELECT emp_id,aadhar, CONCAT(first_name,' ',last_name),DATE_FORMAT(doj, '%d/%m/%Y'),job ,DATE_FORMAT(dob, '%d/%m/%Y') ,father,salary ,DATE_FORMAT(layoff, '%d/%m/%Y') ,password,state,pri_phone,sec_phone from emp_person")
        # entry=None
        if resultValue>0:
            userDetails =cur.fetchall()
            return render_template('employee.html',userDetails=userDetails,user_image1=pic1)
        else:
            flash('No Data Found')
            return render_template('employee.html',userDetails=userDetails,user_image1=pic1)
    else:
        return redirect("http://localhost:5000/", code=302)
#  insert new employee details
@app.route('/del_emp',methods = ['GET','POST'])
def del_emp():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            cur = mysql.connection.cursor()
            userDetails=request.form
            first_name=userDetails['first_name']
            emp_id=userDetails['emp_id']
            resultValue=cur.execute("DELETE from emp_person where emp_id=%s and first_name=%s",(emp_id,first_name))
            print(resultValue)
            if resultValue>0:
                mysql.connection.commit()
                cur.close()
                flash("Deleted successfully!!!")
                return redirect(url_for('emp_details'))
            else: 
                flash("Wrong Entry!!!")
                return redirect(url_for('emp_details'))
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/new_emp',methods = ['GET','POST'])
def new_emp():
    if request.method == 'POST':
        userDetails=request.form
        print(userDetails)
        # emp_id=userDetails['empid']
        aadhar=userDetails['Aadhar']
        first_name=userDetails['first_name']
        last_name=userDetails['last_name']
        doj=userDetails['jod']
        job=userDetails['job']
        father=userDetails['father']
        salary=userDetails['salary']
        dob=userDetails['dob']
        # age=None
        layoff=None
        password=userDetails['password']
        state=userDetails['state']
        pri_phone=userDetails['phone']
        sec_phone=userDetails['sec_phone']
        cur = mysql.connection.cursor()
        resultValue=cur.execute("select * from emp_person where (aadhar=%s or pri_phone=%s) ",(aadhar,pri_phone))
        if resultValue==0:
            cur.execute("INSERT INTO emp_person(  aadhar,first_name,last_name,doj,job ,dob ,father,salary,layoff ,password,state,pri_phone,sec_phone)VALUES(%s, %s, %s, %s,%s,%s,%s, %s, %s, %s,%s,%s,%s)",( aadhar,first_name,last_name,doj,job ,dob ,father,salary,layoff ,password,state,pri_phone,sec_phone))
            mysql.connection.commit()
            cur.close()
            flash("New Data Entered!!!")
            return redirect(url_for('emp_details'))
        else: 
            flash("Wrong Entry,Try Again!!!")
            return redirect(url_for('emp_details'))
    return render_template('employee.html')

# @app.route('/empdata',methods = ['GET','POST'])
# def new_emp():
#     if request.method=='POST':



@app.route('/exist_emp',methods = ['GET', 'POST'])
def exist_emp():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            emp_id=userDetails['userInput']
            print(type(emp_id))
            cur = mysql.connection.cursor()
            resultValue=cur.execute("SELECT emp_id,aadhar, CONCAT(first_name,' ',last_name),DATE_FORMAT(doj, '%%d/%%m/%%Y'),job ,DATE_FORMAT(dob, '%%d/%%m/%%Y') ,father,salary ,DATE_FORMAT(layoff, '%%d/%%m/%%Y') ,password,state,pri_phone,sec_phone,first_name,last_name,doj,dob from emp_person where emp_id=%s",[emp_id])
            if resultValue>0:
                userDetails =cur.fetchall()
                # flash("Data found!!!")
                return render_template('updateemp.html',userDetails=userDetails,user_image1=pic1,emp_id=emp_id)
            else: 
                flash("Wrong Entry!!!")
                return redirect(url_for('emp_details'))
    else:
        return redirect("http://localhost:5000/", code=302)

# update existing entry 
@app.route('/upd_emp',methods=['GET','POST'])
def upd_emp():
    if 'logged_in' in session:
        if request.method=='POST':
            userDetails=request.form
            aadhar=userDetails['Aadhar']
            first_name=userDetails['first_name']
            last_name=userDetails['last_name']
            doj=userDetails['jod']
            job=userDetails['job']
            father=userDetails['father']
            salary=userDetails['salary']
            dob=userDetails['dob']
            # age=None
            layoff=None
            password=userDetails['password']
            state=userDetails['state']
            pri_phone=userDetails['phone']
            sec_phone=userDetails['sec_phone']
            emp_id=userDetails['emp_id']
            cur = mysql.connection.cursor()
            resultValue=cur.execute("select * from emp_person where (aadhar=%s or pri_phone=%s) and emp_id<>%s",(aadhar,pri_phone,emp_id))
            if resultValue==0:
                cur.execute("UPDATE emp_person SET aadhar=%s,first_name=%s,last_name=%s,doj=%s,job=%s,dob=%s,father=%s,salary=%s,layoff=%s,password=%s,state=%s,pri_phone=%s,sec_phone=%s where emp_id=%s",(aadhar,first_name,last_name,doj,job,dob,father,salary,layoff,password,state,pri_phone,sec_phone,emp_id))
                mysql.connection.commit()
                cur.close()
                flash("Updated successfully!!!")
                return redirect(url_for('emp_details'))
            else: 
                flash("Wrong Entry,Try Again!!!")
                return redirect(url_for('emp_details'))
    else:
        return redirect("http://localhost:5000/", code=302)
# search filter for employee 
@app.route('/search_emp',methods=['GET','POST'])
def search_emp():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            first_name=userDetails['first_name']
            cur=mysql.connection.cursor()
            resultValue=cur.execute("SELECT emp_id,aadhar, CONCAT(first_name,' ',last_name),DATE_FORMAT(doj, '%%d/%%m/%%Y'),job ,DATE_FORMAT(dob, '%%d/%%m/%%Y') ,father,salary ,DATE_FORMAT(layoff, '%%d/%%m/%%Y') ,password,state,pri_phone,sec_phone from emp_person where %s in (aadhar,first_name,last_name,doj,job ,dob ,father,salary ,layoff ,password,state,pri_phone,sec_phone);",[first_name])
            if resultValue>0:
                userDetails =cur.fetchall()
                flash("Data found!!!")
                return render_template('employee.html',userDetails=userDetails,user_image1=pic1)
            else:
                flash("No Data Found")
                return redirect(url_for('emp_details'))
    else:
        return redirect("http://localhost:5000/", code=302)

# ********************sales******************

@app.route('/sales_details',methods = ['GET', 'POST'])
def sales_details():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute(" select sales.sales_id,sales.order_id,DATE_FORMAT(sales.date, '%d/%m/%Y'),customer.buis_name,sales.trans_name,sales.vehicle_num,sales.bill,sales.status from sales,customer,orders where orders.customer_id=customer.customer_id and orders.order_id=sales.order_id order by sales.sales_id")
        userDetails =cur.fetchall()
        return render_template('sales.html',userDetails=userDetails,user_image1=pic1)
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/exist_sales',methods = ['GET', 'POST'])
def exist_sales():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            sales_id=userDetails['userInput']
            cur = mysql.connection.cursor()
            resultValue=cur.execute("select sales.sales_id,sales.order_id,sales.date,customer.buis_name,sales.trans_name,sales.vehicle_num,sales.bill,sales.status,DATE_FORMAT(sales.date, '%%d/%%m/%%Y') from sales,customer,orders where orders.customer_id=customer.customer_id and orders.order_id=sales.order_id and sales_id=%s",[sales_id])
            if resultValue>0:
                userDetails =cur.fetchall()
                flash("Click on update to update existing entry!!!")
                return render_template('updatesales.html',userDetails=userDetails,user_image1=pic1)
            else:
                flash("No Data Found!!!")
                return redirect(url_for('sales_details'))
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/upd_sales',methods = ['GET','POST'])
def upd_sales():
    if request.method == 'POST':
        userDetails=request.form
        # emp_id=userDetails['empid']
        sales_id=userDetails['sales_id']
        date=userDetails['date']
        trans_name=userDetails['trans_name']
        vehicle_num=userDetails['vehicle_no']
        bill=userDetails['bill']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE sales SET date=%s,trans_name=%s,vehicle_num=%s,bill=%s where sales_id=%s",(date,trans_name,vehicle_num,bill,sales_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('sales_details'))

@app.route('/search_sales',methods=['GET','POST'])
def search_sales():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            userInput=userDetails['userInput']
            cur=mysql.connection.cursor()
            resultValue=cur.execute("select sales.sales_id,sales.order_id,DATE_FORMAT(sales.date, '%%d/%%m/%%Y'),customer.buis_name,sales.trans_name,sales.vehicle_num,sales.bill,sales.status from sales,customer,orders where orders.customer_id=customer.customer_id and orders.order_id=sales.order_id and %s in (customer.buis_name,sales.trans_name,sales.vehicle_num) order by sales.sales_id  ",[userInput])
            if resultValue>0:
                userDetails =cur.fetchall()
                flash("Data found!!!")
                return render_template('sales.html',userDetails=userDetails,user_image1=pic1)
            else:
                flash("No Data Found!!!")
                return redirect(url_for('sales_details'))
    else:
        return redirect("http://localhost:5000/", code=302)

#*************************************orders*********************************************

@app.route('/order_details',methods = ['GET', 'POST'])
def order_details():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        cur = mysql.connection.cursor()
        cur2=mysql.connection.cursor()
        cur3=mysql.connection.cursor()
        cur.execute(" SELECT  orders.order_id,orders.customer_id,orders.advance,orders.status,DATE_FORMAT(orders.del_date, '%d/%m/%Y'),DATE_FORMAT(orders.place_date, '%d/%m/%Y'), GROUP_CONCAT(orders_norm.item_id SEPARATOR ', '),GROUP_CONCAT(orders_norm.quantity SEPARATOR ', '),customer.customer_id,customer.buis_name from  orders inner join orders_norm on orders.order_id=orders_norm.order_id inner join customer on customer.customer_id=orders.customer_id group by orders_norm.order_id")
        cur2.execute("SELECT customer_id,buis_name from customer")
        cur3.execute("SELECT item_id,description from items")
        userDetails = cur.fetchall()
        buisness=cur2.fetchall()
        items=cur3.fetchall()
        return render_template('order.html',userDetails=userDetails,user_image1=pic1,buisness=buisness,items=items)
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/new_order',methods = ['GET', 'POST'])
def new_orders():
    if request.method == 'POST':
        userDetails=request.form
        # order_id = userDetails['orderid']
        customer_id = userDetails['customer_id']
        advance = userDetails['Advance']
        # status = userDetails['Status']
        item_id = userDetails['Itemid']
        quantity=userDetails['Quantity']
        del_date=userDetails['ExpectedDeliveryDate']
        place_date=userDetails['PlacementDate']
        print(del_date)
        print(place_date)
        if place_date<=del_date:
            cur = mysql.connection.cursor()
            item_list=item_id.split(',')
            quantity_list=quantity.split(',')
            cur.execute("INSERT INTO orders(customer_id,advance,del_date,place_date) VALUES(%s, %s, %s, %s)",(customer_id,advance,del_date,place_date))
            mysql.connection.commit()
            cur3=mysql.connection.cursor()
            cur3.execute("SELECT max(order_id) from orders")
            resultValue=cur3.fetchall()
            size=resultValue[0][0]
            for i in range(len(item_list)):
                cur.execute("INSERT INTO orders_norm(order_id,item_id,quantity) VALUES (%s,%s, %s)",(size,item_list[i],quantity_list[i]))
            flash("New Data Entered!!!")
            mysql.connection.commit()
            cur.close()
                
            return redirect(url_for('order_details'))
        else:
            flash("placement date should be less than delivery date!!!")
            return redirect(url_for('order_details'))
  
    # return render_template('order.html')
@app.route('/exist_orders',methods = ['GET', 'POST'])
def exist_orders():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            userInput=userDetails['userInput']
            # print(type(order_id[0]))
            cur = mysql.connection.cursor()
            resultValue=cur.execute("SELECT  orders.order_id,orders.customer_id,orders.advance,orders.status,orders.del_date,orders.place_date, GROUP_CONCAT(orders_norm.item_id SEPARATOR ', '),GROUP_CONCAT(orders_norm.quantity SEPARATOR ', '),customer.customer_id,customer.buis_name,DATE_FORMAT(orders.del_date, '%%d/%%m/%%Y'),DATE_FORMAT(orders.place_date, '%%d/%%m/%%Y') from  orders inner join orders_norm on orders.order_id=orders_norm.order_id inner join customer on customer.customer_id=orders.customer_id group by orders_norm.order_id having  %s in (orders.order_id,customer.buis_name,orders.status)",[userInput])
            if resultValue>0:
                userDetails =cur.fetchall()
                cur2=mysql.connection.cursor()
                cur2.execute("SELECT customer_id,buis_name from customer ")
                buisness=cur2.fetchall()
                flash("Data found!!!")
                return render_template('updateorders.html',userDetails=userDetails,user_image1=pic1,buisness=buisness)
            else:
                flash("No Data Found!!!")
                return redirect(url_for('order_details'))
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/upd_orders',methods=['GET','POST'])
def upd_orders():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            order_id=userDetails['order_id']
            advance = userDetails['Advance']
            # status = userDetails['Status']
            item_id = userDetails['Itemid']
            quantity=userDetails['Quantity']
            del_date=userDetails['ExpectedDeliveryDate']
            # print(del_date)
            place_date=userDetails['PlacementDate']
            # del_dat = datetime.strptime(del_date, '%d/%m/%y')
            # place_dat = datetime.strptime(place_date, '%d/%m/%y')
            # print(del_date)
            cur = mysql.connection.cursor()
            item_list=item_id.split(',')
            quantity_list=quantity.split(',')
            cur.execute("UPDATE orders SET advance=%s,del_date=%s,place_date=%s where order_id=%s",(advance,del_date,place_date,order_id))
            cur.execute("DELETE from orders_norm where order_id=%s",[order_id])
            for i in range(len(item_list)):
                cur.execute("INSERT INTO orders_norm(order_id,item_id,quantity) VALUES (%s,%s, %s)",(order_id,item_list[i],quantity_list[i]))
            
            mysql.connection.commit()
            cur.close()
            flash("Updated successfully!!!")
            return redirect(url_for('order_details'))
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/new_sales',methods=['GET', 'POST'])
def new_sales():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            date=userDetails['date']
            trans_name=userDetails['trans_name']
            vehicle_num=userDetails['vehicle_num']
            bill=userDetails['bill']
            order_id=userDetails['order_id']
            status1="Paid"
            status="Sold"
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO sales(order_id,date,status,trans_name,vehicle_num,bill) VALUES (%s,%s,%s,%s,%s,%s)",(order_id,date,status1,trans_name,vehicle_num,bill))
            cur.execute("UPDATE orders SET status=%s where order_id=%s",(status,order_id))
            mysql.connection.commit()
            cur.close()
            flash("Sales updated successfully!!!")
            return redirect(url_for('order_details'))
    else:
        return redirect("http://localhost:5000/", code=302)

# @app.route('/search_sales',methods=['GET','POST'])
# def search_sales():
#     pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
#     if 'logged_in' in session:
#         if request.method == 'POST':
#             userDetails=request.form
#             first_name=userDetails['first_name']
#             cur=mysql.connection.cursor()
#             cur.execute("SELECT ")

# *********************************customer***************************************************
@app.route('/cus_details',methods = ['GET', 'POST'])
def cus_details():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT customer.customer_id,concat(customer.first_name,' ',customer.last_name),customer.buis_name,concat(customer.street_add,' ',customer.state,' ',customer.zip_code),customer.tin_no, GROUP_CONCAT(customer_norm.phone SEPARATOR ', ') from customer,customer_norm where customer.customer_id=customer_norm.customer_id group by customer.customer_id")
        userDetails =cur.fetchall()
        # flash("hello")
        return render_template('customer.html',userDetails=userDetails,user_image1=pic1)
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/search_cus/<userInput>',methods=['GET','POST'])
def searchcus(userInput):
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        # if request.method == 'POST':
            # userDetails=request.form
            # print(userInput)
            # userInput=userDetails['userInput']
            # print(userInput)
        cur = mysql.connection.cursor()
        resultValue=cur.execute("SELECT customer.customer_id,concat(customer.first_name,' ',customer.last_name),customer.buis_name,concat(customer.street_add,' ',customer.state,' ',customer.zip_code),customer.tin_no, GROUP_CONCAT(customer_norm.phone SEPARATOR ','),customer.first_name,customer.last_name,customer.state,customer.street_add,customer.zip_code from customer,customer_norm where customer.customer_id=customer_norm.customer_id and  %s in (customer.first_name,customer.buis_name,customer.customer_id,customer.tin_no) group by customer.customer_id ",[userInput])
        if resultValue>0:
            userDetails =cur.fetchall()
            flash("Data found!!!")
                # print(userDetails)
            return render_template('updatecus.html',userDetails=userDetails,user_image1=pic1)
        else:
            flash("No Data Found!!!")
                # print("helo")
            return redirect(url_for('cus_details'))

    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/search_cus',methods=['GET','POST'])
def search_cus():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            # print(userInput)
            userInput=userDetails['userInput']
            # print(userInput)
            cur = mysql.connection.cursor()
            resultValue=cur.execute("SELECT customer.customer_id,concat(customer.first_name,' ',customer.last_name),customer.buis_name,concat(customer.street_add,' ',customer.state,' ',customer.zip_code),customer.tin_no, GROUP_CONCAT(customer_norm.phone SEPARATOR ','),customer.first_name,customer.last_name,customer.state,customer.street_add,customer.zip_code from customer,customer_norm where customer.customer_id=customer_norm.customer_id and  %s in (customer.first_name,customer.buis_name,customer.customer_id,customer.tin_no) group by customer.customer_id ",[userInput])
            if resultValue>0:
                userDetails =cur.fetchall()
                flash("Data found!!!")
                # print(userDetails)
                return render_template('updatecus.html',userDetails=userDetails,user_image1=pic1)
            else:
                flash("No Data Found!!!")
                # print("helo")
                return redirect(url_for('cus_details'))

    else:
        return redirect("http://localhost:5000/", code=302)


@app.route('/new_customer',methods = ['GET', 'POST'])
def new_customer():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            # customerid = userDetails['customerid']
            buis_name=userDetails['buis_name']
            # size=userDetails['size']
            first_name = userDetails['first_name']
            last_name = userDetails['last_name']
            zip_code = userDetails['zip_code']
            state = userDetails['state']
            street_add=userDetails['street_add']
            tin_no=userDetails['tin_no']
            phone=userDetails['phone']
            cur = mysql.connection.cursor()
            phone_list=phone.split(',')
            cur.execute("INSERT INTO customer(first_name,last_name,zip_code,state,street_add,tin_no,buis_name) VALUES( %s, %s, %s, %s,%s,%s,%s)",(first_name,last_name,zip_code,state,street_add,tin_no,buis_name))
            mysql.connection.commit()
            cur3=mysql.connection.cursor()
            cur3.execute("SELECT max(customer_id) from customer")
            resultValue=cur3.fetchall()
            size=resultValue[0][0]
            for i in range(len(phone_list)):
                cur.execute("INSERT INTO customer_norm(customer_id,phone) VALUES (%s, %s)",(size,phone_list[i]))
            
            mysql.connection.commit()
            cur.close()
            flash("New Data Entered!!!")
            return redirect(url_for('cus_details'))
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/del_cus',methods=['GET','POST'])
def del_cus():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            customer_id = userDetails['customer_id']
            buis_name=userDetails['buis_name']
            cur = mysql.connection.cursor()
            resultValue=cur.execute("DELETE from customer where customer_id=%s and buis_name=%s",(customer_id,buis_name))
            if resultValue>0:
                flash("Deleted successfully!!!")
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('cus_details'))
            else: 
                flash("Wrong Entry!!!")
                return redirect(url_for('cus_details'))
            
    else:
        return redirect("http://localhost:5000/", code=302)
    
@app.route('/upd_cus',methods=['GET','POST'])
def upd_cus():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            customer_id=userDetails['customer_id']
            first_name = userDetails['first_name']
            last_name = userDetails['last_name']
            buis_name=userDetails['buis_name']
            tin_no=userDetails['tin_no']
            phone=userDetails['phone']
            zip_code = userDetails['zip_code']
            state = userDetails['state']
            street_add=userDetails['street_add']
            cur = mysql.connection.cursor()
            phone_list=phone.split(',')
            cur.execute("UPDATE customer SET first_name=%s,last_name=%s,buis_name=%s,tin_no=%s,zip_code=%s,state=%s,street_add=%s where customer_id=%s",(first_name,last_name,buis_name,tin_no,zip_code,state,street_add,customer_id))
            cur.execute("DELETE from customer_norm where customer_id=%s",[customer_id])
            for i in range(len(phone_list)):
                cur.execute("INSERT INTO customer_norm(customer_id,phone) VALUES (%s, %s)",(customer_id,phone_list[i]))
            
            mysql.connection.commit()
            cur.close()
            flash("Updated successfully!!!")
            return redirect(url_for('cus_details'))
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/items_details',methods = ['GET', 'POST'])
def items_details():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from items")
        userDetails =cur.fetchall()
        print(userDetails)
        return render_template('items.html',itemsDetails=userDetails,user_image1=pic1)
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/new_items',methods=['GET','POST'])
def new_items():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            item_id=userDetails['item_id']
            description=userDetails['description']
            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO items(item_id,description) VALUES(%s,%s)",(item_id,description))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('items_details'))
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/upd_items',methods=['GET','POST'])
def upd_items():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            print(userDetails)
            item_id=userDetails['item_id']
            description=userDetails['description']
            cur=mysql.connection.cursor()
            cur.execute("UPDATE items set description=%s where item_id=%s",(description,item_id))
            mysql.connection.commit()
            cur.close()
            flash("Updated successfully!!!")
            return redirect(url_for('items_details'))
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/search_items',methods=['GET','POST'])
def search_items():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            item_id=userDetails['item_id']
            cur=mysql.connection.cursor()
            cur.execute("SELECT * from items where item_id=%s",[item_id])
            userDetails =cur.fetchall()
            # flash("Updated successfully!!!")
            return render_template('upd_items.html',itemsDetails=userDetails,user_image1=pic1)
    else:
        return redirect("http://localhost:5000/", code=302)


@app.route('/att_details',methods = ['GET', 'POST'])
def att_details():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute(" select emp_person.first_name,attendance.emp_id,DATE_FORMAT(attendance.date, '%d/%m/%Y'),attendance.presence,DATE_FORMAT(attendance.date+1, '%Y-%m-%d') from emp_person,attendance where attendance.emp_id=emp_person.emp_id and date=(select max(date) from attendance)")
        userDetails =cur.fetchall()
    return render_template('man_attendance.html',attDetails=userDetails,user_image1=pic1)

@app.route('/search_att',methods=['GET','POST'])
def search_att():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            date=userDetails['date']
            # print(userInput)
            cur = mysql.connection.cursor()
            cur.execute("select emp_person.first_name,attendance.emp_id,DATE_FORMAT(attendance.date, '%%d/%%m/%%Y'),attendance.presence,DATE_FORMAT(attendance.date+1, '%%Y-%%m-%%d') from emp_person,attendance where attendance.emp_id=emp_person.emp_id and date=%s",[date])
            userDetails =cur.fetchall()
            print(userDetails)
            flash("Data Found!!!")
            return render_template('man_attendance.html',attDetails=userDetails,user_image1=pic1)
    else:
        return redirect("http://localhost:5000/", code=302)

# @app.route('/upd_att',methods=['GET','POST'])
# def upd_att():
    

@app.route('/payrolls_details',methods = ['GET', 'POST'])
def payrolls_details():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from employee")
    userDetails =cur.fetchall()
    return render_template('users.html',userDetails=userDetails)

@app.route('/pro_details',methods = ['GET', 'POST'])
def pro_details():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT DATE_FORMAT(date, '%d/%m/%Y'),GROUP_CONCAT(item_id SEPARATOR ', '),GROUP_CONCAT(quamtity SEPARATOR ', ') from production group by date ")
        userDetails =cur.fetchall()
        return render_template('production.html',userDetails=userDetails,user_image1=pic1)
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/new_production',methods = ['GET', 'POST'])
def new_production():
    if request.method == 'POST':
        userDetails=request.form
        date = userDetails['date']
        item_id = userDetails['item_id']
        quantity = userDetails['quantity']
        cur = mysql.connection.cursor()
        item_list=item_id.split(',')
        quantity_list=quantity.split(',')
        for i in range(len(item_list)):
            cur.execute("INSERT INTO production(date,item_id,quamtity) VALUES (%s,%s, %s)",(date,item_list[i],quantity_list[i]))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('pro_details'))


@app.route('/search_pro',methods=['GET','POST'])
def search_pro():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            first_name=userDetails['first_name']
            cur=mysql.connection.cursor()
            cur.execute("SELECT DATE_FORMAT(date, '%%d/%%m/%%Y'),GROUP_CONCAT(item_id SEPARATOR ', '),GROUP_CONCAT(quamtity SEPARATOR ', ') from production where date=%s",[first_name])
            userDetails =cur.fetchall()
            return render_template('updpro.html',userDetails=userDetails,user_image1=pic1,date=first_name)
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/upd_pro',methods=['GET','POST'])
def upd_pro():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.jpg')
    if 'logged_in' in session:
        if request.method == 'POST':
            userDetails=request.form
            date = userDetails['date']
            item_id = userDetails['item_id']
            quantity = userDetails['quantity']
            cur = mysql.connection.cursor()
            item_list=item_id.split(',')
            quantity_list=quantity.split(',')
            for i in range(len(item_list)):
                cur.execute("DELETE from production where date=%s",[date])
            for i in range(len(item_list)):
                    cur.execute("INSERT INTO production(date,item_id,quamtity) VALUES (%s,%s, %s)",(date,item_list[i],quantity_list[i]))
            mysql.connection.commit()
            cur.close()
            flash("Updated successfully!!!")
            return redirect(url_for('pro_details'))
    else:
        return redirect("http://localhost:5000/", code=302)

@app.route('/pur_details',methods = ['GET', 'POST'])
def pur_details():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from employee")
    userDetails =cur.fetchall()
    return render_template('users.html',userDetails=userDetails)

    
if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)