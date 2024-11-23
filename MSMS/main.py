from flask import Flask, render_template, request, session, redirect, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Make sure this is set for session management

# MySQL Database configuration
DB_CONFIG = {
    "host": "localhost",     # Update as needed
    "user": "root",          # Update with MySQL username
    "password": "qwertyuiopSQL@04",  # Update with MySQL password
    "database": "medical",   # Update with your database name
    "login_image": "4k.jpg"  # Login image filename
}

# Connect to the database
from mysql.connector import Error

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        return conn
    except Error as e:
        print(f"Database connection failed: {e}")
        return None
    
@app.route("/edit/<int:mid>", methods=['GET', 'POST'])
def edit(mid):
    # Check if the user is logged in
    if 'user' in session:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch the post data by mid
        cursor.execute("SELECT * FROM Posts WHERE mid = %s", (mid,))
        post = cursor.fetchone()

        if request.method == 'POST':
            # Retrieve form data
            medical_name = request.form['medical_name']
            owner_name = request.form['owner_name']
            phone_no = request.form['phone_no']
            address = request.form['address']

            # Update the post in the database
            cursor.execute("""
                UPDATE Posts SET medical_name = %s, owner_name = %s, phone_no = %s, address = %s WHERE mid = %s
            """, (medical_name, owner_name, phone_no, address, mid))
            conn.commit()
            conn.close()

            flash("Post updated successfully!", "success")
            return redirect('/index')

        return render_template('edit.html', post=post, params=DB_CONFIG)
    else:
        flash("Please log in first.", "warning")
        return redirect('/login')

@app.route("/delete/<string:mid>", methods=['GET', 'POST'])
def delete(mid):
    if 'user' in session:
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Delete the post from the database by mid (Post table)
            cursor.execute("DELETE FROM Posts WHERE mid = %s", (mid,))
            conn.commit()  # Commit the changes
            flash("Post deleted successfully!", "danger")
        except Exception as e:
            flash(f"Error deleting post: {str(e)}", "danger")
        finally:
            conn.close()

        return redirect('/index')  # Redirect to the index page after deletion
    else:
        flash("Please log in first.", "warning")
        return redirect('/login')


@app.route("/deletemp/<string:id>", methods=['GET', 'POST'])
def deletemp(id):
    if 'user' in session:
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Delete the record from the Medicines table by id
            cursor.execute("DELETE FROM Medicines WHERE id = %s", (id,))
            conn.commit()  # Commit the changes
            flash("Medicine deleted successfully!", "primary")
        except Exception as e:
            flash(f"Error deleting medicine: {str(e)}", "danger")
        finally:
            conn.close()

        return redirect('/list')  # Redirect to the list page after deletion
    else:
        flash("Please log in first.", "warning")
        return redirect('/login')



@app.route("/")
def hello():
    return render_template('login.html', params=DB_CONFIG)


@app.route("/index")
def home():
    if 'user' in session:
        # Database connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch all medical records from the relevant table (adjust table name if needed)
        cursor.execute("SELECT * FROM Posts")  # Ensure you're querying the correct table (Posts or another)
        posts = cursor.fetchall()  # Get all the records
        
        conn.close()

        # Pass the fetched data to the dashboard template
        return render_template('dashbord.html', params=DB_CONFIG, posts=posts)
    else:
        flash("Please log in first", "warning")
        return redirect('/login')


@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        name = request.form.get('search')  # The search term (medicine or product)

        # Validate if the search term is provided
        if not name:
            flash("Please enter a search term.", "danger")
            return redirect('/search')

        # Search for the medicine in the Addmp table
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM Addmp WHERE medicine = %s", (name,))
            post = cursor.fetchone()

            # Search for the product in the Addpd table
            cursor.execute("SELECT * FROM Addpd WHERE product = %s", (name,))
            pro = cursor.fetchone()

            if not post and not pro:
                flash("Item is not available.", "danger")
            else:
                flash("Item is available.", "primary")

        finally:
            conn.close()

    return render_template('search.html', params=DB_CONFIG)



@app.route("/details", methods=['GET', 'POST'])
def details():
    if 'user' in session:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Logs")
        posts = cursor.fetchall()
        conn.close()
        return render_template('details.html', params=DB_CONFIG, posts=posts)
    else:
        flash("Please log in to access this page", "warning")
        return redirect('/login')


