from flask import Flask, render_template, request, redirect, url_for, session,jsonify,flash
from flask_mail import Mail, Message
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from werkzeug.utils import secure_filename
import time
from datetime import datetime
app = Flask(__name__)
CORS(app)


# Flask-Mail Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your_email_password'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)

app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Abhirup12345@localhost/assignments'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User model
class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    college = db.Column(db.String(100), nullable=False)  
    
class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    college_name = db.Column(db.String(255), nullable=False)
    words = db.Column(db.Integer, nullable=False)
    assignmentType=db.Column(db.String(255), nullable=False)
    urgency=db.Column(db.String(255), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_data = db.Column(db.LargeBinary, nullable=False)
    payment_status = db.Column(db.String(50), default="pending")  # New Field
    payment_method = db.Column(db.String(50), nullable=True)  # New Field
    transaction_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='Pending') # Default to 'Pending'
    orderstatus = db.Column(db.String(20), default='Pending')
    price=db.Column(db.Integer,nullable=False)
    placed_date = db.Column(db.DateTime, nullable=False)
    confirmed_date = db.Column(db.DateTime, nullable=True)
    delivered_date = db.Column(db.DateTime, nullable=True)
    def __repr__(self):
        return f'<Order {self.id}>'    


@app.route('/')
def home():
    # Check if the user is logged in
    if 'user' in session:
        return redirect(url_for('dashboard'))  # Redirect to the dashboard if logged in
    return render_template('index.html') 

@app.route('/sample')
def sample():
    return render_template('sample.html') 
