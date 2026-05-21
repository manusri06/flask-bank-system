# 🏦 MSS Pay - Flask Banking System

A full-stack online banking web application built with **Python Flask** and **MySQL**, deployed on **Render** with a cloud database on **Aiven**.

## 🌐 Live Demo
👉 [https://flask-bank-system-z61t.onrender.com](https://flask-bank-system-z61t.onrender.com)

> ⚠️ First load may take 30-50 seconds (free tier spin-up). Please wait!

---

## 📸 Features

- ✅ User Registration & Login
- ✅ Secure Password Hashing (Werkzeug)
- ✅ Deposit Money
- ✅ Transfer Money to Other Users
- ✅ View Account Balance
- ✅ Transaction History
- ✅ Session Management
- ✅ Logout

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | MySQL (Aiven Cloud) |
| Frontend | HTML, CSS |
| Hosting | Render (Free Tier) |
| Security | Werkzeug Password Hashing |

---

## 📁 Project Structure

```
flask-bank-system/
├── static/              # Static files (images, CSS)
├── templates/           # HTML templates
│   ├── signup.html
│   ├── login.html
│   ├── dashboard.html
│   ├── addbal.html
│   ├── pay.html
│   ├── history.html
│   └── viewbal.html
├── app.py               # Main Flask application
├── requirements.txt     # Python dependencies
└── Procfile             # Deployment configuration
```

---

## 🗄️ Database Schema

```sql
-- Customers Table
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(50) UNIQUE,
    password VARCHAR(500)
);

-- Accounts Table
CREATE TABLE accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    balance DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Transactions Table
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    from_acc INT,
    to_acc INT,
    amount DECIMAL(10,2),
    status VARCHAR(100),
    remaining_balance DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## ⚙️ Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/manusri06/flask-bank-system.git
cd flask-bank-system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set environment variables
```bash
# Windows (PowerShell)
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD="yourpassword"
$env:DB_NAME="banking_db"
$env:SECRET_KEY="your-secret-key"
```

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

---

## 🚀 Deployment

This app is deployed using:
- **Render** - Flask web hosting (free tier)
- **Aiven** - Cloud MySQL database (free tier)

### Environment Variables Required on Render:

| Variable | Description |
|----------|-------------|
| `DB_HOST` | Aiven MySQL host |
| `DB_PORT` | Aiven MySQL port |
| `DB_USER` | Aiven MySQL user |
| `DB_PASSWORD` | Aiven MySQL password |
| `DB_NAME` | Database name |
| `SECRET_KEY` | Flask secret key |

---

## 📦 Requirements

```
flask
mysql-connector-python
werkzeug
gunicorn
```

---

## 👤 Author

**Manusri06**
- GitHub: [@manusri06](https://github.com/manusri06)

---

## 📝 License

This project is for educational purposes — DBMS College Project.
