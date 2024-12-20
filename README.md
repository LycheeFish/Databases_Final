# Grocery Database Application

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Dataset Information](#dataset-information)
- [Usage](#usage)

---

## Introduction
This project is a Grocery Database Application that allows users to interact with a database containing a curated grocery dataset. The application uses Python and SQLAlchemy for database operations and provides essential features to manage and query the dataset.

---

## Installation
1. Clone this repository:
   
bash
   git clone https://github.com/yourusername/repository-name.git
   cd repository-name
Install the required dependencies using the requirements.txt file:
'''
pip install -r requirements.txt
'''
## Configuration
To run this application, you need to create a config.py file in the base folder of the project. Use the following template for your config.py file:
'''
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'a_key')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploaded_images')
    DB_URI = os.getenv('DB_URI', 'mysql+pymysql://avnadmin:AVNS_ZQwUAF71XLlxalNAIfe@mysql-3d2e73f1-databasesfinal.f.aivencloud.com:13103/defaultdb')
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "ssl": {"verify_cert": False}
        }
    }
'''
The given format for DB_URI is dialect+driver://username:password@host:port/database
Place the config.py file in the root directory of the project.

## Database Setup
To populate the database, follow these steps:

Populate the Users Table:
Insert sample data into the Users table using the following SQL query:
'''
INSERT INTO Users (email, name, password, payment_info, phone_number, user_id)
VALUES 
('john.doe@example.com', 'John Doe', 'password123', 'Visa 1234', '123-456-7890', 1),
('jane.smith@example.com', 'Jane Smith', 'securePass456', 'Mastercard 5678', '987-654-3210', 2),
('michael.brown@example.com', 'Michael Brown', 'mikePassword789', 'PayPal account', '555-123-4567', 3),
('emily.wilson@example.com', 'Emily Wilson', 'emilySecure321', 'Amex 9999', '444-987-6543', 4),
('david.jones@example.com', 'David Jones', 'davidPass000', 'Visa 5678', '666-555-4444', 5);
Populate the Groceries Dataset Table:
Use the updated_file.csv included in the repository to populate the Groceries_dataset table. This file contains a truncated version of the full dataset.
'''
For the full version of the dataset, visit:
Groceries Dataset on Kaggle (https://www.kaggle.com/datasets/heeraldedhia/groceries-dataset)

## Dataset Information
The dataset contains information about grocery purchases. The included updated_file.csv provides a sample of the full dataset to work with.

## Usage
Once the configuration and database setup are complete, you can run the app from the root directory with 
'''
flask --app projectapp run --debug
'''
