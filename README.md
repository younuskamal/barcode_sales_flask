# Barcode System

Barcode System is a web application built with Flask for managing products and users in a point-of-sale system. The application provides an interface for managing products, user registration and login, sales recording, and user management for administrators.

## Features

- User registration and login
- Product management (add, update, delete)
- Sales recording and PDF invoice generation
- User management by administrators (approve and delete users)
- API endpoints for product search

## Requirements

- Python 3.x
- Flask
- Flask-MySQLdb
- Werkzeug
- PyPDF2 (for generating PDF invoices)

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd <repository_directory>

2. Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate

3. Install the requirements:

pip install -r requirements.txt

4. Set up the database:

Ensure you have a MySQL database named barcod_system. You may need to create the database and necessary tables based on the application's database schema.

Running the Application
To start the development server:
python app.py

You can now access the application in your web browser at http://localhost:5000.

Usage
Login: Navigate to /login to log in.
Register New Users: Navigate to /register to register a new user.
Manage Products: Navigate to /manage_products to add, update, or delete products.
Sell Products: Navigate to /sell_product to record a sale.
Search Products: Navigate to /search_product to search for products.
Manage Users: Navigate to /admin/manage_users to manage users (admin privileges required).
API Endpoints
GET /api/product?barcode=<barcode>
Get product details based on the barcode.
Contributing
If you wish to contribute to the project, you can open issues or submit pull requests on GitHub.

License
This project is licensed under the [License Name] - see the LICENSE file for details.

Notes
Ensure to update the requirements.txt file when adding new libraries.
This project is for educational purposes and can be modified to fit your specific needs.
