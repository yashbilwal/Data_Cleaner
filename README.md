# 📊 Data Filteration & Cleaning Tool

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%23563D7C.svg?style=for-the-badge&logo=bootstrap&logoColor=white)

A web application for cleaning and filtering messy CSV data with user authentication and file management capabilities.

## ✨ Features

- 🔐 **User Authentication** (Register/Login/Logout)
- 📁 **CSV File Upload** with validation
- 🧹 **Automatic Data Cleaning**:
  - Removes empty columns
  - Handles multi-header CSVs
  - Transforms to tidy format
- 💾 **File Management**:
  - View processed files
  - Download cleaned data
- 🎨 **Beautiful UI** with Bootstrap

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 5.7+
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/yashbilwal/Data_Cleaner.git
cd Data_Cleaner

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt



Configuration
Create .env file:

MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DB=data_filteration
SECRET_KEY=your-secret-key-here



Initialize database:
python init_db.py


Running
python app.py


Open http://localhost:5000 in your browser