@app.route('/pricing', methods=['GET', 'POST'])
def pricing():
    error = request.args.get('error')
    return render_template('pricing.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = users.query.filter_by(email=email).first()

        if user:
            if bcrypt.check_password_hash(user.password, password):
                session['user'] = user.email
                session['user_id'] = user.id
                session['user_name'] = user.name  # Store name for personalized greetings
                return redirect(url_for('dashboard'))
            else:
                error = "Incorrect password. Please try again."
        else:
            error = "User not found. Please sign up first."
        
        return render_template('login.html', error=error)

    # Handle GET request
    return render_template('login.html')



@app.route('/check-login')
def check_login():
    return jsonify({"isLoggedIn": 'user' in session})

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect if not logged in

    user_id = session.get('user_id')  # Fetch user ID from session
    if user_id:
        # Fetch user from the database by their ID
        user = users.query.get(user_id)
        if user:
            # Pass the user's name to the template
            return render_template('dashboard.html', user_name=user.name)

    # If user_id is not in the session or user is not found
    error_message = "User not found. Please log in again."
    return redirect(url_for('login', error=error_message))



@app.route('/my-orders')
def my_orders():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Retrieve orders for the logged-in user
    user_orders = Orders.query.filter_by(email=session['user']).all()
    
    return render_template('my_orders.html', orders=user_orders)


@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    name = request.form.get('name')
    college = request.form.get('college')

    print(f"Received College: {college}")  # Debugging line

    if not college:
        return "College field is required", 400

    if password != confirm_password:
        return "Passwords do not match", 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = users(email=email, password=hashed_password, name=name, college=college)

    try:
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    except Exception as e:
        db.session.rollback()
        return str(e), 500


@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    return redirect(url_for('login'))

@app.route('/contact')
def contact():
    return render_template('contact.html')



@app.route('/update-status', methods=['POST'])
def update_status():
    try:
        # Parse request JSON or form data
        if request.is_json:
            data = request.get_json()
            order_id = data.get('orderId')  # Use 'orderId' to match the frontend
            new_status = data.get('status')
        else:
            order_id = request.form.get('orderId')  # Use 'orderId' to match the frontend
            new_status = request.form.get('status')

        print(f"Received Order ID: {order_id}, New Status: {new_status}")  # Debugging log

        # Validate input
        if not order_id or not new_status:
            print("Error: Missing parameters")  # Debugging log
            return jsonify({"error": "Missing required parameters"}), 400

        # Fetch the order by ID
        order = Orders.query.get(order_id)  # Primary key lookup
        if not order:
            print("Error: Order not found")  # Debugging log
            return render_template('success.html')
        # Update the order status
        order.status = new_status

        # If the status is "delivered", set the delivered_date to the current timestamp
        if new_status.lower() == "delivered":
            order.delivered_date = datetime.now()  # Set to current timestamp

        db.session.commit()
        print("Status updated successfully")  # Debugging log
        return render_template('success.html')

    except Exception as e:
        print("Error during update:", str(e))  # Debugging log
        return jsonify({"error": str(e)}), 500




@app.route('/update-orderstatus', methods=['POST'])
def update_orderstatus():
    try:
        # Parse request JSON or form data
        if request.is_json:
            data = request.get_json()
            order_id = data.get('orderId')  # Use 'orderId' to match the frontend
            new_status = data.get('orderstatus')
            new_price = data.get('price')
        else:
            order_id = request.form.get('orderId')  # Use 'orderId' to match the frontend
            new_status = request.form.get('orderstatus')
            new_price = request.form.get('price')

        print(f"Received Order ID: {order_id}, New Status: {new_status}, New Price: {new_price}")  # Debugging log

        # Validate input
        if not order_id or not new_status:
            print("Error: Missing parameters")  # Debugging log
            return jsonify({"error": "Missing required parameters"}), 400

        # Fetch the order by ID
        order = Orders.query.get(order_id)  # Primary key lookup
        if not order:
            print("Error: Order not found")  # Debugging log
            return jsonify({"error": "Order not found"}), 404

        # Update the order status and price
        order.orderstatus = new_status
        order.price = new_price

        # If the status is "confirmed", set the confirmed_date to the current timestamp
        if new_status.lower() == "accepted":
            order.confirmed_date = datetime.now()  # Set to current timestamp

        # If the status is "delivered", set the delivered_date to the current timestamp
        if new_status.lower() == "delivered":
            order.delivered_date = datetime.now()  # Set to current timestamp

        db.session.commit()
        print("Status and price updated successfully")  # Debugging log
        return render_template('orderstatus.html')

    except Exception as e:
        print("Error during update:", str(e))  # Debugging log
        return jsonify({"error": str(e)}), 500

# Order summary endpoint
@app.route('/order', methods=['GET', 'POST'])
def order():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Extract query parameters
    data = {
        "college": request.args.get("college"),
        "type": request.args.get("type"),
        "urgency": request.args.get("urgency"),
        "length": request.args.get("length"),
        "pages": request.args.get("pages"),
        "email": request.args.get("email"),
        "phone": request.args.get("phone"),
        "asstype":request.args.get("asstype"),
        "file": request.args.get("file"),  # Include file name
    }
    
    email = request.args.get('email')
    selected_college = request.args.get('college')
    
    # Check if the email matches the logged-in user's email
    if email != session.get('user'):
        error = "Logged-in user email does not match the provided email"
        return render_template('pricing.html', error=error)
    
    # Fetch the user's registered college from the database
    user = users.query.filter_by(email=session.get('user')).first()
    
    if not user:
        return redirect(url_for('login'))  # Handle case where user is not found in the database
    
    registered_college = user.college
    
    # Check if the selected college matches the registered college
    if selected_college != registered_college:
        error = "You can only select your registered college"
        return render_template('pricing.html', error=error)
    
    # Render the order page if all checks pass
    return render_template('order.html', data=data)


    



@app.route('/success')
def success():
    return render_template('success.html')

from werkzeug.utils import secure_filename
import os
from datetime import datetime

@app.route('/save-order', methods=['POST'])
def save_order():
    # Check if a file is uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part", "error")
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash("No selected file", "error")
            return redirect(request.url)
        
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            flash("File uploaded successfully!", "success")

    # Save the file temporarily and read its binary content
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')  # Move folder outside OneDrive

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
         print("Creating uploads folder...")
      

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        print(f"File will be saved to: {os.path.abspath(file_path)}")

        
        # Debugging file path
        print(f"Uploads folder path: {app.config['UPLOAD_FOLDER']}")
    
        file.save(file_path)
        print(f"File successfully saved: {filename}")
        
        with open(file_path, "rb") as f:
            file_data = f.read()

        # Optional: Remove the temporary file
        os.remove(file_path)

    except Exception as e:
        print(f"Error saving file: {str(e)}")  # Add logging here
        return jsonify({"error": f"Error saving file: {str(e)}"}), 500

    # Retrieve form data from the request
    college = request.form.get('college')
    work_type = request.form.get('type')
    urgency = request.form.get('urgency')
    words = request.form.get('length')
    pages = request.form.get('pages')
    asstype = request.form.get("asstype")
    email = request.form.get('email')
    phone = request.form.get('phone')

    # Validate required fields
    if not all([college, work_type, urgency, words, asstype, pages, email, phone]):
        return jsonify({"error": "Missing required fields"}), 400

    # Validate numeric fields
    try:
        words = int(words)
        pages = int(pages)
    except ValueError:
        return jsonify({"error": "Invalid numeric values"}), 400

    # Save data to the database
    try:
        new_order = Orders(
            email=email,
            college_name=college,
            words=words,
            pages=pages,
            urgency=urgency,
            phone=phone,
            assignmentType=asstype,
            file_name=filename,
            placed_date=datetime.now(),
            file_data=file_data
        )
        db.session.add(new_order)
        db.session.commit()

        # Redirect to the payment page with the order ID
        return redirect(url_for('payment', order_id=new_order.id))

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/payment', methods=['GET'])
def payment():
    # Retrieve the order ID from query parameters
    order_id = request.args.get('order_id')

    # Fetch the order details from the database
    order = Orders.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Render the payment page with order details
    return render_template('payment.html', order=order)
@app.route('/process-payment', methods=['POST'])
def process_payment():
    # Retrieve form data from the payment form
    order_id = request.form.get('order_id')
    payment_method = request.form.get('payment_method')

    # Validate input fields
    if not order_id or not payment_method:
        return jsonify({"error": "Missing payment details"}), 400

    # Fetch the order from the database
    order = Orders.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Simulate payment processing
    try:
        # Replace this block with integration to a payment gateway
        payment_status = "success"  # Assume payment is successful for now
        transaction_id = f"TXN{order_id}{int(time.time())}"  # Example transaction ID
        # Update the order in the database with payment details
        order.payment_status = payment_status
        order.payment_method = payment_method
        order.transaction_id = transaction_id
        db.session.commit()

        # Redirect to success page
        return redirect(url_for('payment_success', order_id=order_id))

    except Exception as e:
        return jsonify({"error": f"Payment processing failed: {str(e)}"}), 500
@app.route('/payment-success', methods=['GET'])
def payment_success():
    order_id = request.args.get('order_id')

    # Fetch the order details
    order = Orders.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404
    # Render success page
    return render_template('payment_success.html', order=order)


app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "nexusdb189@gmail.com"  # Your Gmail account
app.config["MAIL_PASSWORD"] = "kxgyhptfuoilxvaq"  # App-specific password
app.config["MAIL_DEFAULT_SENDER"] = "nex@gmail.com"  # Default sender
app.config['UPLOAD_FOLDER'] = './uploads'  # Folder to save the uploaded files

mail = Mail(app)

@app.route("/send-email", methods=["POST"])
def send_email():
    # Check if the 'pdf-upload' field exists in the request files
    if 'pdf-upload' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['pdf-upload']  # Get the uploaded file

    # Check if the file is empty
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file to the 'uploads' folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure the directory exists
        file.save(file_path)  # Save the file
    except Exception as e:
        return jsonify({"error": f"Error saving file: {str(e)}"}), 500

    data = request.form  # Form data from the frontend

    # Get the sender email from the form data
    sender_email = data.get("email")
    if not sender_email:
        return jsonify({"error": "Sender email is missing in the order summary."}), 400

    try:
        # Construct the email message
        msg = Message(
            subject="New Order Summary",
            sender=sender_email,  # Use the email from the order summary as the sender
            recipients=["nexusdb189@gmail.com"],  # Receiver email
            body=f"""
            New Order Summary:
            ---------------------------
            College: {data['college']}
            Type: {data['type']}
            Urgency: {data['urgency']}
            Word/Page Count: {data['length']}
            Number of Pages: {data['pages']}
            Details: {data['details']}
            Email: {sender_email}
            Phone: {data['phone']}
            Total Price: {data['totalPrice']}
            """
        )

        # Attach the PDF file to the email
        with open(file_path, "rb") as f:
            msg.attach(file.filename, "application/pdf", f.read())

        # Send the email
        mail.send(msg)

        return jsonify({"message": "Email sent successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True, port=5600)
