import sqlite3

from flask import Flask, request, render_template, session, url_for, redirect

app: Flask = Flask(__name__, static_url_path='/static')
app.secret_key = "FelixPham"

#Mặc định gọi form search
@app.route('/')
def index():
    # Check if 'username' key exists in the session
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    return render_template(
        'SearchWithCSSDataDBAddToCartTable.html',
        search_text="",
        user_name = current_username)

#Đối với phương thức Search
@app.route('/searchData', methods=['POST'])
def searchData():
    #Get data from Request
    # Check if 'username' key exists in the session
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    search_text = request.form['searchInput']
    #Thay bang ham load du lieu tu DB
    product_table = load_data_from_db(search_text)
    print(product_table)
    return render_template(
        'SearchWithCSSDataDBAddToCartTable.html',
                           search_text=search_text,
                           products=product_table,
                           user_name=current_username
                           )

#Load dữ liệu và lọc ra bản ghi phù hợp
def load_data(search_text):
    import pandas as pd
    df = pd.read_csv('gradedata.csv')
    dfX = df
    if search_text != "":
        dfX = df[(df["fname"] == search_text) |
                 (df["lname"] == search_text)]
        print(dfX)
    html_table = dfX.to_html(classes='data',
                             escape=False)
    return html_table

def load_data_from_db(search_text):
        sqldbname = 'db/website.db'
        if search_text != "":
            # Khai bao bien de tro toi db
            conn = sqlite3.connect(sqldbname)
            cursor = conn.cursor()
            sqlcommand = ("Select * from storages "
                          "where model like '%")+search_text+ "%'"
            cursor.execute(sqlcommand)
            data = cursor.fetchall()
            conn.close()
            return data

    # Đối với phương thức Search
@app.route('/search', methods=['POST'])
def search():
    # Get data from Request
    search_text = request.form['searchInput']
    return render_template('SearchWithCSSDataDBAddToCartTable.html',
                           search_text=search_text)

@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    #1. Declare Database to get price
    sqldbname = 'db/website.db'
    #2. Get the product id and quantity from the form
    product_id = request.form["product_id"]
    quantity = int(request.form["quantity"])

    #3. get the product name and price from the database
    # or change the structure of shopping cart
    connection = sqlite3.connect(sqldbname)
    cursor = connection.cursor()
    cursor.execute("SELECT model, price, picture, details "
                   "FROM storages WHERE id = ?",
                   product_id)
    #3.1. get one product
    product = cursor.fetchone()
    connection.close()

    #4. create a dictionary for the product
    product_dict = {
        "id": product_id,
        "name": product[0],
        "price": product[1],
        "quantity": quantity,
        "picture": product[2],
        "details": product[3]
    }
    #5. get the cart from the session or create an empty list
    cart = session.get("cart", [])

    #6. check if the product is already in the cart
    found = False
    for item in cart:
        if item["id"] == product_id:
            #6.1 update the quantity of the existing product
            item["quantity"] += quantity
            found = True
            break

    if not found:
        #6.2 add the new product to the cart
        cart.append(product_dict)
    #7. save the cart back to the session
    session["cart"] = cart

    #8. Print out
    rows = len(cart)
    outputmessage = (f'"Product added to cart successfully!"'
                     f"</br>Current: "+str(rows) + " products"
                     f'</br>Continue Search! <a href="/">Search Page</a>'
                     f'</br>View Shopping Cart! <a href="/view_cart">ViewCart</a>')
    # return a success message

    return outputmessage

@app.route("/view_cart")
def view_cart():
    # get the cart from the session or create an empty list
    # render the cart.html template and pass the cart
    current_cart = []
    if 'cart' in session:
        current_cart = session.get("cart", [])
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    return render_template(
        "cart_update.html",
        carts=current_cart,
        user_name=current_username
    )

@app.route('/update_cart', methods=['POST'])
def update_cart():
    # 1. Get the shopping cart from the session
    cart = session.get('cart', [])
    # 2. Create a new cart to store updated items
    new_cart = []
    # 3. Iterate over each item in the cart
    for product in cart:
        product_id = str(product['id'])
        # 3.1 If this product has a new quantity in the form data
        if f'quantity-{product_id}' in request.form:
            quantity = int(request.form[f'quantity-{product_id}'])
            # If the quantity is 0 or this is a delete field, skip this product
            if quantity == 0 or f'delete-{product_id}' in request.form:
                continue
            # Otherwise, update the quantity of the product
            product['quantity'] = quantity
        # 3.2 Add the product to the new cart
        new_cart.append(product)
    # 4. Save the updated cart back to the session
    session['cart'] = new_cart
    # 5.Redirect to the shopping cart page (or wherever you want)
    return redirect(url_for('view_cart'))


@app.route('/update_cart_v2', methods=['POST'])
def update_cart_v2():
    # Get the shopping cart from the session
    cart = session.get('cart', {})
    # Iterate over each item in the POST data
    for key in request.form:
        # If this is a quantity field
        if key.startswith('quantity-'):
            product_id = key.split('-')[1]
            quantity = int(request.form[key])
            # If the quantity is 0 or this is a delete field, remove the product
            if quantity == 0 or f'delete-{product_id}' in request.form:
                cart.pop(int(product_id))
            else:
                # Otherwise, update the quantity of the product
                if product_id in cart:
                    cart[int(product_id)]['quantity'] = quantity

    # Save the updated cart back to the session
    session['cart'] = cart

    # Redirect to the shopping cart page (or wherever you want)

    return redirect(url_for('view_cart'))