@app.route("/insert", methods=['GET', 'POST'])
def insert():
    if request.method == 'POST':
        mid = request.form.get('mid')
        medical_name = request.form.get('medical_name')
        owner_name = request.form.get('owner_name')
        phone_no = request.form.get('phone_no')
        address = request.form.get('address')

        # Validate if the mid exists in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Posts WHERE mid = %s", (mid,))
        existing_medical = cursor.fetchone()
        conn.close()

        if existing_medical:
            flash("Medical ID already exists, cannot insert.", "danger")
            return redirect('/insert')  # Optionally, return to the insert page

        # Proceed with the insertion if mid is valid
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Posts (mid, medical_name, owner_name, phone_no, address) VALUES (%s, %s, %s, %s, %s)",
            (mid, medical_name, owner_name, phone_no, address)
        )
        conn.commit()
        conn.close()
        flash("Thanks for submitting your details", "success")

    return render_template('insert.html', params=DB_CONFIG)


@app.route("/addmp", methods=['GET', 'POST'])
def addmp():
    if request.method == 'POST':
        newmedicine = request.form.get('medicine')
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Insert the new medicine into the addmp table
            cursor.execute("INSERT INTO addmp (medicine) VALUES (%s)", (newmedicine,))
            conn.commit()  # Commit the transaction
            flash("Thanks for adding new medicine", "primary")  # Success message
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")  # Handle any errors
        finally:
            conn.close()  # Close the connection
    return render_template('search.html', params=DB_CONFIG)  # Render the search page again

@app.route("/addpd", methods=['GET', 'POST'])
def addpd():
    if request.method == 'POST':
        new_product = request.form.get('product')  # Get the product from the form
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Insert the new product into the addpd table
            cursor.execute("INSERT INTO addpd (product) VALUES (%s)", (new_product,))
            conn.commit()  # Commit the transaction
            flash("Thanks for adding new product", "primary")  # Success message
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")  # Handle any errors
        finally:
            conn.close()  # Close the connection
    return render_template('search.html', params=DB_CONFIG)  # Render the search page again



@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'user' in session:
        # If the user is already logged in, just redirect them to the home/dashboard page
        return redirect('/index')

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('password')

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed. Please try again later.", "danger")
            return render_template('login.html', params=DB_CONFIG)

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (username, userpass))
        user = cursor.fetchone()
        conn.close()

        if user:
            if user['role'] in ['authority', 'medical_owner']:
                # Set session variables
                session['user'] = username
                session['role'] = user['role']
                flash(f"Welcome, {user['role']}!", "primary")
                return redirect('/index')  # Redirect to home page after login
            else:
                flash("Wrong role", "danger")  # If role is not valid
        else:
            flash("Incorrect username or password", "danger")

    return render_template('login.html', params=DB_CONFIG)



