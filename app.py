from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random
import string
from flask import jsonify
from flask import Response
from utils import generate_invoice_pdf


# إنشاء تطبيق Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()  # تعيين مفتاح سري عشوائي

# إعداد اتصال قاعدة البيانات MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # اسم المستخدم لقاعدة البيانات
app.config['MYSQL_PASSWORD'] = ''  # كلمة مرور قاعدة البيانات
app.config['MYSQL_DB'] = 'barcod_system'

mysql = MySQL(app)

def generate_short_id(length=8):
    """توليد معرف قصير يتراوح طوله بين 5 إلى 22 حرفًا ورقمًا"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def is_admin(user_id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute('SELECT is_active FROM users WHERE id=%s', (user_id,))
        result = cursor.fetchone()
    except Exception as e:
        print(f"Database Error: {e}")
        result = None
    finally:
        cursor.close()
    if result:
        return result[0] == 1  # تأكد من أن القيمة هي 1 لتكون True
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        try:
            cursor.execute('SELECT id, password_hash, is_active FROM users WHERE username=%s', (username,))
            user = cursor.fetchone()
        except Exception as e:
            print(f"Database Error: {e}")
            user = None
        finally:
            cursor.close()
        
        if user and check_password_hash(user[1], password):
            if user[2]:  # التحقق من حالة تفعيل الحساب
                session['user_id'] = user[0]
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Your account is not active yet. Please contact admin.', 'danger')
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password)
        
        cursor = mysql.connection.cursor()
        try:
            cursor.execute('INSERT INTO users (id, username, password_hash, is_active) VALUES (%s, %s, %s, %s)', 
                           (generate_short_id(8), username, hashed_password, False))
            mysql.connection.commit()
            flash('Registration successful! Please wait for admin approval.', 'success')
        except Exception as e:
            print(f"Database Error: {e}")
            flash('An error occurred during registration.', 'danger')
        finally:
            cursor.close()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('manage_products'))
    return redirect(url_for('login'))

@app.route('/manage_products', methods=['GET', 'POST'])
def manage_products():
    if 'user_id' not in session:
        flash('You need to log in to manage products.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        barcode = request.form['barcode']
        name = request.form['name']
        purchase_price = request.form['purchase_price']
        sale_price = request.form['sale_price']
        quantity = request.form['quantity']
        manufacturer = request.form['manufacturer']
        product_id = request.form.get('product_id')

        cursor = mysql.connection.cursor()
        try:
            if product_id:
                # تحديث المنتج
                cursor.execute('UPDATE products SET barcode=%s, name=%s, purchase_price=%s, sale_price=%s, quantity=%s, manufacturer=%s WHERE id=%s', 
                               (barcode, name, purchase_price, sale_price, quantity, manufacturer, product_id))
                flash('Product updated successfully!', 'success')
            else:
                # التحقق من وجود المنتج
                cursor.execute('SELECT * FROM products WHERE barcode=%s', (barcode,))
                existing_product = cursor.fetchone()
                
                if existing_product:
                    flash('Product with this barcode already exists!', 'danger')
                else:
                    product_id = generate_short_id(12)  # توليد معرف قصير للمنتج
                    cursor.execute('INSERT INTO products (id, barcode, name, purchase_price, sale_price, quantity, manufacturer) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                                   (product_id, barcode, name, purchase_price, sale_price, quantity, manufacturer))
                    flash('Product added successfully!', 'success')
            mysql.connection.commit()
        except Exception as e:
            print(f"Database Error: {e}")
            flash('An error occurred while processing the product.', 'danger')
        finally:
            cursor.close()

    cursor = mysql.connection.cursor()
    try:
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
    except Exception as e:
        print(f"Database Error: {e}")
        products = []
        flash('An error occurred while fetching products.', 'danger')
    finally:
        cursor.close()

    return render_template('manage_products.html', products=products)

@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'user_id' not in session:
        flash('You need to log in to edit products.', 'danger')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        barcode = request.form['barcode']
        name = request.form['name']
        purchase_price = request.form['purchase_price']
        sale_price = request.form['sale_price']
        quantity = request.form['quantity']
        manufacturer = request.form['manufacturer']

        try:
            cursor.execute('UPDATE products SET barcode=%s, name=%s, purchase_price=%s, sale_price=%s, quantity=%s, manufacturer=%s WHERE id=%s', 
                           (barcode, name, purchase_price, sale_price, quantity, manufacturer, product_id))
            mysql.connection.commit()
            flash('Product updated successfully!', 'success')
        except Exception as e:
            print(f"Database Error: {e}")
            flash('An error occurred while updating the product.', 'danger')
        finally:
            cursor.close()
        return redirect(url_for('manage_products'))
    
    # تحميل بيانات المنتج للتعديل
    try:
        cursor.execute('SELECT * FROM products WHERE id=%s', (product_id,))
        product = cursor.fetchone()
    except Exception as e:
        print(f"Database Error: {e}")
        product = None
        flash('An error occurred while fetching product details.', 'danger')
    finally:
        cursor.close()
    
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('manage_products'))

    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<product_id>')
def delete_product(product_id):
    if 'user_id' not in session:
        flash('You need to log in to delete products.', 'danger')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    try:
        cursor.execute('DELETE FROM products WHERE id=%s', (product_id,))
        mysql.connection.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        print(f"Database Error: {e}")
        flash('An error occurred while deleting the product.', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('manage_products'))

@app.route('/admin/manage_users')
def manage_users():
    if 'user_id' not in session:
        flash('You need to log in to manage users.', 'danger')
        return redirect(url_for('login'))

    if not is_admin(session['user_id']):
        flash('You need admin privileges to manage users.', 'danger')
        return redirect(url_for('index'))

    cursor = mysql.connection.cursor()
    try:
        cursor.execute('SELECT id, username, is_active FROM users')
        users = cursor.fetchall()
    except Exception as e:
        print(f"Database Error: {e}")
        users = []
        flash('An error occurred while fetching users.', 'danger')
    finally:
        cursor.close()

    return render_template('manage_users.html', users=users)

@app.route('/admin/approve_user/<user_id>')
def approve_user(user_id):
    if 'user_id' not in session:
        flash('You need to log in to approve users.', 'danger')
        return redirect(url_for('login'))

    if not is_admin(session['user_id']):
        flash('You need admin privileges to approve users.', 'danger')
        return redirect(url_for('index'))

    cursor = mysql.connection.cursor()
    try:
        cursor.execute('UPDATE users SET is_active = TRUE WHERE id=%s', (user_id,))
        mysql.connection.commit()
        flash('User approved successfully!', 'success')
    except Exception as e:
        print(f"Database Error: {e}")
        flash('An error occurred while approving the user.', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('manage_users'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    is_admin_user = is_admin(user_id) if user_id else False
    return dict(is_admin=is_admin_user)

@app.route('/admin/delete_user/<user_id>')
def delete_user(user_id):
    if 'user_id' not in session:
        flash('You need to log in to delete users.', 'danger')
        return redirect(url_for('login'))

    current_user_id = session['user_id']

    if not is_admin(current_user_id):
        flash('You need admin privileges to delete users.', 'danger')
        return redirect(url_for('index'))

    if current_user_id == user_id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('manage_users'))

    cursor = mysql.connection.cursor()
    try:
        cursor.execute('DELETE FROM users WHERE id=%s', (user_id,))
        mysql.connection.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        print(f"Database Error: {e}")
        flash('An error occurred while deleting the user.', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('manage_users'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        flash('You need to log in to access the dashboard.', 'danger')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    
    try:
        # جمع عدد المنتجات
        cursor.execute('SELECT COUNT(*) FROM products')
        total_products = cursor.fetchone()[0]
        
        # جمع عدد المستخدمين
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # جمع بيانات المبيعات الأخيرة
        cursor.execute('SELECT id, product_id, total_price, quantity, sale_date FROM sales ORDER BY sale_date DESC LIMIT 10')
        recent_sales = cursor.fetchall()
        
        recent_alerts = ["Alert 1", "Alert 2", "Alert 3"]  # يمكنك تعديل هذه البيانات
        
    except Exception as e:
        print(f"Database Error: {e}")
        total_products = 0
        total_users = 0
        recent_sales = []
        recent_alerts = []
        flash('An error occurred while fetching dashboard data.', 'danger')
    finally:
        cursor.close()

    return render_template('home.html', total_products=total_products, total_users=total_users, recent_sales=recent_sales, recent_alerts=recent_alerts)

@app.route('/sell_product', methods=['GET', 'POST'])
def sell_product():
    if 'user_id' not in session:
        flash('You need to log in to sell products.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        barcode = request.form['barcode']
        quantity = int(request.form['quantity'])
        discount = float(request.form.get('discount', 0))
        buyer_name = request.form.get('buyer_name', '')
        buyer_phone = request.form.get('buyer_phone', '')

        cursor = mysql.connection.cursor()
        try:
            cursor.execute('SELECT id, sale_price, quantity FROM products WHERE barcode=%s', (barcode,))
            product = cursor.fetchone()

            if product:
                product_id, sale_price, available_quantity = product

                if quantity > available_quantity:
                    flash('Not enough quantity available.', 'danger')
                else:
                    total_price = sale_price * quantity
                    if discount:
                        total_price -= total_price * (discount / 100)
                    
                    # توليد receipt_id للفاتورة
                    receipt_id = generate_short_id(12)

                    cursor.execute('INSERT INTO sales (id, product_id, quantity, total_price, buyer_name, buyer_phone, receipt_id) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                                   (generate_short_id(12), product_id, quantity, total_price, buyer_name, buyer_phone, receipt_id))
                    cursor.execute('UPDATE products SET quantity=%s WHERE id=%s',
                                   (available_quantity - quantity, product_id))

                    mysql.connection.commit()
                    flash('Product sold successfully!', 'success')
            else:
                flash('Product not found.', 'danger')
        except Exception as e:
            print(f"Database Error: {e}")
            flash('An error occurred while selling the product.', 'danger')
        finally:
            cursor.close()

    return render_template('sell_product.html')

@app.route('/api/product')
def api_product():
    barcode = request.args.get('barcode')
    if not barcode:
        return jsonify({'error': 'Barcode is required'}), 400

    cursor = mysql.connection.cursor()
    try:
        cursor.execute('SELECT name, sale_price FROM products WHERE barcode=%s', (barcode,))
        product = cursor.fetchone()
        if product:
            return jsonify({'name': product[0], 'sale_price': float(product[1])})
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        print(f"Database Error: {e}")
        return jsonify({'error': 'An error occurred'}), 500
    finally:
        cursor.close()
@app.route('/sell_product/complete', methods=['POST'])
def complete_sale():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    items = data.get('items')
    total_price = data.get('totalPrice')
    buyer_name = data.get('buyerName', '')
    buyer_phone = data.get('buyerPhone', '')

    if not items or total_price is None:
        return jsonify({'error': 'Invalid data'}), 400

    cursor = mysql.connection.cursor()
    try:
        receipt_id = generate_short_id(12)

        # Retrieve seller_id from the session
        seller_id = session['user_id']

        for item in items:
            cursor.execute('SELECT id, quantity, sale_price FROM products WHERE name=%s', (item['productName'],))
            product = cursor.fetchone()
            if product:
                product_id, available_quantity, sale_price = product
                if item['quantity'] > available_quantity:
                    return jsonify({'error': f'Not enough stock for product {item["productName"]}'}), 400

                total = item['quantity'] * sale_price
                cursor.execute('INSERT INTO sales (id, product_id, quantity, total_price, buyer_name, buyer_phone, receipt_id, price, seller_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                               (generate_short_id(12), product_id, item['quantity'], total, buyer_name, buyer_phone, receipt_id, sale_price, seller_id))
                cursor.execute('UPDATE products SET quantity=%s WHERE id=%s',
                               (available_quantity - item['quantity'], product_id))
            else:
                return jsonify({'error': f'Product {item["productName"]} not found'}), 404

        mysql.connection.commit()

        receipt_items = []
        for item in items:
            cursor.execute('SELECT sale_price FROM products WHERE name=%s', (item['productName'],))
            sale_price = cursor.fetchone()[0]
            receipt_items.append({
                'productName': item['productName'],
                'quantity': item['quantity'],
                'total': item['quantity'] * sale_price
            })

        # Generate PDF
        pdf_buffer = generate_invoice_pdf(receipt_id, receipt_items, total_price, buyer_name, buyer_phone, seller_id)

        return Response(pdf_buffer, mimetype='application/pdf', headers={
            'Content-Disposition': f'attachment; filename=invoice_{receipt_id}.pdf'
        })

    except Exception as e:
        print(f"Database Error: {e}")
        mysql.connection.rollback()
        return jsonify({'error': 'An error occurred'}), 500
    finally:
        cursor.close()


@app.route('/search_receipt', methods=['GET', 'POST'])
def search_receipt():
    if 'user_id' not in session:
        flash('You need to log in to search for receipts.', 'danger')
        return redirect(url_for('login'))
    
    receipt = None
    items = []
    
    receipt_id = request.form.get('receipt_id')
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute('SELECT receipt_id, buyer_name, buyer_phone, total_price, sale_date FROM sales WHERE receipt_id=%s', (receipt_id,))
        receipt = cursor.fetchone()
        
        if receipt:
            cursor.execute('SELECT product_name, quantity, price, (quantity * price) AS total_price FROM sales WHERE receipt_id=%s', (receipt_id,))
            items = cursor.fetchall()
        else:
            flash('Receipt not found.', 'danger')
    
    except Exception as e:
        print(f"Database Error: {e}")
        flash('An error occurred while searching for the receipt.', 'danger')
    finally:
        cursor.close()
    
    return render_template('search.html', receipt=receipt, items=items)

@app.route('/search_product', methods=['GET', 'POST'])
def search_product():
    if 'user_id' not in session:
        flash('You need to log in to search for products.', 'danger')
        return redirect(url_for('login'))
    
    product = None
    
    barcode = request.form.get('barcode')
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute('SELECT name, quantity, sale_price AS price FROM products WHERE barcode=%s', (barcode,))
        product = cursor.fetchone()
        
        if not product:
            flash('Product not found.', 'danger')
    
    except Exception as e:
        print(f"Database Error: {e}")
        flash('An error occurred while searching for the product.', 'danger')
    finally:
        cursor.close()
    
    return render_template('search.html', product=product)

@app.route('/search_user', methods=['GET', 'POST'])
def search_user():
    if 'user_id' not in session:
        flash('You need to log in to search for users.', 'danger')
        return redirect(url_for('login'))
    
    user = None
    
    user_id = request.form.get('user_id')
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute('SELECT id, username, email, role FROM users WHERE id=%s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found.', 'danger')
    
    except Exception as e:
        print(f"Database Error: {e}")
        flash('An error occurred while searching for the user.', 'danger')
    finally:
        cursor.close()
    
    return render_template('search.html', user=user)

if __name__ == '__main__':

    app.run(debug=True)