@app.route('/update_cart_v1', methods=['POST'])
def update_cart_v1():
    # 1. Get the shopping cart from the session
    cart = session.get('cart', [])
    # 2. Create a new cart to store updated items
    new_cart = []
    # 3. Iterate over each item in the cart
    for product in cart:
        product_id = str(product['id'])
        # 3.1 If this product has a new quantity in the form data
        if f'quantity-{product_id}' in request.form:
            quantity = int(request.form[f'quantity-{product_id}'])
            # If the quantity is 0 or this is a delete field, skip this product
            if quantity == 0 or f'delete-{product_id}' in request.form:
                continue
            # Otherwise, update the quantity of the product
            product['quantity'] = quantity
        # 3.2 Add the product to the new cart
        new_cart.append(product)
    # 4. Save the updated cart back to the session
    session['cart'] = new_cart
    # 5.Redirect to the shopping cart page (or wherever you want)
    return redirect(url_for('view_cart'))


@app.route('/proceed_cart', methods=['POST'])
def proceed_cart():
    # 1. Retrieve the user ID from the session:
    if 'current_user' in session:
        user_id = session['current_user']['id']
        user_email = session['current_user']['email']
    else:
        user_id = 0
        user_email = "";
    # 2. Get the shopping cart from the session
    current_cart = []
    if 'cart' in session:
        shopping_cart  = session.get("cart", [])
    # 3.: Save Order Information to the "order" Table
    # Establish a database connection
    sqldbname = 'db/website.db'
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    # Define the order information (Create a new form)
    user_address = "User Address"  # Replace this with the actual address from the session
    user_mobile = "User Mobile"  # Replace this with the actual mobile number from the session
    purchase_date = "2023-10-10"  # Replace this with the actual purchase date
    ship_date = "2023-10-15"  # Replace this with the actual ship date
    status = 1  # Replace this with the actual status (e.g., processing, shipped, etc.)
    # Insert the order into the "order" table
    cursor.execute('''
        INSERT INTO "order" (user_id, user_email, user_address, 
        user_mobile, purchase_date, ship_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, user_email, user_address,
          user_mobile, purchase_date, ship_date, status))
    # 4. Get the ID of the inserted order
    order_id = cursor.lastrowid
    print(order_id)
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    #5: Save Order Details to the "order_details" Table
    # Establish a new database connection (or reuse the existing connection)
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    # Insert order details into the "order_details" table
    for product in shopping_cart:
        product_id = product['id']
        price = product['price']
        quantity = product['quantity']
        cursor.execute('''
            INSERT INTO order_details (order_id, product_id, price, quantity)
            VALUES (?, ?, ?, ?)
        ''', (order_id, product_id, price, quantity))
    # 6. Commit the changes and close the connection
    conn.commit()
    conn.close()
    # 7. To remove the current_cart from the session
    if 'cart' in session:
        current_cart = session.pop("cart", [])
    else:
        print("No current_cart in session.")
    #Call to orders/order_id
    order_url = url_for('orders', order_id=order_id, _external=True)
    return f'Redirecting to order page: <a href="{order_url}">{order_url}</a>'

@app.route('/orders/', defaults={'order_id': None}, methods=['GET'])
@app.route('/orders/<int:order_id>/', methods=['GET'])
def orders(order_id):
    sqldbname = 'db/website.db'
    #if 'current_user' in session:
    #    user_id = session['current_user']['id']
    user_id = session.get('current_user', {}).get('id')
    if user_id:
        conn = sqlite3.connect(sqldbname)
        cursor = conn.cursor()
        if order_id is not None:
            cursor.execute('SELECT * FROM "order" WHERE id = ? AND user_id = ?', (order_id, user_id))
            order = cursor.fetchone()
            cursor.execute('SELECT * FROM order_details WHERE order_id = ?', (order_id,))
            order_details = cursor.fetchall()
            conn.close()
            return render_template('order_details.html', order=order, order_details=order_details)
        else:
            cursor.execute('SELECT * FROM "order" WHERE user_id = ?', (user_id,))
            user_orders = cursor.fetchall()
            conn.close()
            return render_template('orders.html', orders=user_orders)
    return "User not logged in."


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Khi nhận dữ liệu từ hành vi post, sau khi nhận dữ liệu
    # từ session sẽ gọi định tuyến sang trang index
    if request.method == 'POST':
        username = request.form['txt_username']
        password = request.form['txt_password']
        # Store 'username' in the session
        obj_user = get_obj_user(username,password)
        if obj_user is not None:
            obj_user = {
                "id" :obj_user[0],
                "name" : obj_user[1],
                "email": obj_user[2]
            }
            session['current_user'] = obj_user
        return redirect(url_for('index'))
    # Trường hợp mặc định là vào trang login
    return render_template('login.html')


def check_exists(username, password):
    result = False;
    sqldbname = 'db/website.db'
    # Khai bao bien de tro toi db
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    # sqlcommand = "Select * from storages where "
    sqlcommand = "Select * from user where name = '"+username+"' and password = '"+password+"'"
    cursor.execute(sqlcommand)
    data = cursor.fetchall()
    print(type(data))
    if len(data)>0:
        result = True
    conn.close()
    return result;

def get_obj_user(username, password):
    result = None;
    sqldbname = 'db/website.db'
    # Khai bao bien de tro toi db
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    # sqlcommand = "Select * from storages where "
    sqlcommand = "Select * from user where name =? and password = ?"
    cursor.execute(sqlcommand,(username,password))
    # return object
    obj_user = cursor.fetchone()
    if obj_user is not None:
        result = obj_user
    conn.close()
    return result;

@app.route('/logout')
def logout():
    session.pop('username', None)
    # Remove 'username' from the session
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)


