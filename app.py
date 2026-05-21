from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import timedelta

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=1)

import os
app.secret_key = os.environ.get("SECRET_KEY", "fallback-dev-key")

def get_db():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", ""),
        user=os.environ.get("DB_USER", ""),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", ""),
        port=int(os.environ.get("DB_PORT", 3306)),
        ssl_ca=False,
        ssl_verify_cert=False,
        ssl_verify_identity=False,
        connection_timeout=30
    )

@app.route('/', methods=['GET','POST'])
def signup():
    if "account_id" in session:
        return redirect('/dashboard')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        db = get_db()

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "select * from customers where email = %s",(email,)
        )
        check = cursor.fetchone()
        if check:
            db.close()
            return render_template('signup.html',error = "Email allready Exist")


        cursor.execute(
            'select * from customers where name = %s',(name,)
        )
        n_check = cursor.fetchone()
        if n_check:
            db.close()
            return render_template('signup.html',n_error = "username allready exist!")

        
        cursor = db.cursor()
        #INSERTING THE USER DATA SIGNUP DATA TO THE CUSTOMERS DB
        try:
            cursor.execute(
                "insert into customers (name,email,password) values (%s,%s,%s)",(name,email,password)
            )
            customer_id = cursor.lastrowid

            cursor.execute(
                "insert into accounts (customer_id) values (%s)",(customer_id,)
            )
            db.commit()

        except Exception as e:
            db.rollback()
            print(f"DB Error: {e}")

        db.close()
        return redirect("/login")
    
    return render_template("signup.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if "account_id" in session:
        return redirect('/dashboard')
    if request.method == 'POST':
        email = request.form['email']
        pas = request.form['password']

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "select * from customers where email = %s",(email,)
        )

        user = cursor.fetchone()

        if not user:
            db.close()
            return render_template('login.html',error = "Create an Account")
        
        if user and check_password_hash(user["password"], pas): # type: ignore
            cursor.execute(
                "select account_id from accounts where customer_id = %s",
                (user["customer_id"],) # type: ignore
            )
            account = cursor.fetchone()

            session.permanent = True
            session["account_id"] = account["account_id"] # type: ignore
            db.close()
            return redirect("/dashboard")
        db.close()
        return render_template('login.html', error2 = "Ivalid Email/Password")
    
    return render_template('login.html')

@app.route('/dashboard',methods=['GET'])
def dash():
    if "account_id" not in session:
        return redirect("/login")
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        'select name from customers c join accounts a on c.customer_id = a.customer_id where account_id = %s ',(session['account_id'],)
    )
    user = cursor.fetchone()
    db.close()
    if not user:
        return redirect("/login")
    return render_template('dashboard.html',msg = user['name'])

@app.route('/addbal',methods=['GET','POST'])
def addbal():

    if "account_id" not in session:
        return redirect("/login")

    if request.method == 'POST':
        money = request.form['money']
        acc_id = session['account_id']

        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                'update accounts set balance = balance+%s where account_id = %s',(money,acc_id)
            )

            cursor.execute(
                "select balance from accounts where account_id = %s",(acc_id,)
            )
            bal = cursor.fetchone()

            cursor.execute(
                "insert into transactions (from_acc, to_acc, amount, status, remaining_balance) values (%s, %s, %s, %s, %s)",(acc_id, acc_id, money, "DEPOSIT", bal['balance']) # type: ignore

            )

            db.commit()
        except Exception as e:
            db.rollback()
            print(f"DB Error: {e}")

        db.close()
        return render_template('addbal.html',state = "Money Deposited Successfully")
    
    return render_template('addbal.html')

@app.route('/pay',methods=['GET','POST'])
def pay():

    if "account_id" not in session:
        return redirect("/login")

    if request.method == 'POST':
        name = request.form['name']
        money = float(request.form['money'])
        acc_id = session['account_id']

        db = get_db()
        cursor = db.cursor(dictionary=True, buffered=True)
        cursor.execute(
            'select account_id from accounts a join customers c on a.customer_id = c.customer_id where c.name = %s',(name,)
        )
        receiver = cursor.fetchone()

        if not receiver:
            db.close()
            return render_template('pay.html', user_error="Username not found!")
        
        if receiver['account_id'] == acc_id: # type: ignore
            db.close()
            return render_template('pay.html',selfpay_error='You cannot send money to yourself!')

        if money <= 0 :
            db.close()
            return render_template('pay.html',money_error='Enter A Valid Amount')
        
        cursor.execute(
            'select balance from accounts where account_id = %s',(acc_id,)
        )
        valid = cursor.fetchone()

        if valid["balance"] < money: # type: ignore
            db.close()
            return render_template('pay.html', bal_error="Insufficient balance!")
        
        try:
            cursor.execute(
                'update accounts set balance = balance - %s where account_id = %s',(money,acc_id)
            )
            
            cursor.execute(
                'update accounts set balance = balance + %s where account_id = %s',(money,receiver['account_id']) # type: ignore
            )

            #TO SHOW REMAINING BALANCE
            cursor.execute(
                'select balance from accounts where account_id = %s',(acc_id,)
            )
            bal = cursor.fetchone()

            cursor.execute(
                "insert into transactions (from_acc, to_acc, amount, status, remaining_balance) values (%s, %s, %s, %s, %s)",(acc_id, receiver['account_id'], money, "SUCCESS", bal['balance']) # type: ignore

            )
            db.commit()
            
        except Exception as e:
            db.rollback()
            print(f"DB Error: {e}")

        msg = f"₹{money} successfully transferred to {name}"
        db.close()
        return render_template('pay.html',state = msg) 
        
    return render_template('pay.html')

@app.route('/history')
def history():

    if "account_id" not in session:
        return redirect("/login")

    acc_id = session['account_id']
    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    cursor.execute(
        'select * from transactions where from_acc = %s or to_acc = %s order by created_at desc',(acc_id, acc_id)
    )

    history = cursor.fetchall()
    db.commit()
    db.close()
    return render_template('history.html',hist=history)

@app.route('/viewbal')
def viewbal():

    if "account_id" not in session:
        return redirect("/login")
    
    acc_id = session['account_id']

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        'select balance from accounts where account_id = %s',(acc_id,)
    )

    bal = cursor.fetchone()
    db.close()
    if not bal:
        return redirect("/dashboard")
    msg = f"YOUR CURRENT BALANCE ₹{bal['balance']}"
    return render_template('viewbal.html', accc_id=acc_id, bal=msg)


@app.route('/logout')
def logout():
    session.pop("account_id",None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")