@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('password')
        role = request.form.get('role')  # Role selection from the signup form

        # Ensure only valid roles are accepted
        if role not in ['authority', 'medical_owner']:
            flash("Invalid role selected", "danger")
            return render_template('signup.html', params=DB_CONFIG)

        # Establish database connection
        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed. Please try again later.", "danger")
            return render_template('signup.html', params=DB_CONFIG)

        cursor = conn.cursor()

        # Insert new user into Users table with the role
        try:
            cursor.execute("INSERT INTO Users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
            conn.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect('/login')
        except Error as e:
            flash("An error occurred. Please try again.", "danger")
        finally:
            conn.close()

    return render_template('signup.html', params=DB_CONFIG)



@app.route("/list", methods=['GET', 'POST'])
def post():
    # Check if the user is logged in
    if 'user' in session:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch all medicines from the database
        cursor.execute("SELECT * FROM Medicines")
        posts = cursor.fetchall()
        conn.close()

        return render_template('post.html', params=DB_CONFIG, posts=posts)
    else:
        flash("Please log in to access this page", "warning")
        return redirect('/login')

@app.route("/medicines", methods=['GET', 'POST'])
def medicine():
    if request.method == 'POST':
        mid = request.form.get('mid')
        name = request.form.get('name')
        medicines = request.form.get('medicines')  # Expecting a comma-separated list
        products = request.form.get('products')  # Expecting a comma-separated list
        email = request.form.get('email')
        amount = request.form.get('amount')

        # Check if the products and medicines fields are not empty
        if not medicines and not products:
            flash("Please select at least one medicine or product", "danger")
            return redirect('/medicines')  # Redirect back to the medicines page

        # Process and handle multiple products and medicines
        medicines_list = medicines.split(',') if medicines else []
        products_list = products.split(',') if products else []

        # Trim spaces from each item in the lists
        medicines_list = [med.strip() for med in medicines_list]
        products_list = [prod.strip() for prod in products_list]

        # If both lists are empty, show an error
        if not medicines_list and not products_list:
            flash("Please provide either medicines or products.", "danger")
            return redirect('/medicines')

        # Establish a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # First, check if all medicines exist in the database
            for med in medicines_list:
                cursor.execute("SELECT * FROM Addmp WHERE medicine = %s", (med,))
                if cursor.fetchone() is None:
                    flash(f"Medicine '{med}' is not available.", "danger")
                    return redirect('/medicines')  # Stop processing if any medicine is unavailable

            # Check if all products exist in the database
            for prod in products_list:
                cursor.execute("SELECT * FROM Addpd WHERE product = %s", (prod,))
                if cursor.fetchone() is None:
                    flash(f"Product '{prod}' is not available.", "danger")
                    return redirect('/medicines')  # Stop processing if any product is unavailable

            # Proceed with inserting the order only if all items are valid
            cursor.callproc('proc_MedicineOrderInsert', (mid, name, medicines, products, email, amount))
            conn.commit()  # Commit the transaction

            flash("Order placed successfully", "primary")

        except mysql.connector.Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            conn.close()

    return render_template('medicine.html', params=DB_CONFIG)


@app.route("/logout")
def logout():
    session.pop('user', None)
    flash("You are logged out", "primary")
    return redirect('/login')


@app.route("/aboutus")
def aboutus():
    return render_template('aboutus.html', params=DB_CONFIG)

@app.route("/sp")
def store():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Calling the stored procedure
        cursor.callproc('proc_MedicalSupplyRetrieve')

        # Fetch the results of the stored procedure
        # Assuming the stored procedure is returning multiple result sets, you can fetch them like this:
        for result in cursor.stored_results():
            posts = result.fetchall()

        # If you have multiple result sets, fetch them like so:
        # cursor.nextset() for the next result set

        if not posts:
            posts = []

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        posts = []
    
    finally:
        conn.close()

    # Debugging line to check if the data is being passed
    print(posts)

    # Assuming params holds site-wide parameters like your header info
    params = {
        'blog_name': 'Medical Supply Blog',
        'tw_url': 'https://twitter.com/medsupply',
        'fb_url': 'https://facebook.com/medsupply',
        'gh_url': 'https://github.com/medsupply'
    }

    # Return the rendered template with the data passed to it
    return render_template('store.html', posts=posts, params=params)


@app.route("/items")
def items():
    # Fetch available medicines from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM Addmp")  # Query for medicines
    posts = cursor.fetchall()  # Get all medicines
    conn.close()

    return render_template('items.html', posts=posts, params=DB_CONFIG)

@app.route("/items2")
def items2():
    # Fetch available products from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM Addpd")  # Query for products
    posts = cursor.fetchall()  # Get all products
    conn.close()

    return render_template('items2.html', posts=posts, params=DB_CONFIG)

@app.route("/all_products", methods=['GET'])
def all_products():
    if 'user' in session:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Execute the query to get all products and total count
            cursor.execute("""
                SELECT 'Medicine' AS type, medicine AS name FROM Addmp
                UNION
                SELECT 'Product' AS type, product AS name FROM Addpd;
            """)
            products = cursor.fetchall()

            cursor.execute("""
                SELECT COUNT(*) AS total_products
                FROM (
                    SELECT 'Medicine' AS type, medicine AS name FROM Addmp
                    UNION
                    SELECT 'Product' AS type, product AS name FROM Addpd
                ) AS all_products;
            """)
            total_products = cursor.fetchone()['total_products']

            if not products:
                flash("No products available.", "danger")
            else:
                flash("Products fetched successfully.", "primary")

        except mysql.connector.Error as e:
            flash(f"Error fetching products: {str(e)}", "danger")
            products = []
            total_products = 0
        finally:
            conn.close()

        # Render the page and pass the data to the template
        return render_template('all_products.html', products=products, total_products=total_products, params=DB_CONFIG)
    else:
        flash("Please log in to access this page", "warning")
        return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)
