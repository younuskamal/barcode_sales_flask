import pymysql
from werkzeug.security import generate_password_hash

# إعداد الاتصال بقاعدة البيانات
db = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='barcod_system'
)

cursor = db.cursor()

# معلومات المستخدم الجديد
username = 'admin'  # اسم المستخدم الذي تريد إنشاء حساب له
password = 'admin'  # تأكد من استخدام كلمة مرور قوية
hashed_password = generate_password_hash(password)
user_id = '213568'  # تأكد من استخدام معرف فريد
is_active = True

# SQL لإدراج المستخدم في قاعدة البيانات
sql = """
    INSERT INTO users (id, username, password_hash, is_active)
    VALUES (%s, %s, %s, %s)
"""

try:
    cursor.execute(sql, (user_id, username, hashed_password, is_active))
    db.commit()
    print('User account created successfully.')
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    cursor.close()
    db.close()
