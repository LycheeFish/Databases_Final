from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import pandas as pd
import os
import sys
import random
import string
import json
from flask import send_from_directory
from config import Config


from datetime import datetime
from ml1 import predict_sales  
from ml2 import recommend_items_for_user

app = Flask(__name__)
app.config.from_object(Config)

db_uri = app.config['DB_URI']
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']

engine = create_engine(
    db_uri,
    connect_args=Config.SQLALCHEMY_ENGINE_OPTIONS["connect_args"]
)
db_session = scoped_session(sessionmaker(bind=engine))

UPLOAD_FOLDER = 'uploaded_images' 
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploaded_images/<filename>')
def uploaded_images(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/hello', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        query = text("SELECT * FROM Groceries_dataset")
        result = db_session.execute(query)
        rows = result.fetchall()

        columns = result.keys() 
        data = pd.DataFrame(rows, columns=columns)

        # Run the ML function
        output = predict_sales(data)
        return render_template('hello.html', output=output)

    return render_template('hello.html', output=None)

@app.route('/groceries', methods=['GET'])
def groceries():
    query = text('SELECT id, Member_number, Date, itemDescription FROM Groceries_dataset LIMIT 10')
    result = db_session.execute(query)
    groceries = [
        {
            "id": row.id,
            "Member_number": row.Member_number,
            "Date": row.Date,
            "itemDescription": row.itemDescription
        }
        for row in result
    ]
    return render_template('groceries.html', groceries=groceries)

@app.route('/stores', methods=['GET'])
def list_stores():
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    try:
        query_stores = text("SELECT store_id, store_name, store_type, location, contact_info, closing_time FROM Stores")
        result_stores = db_session.execute(query_stores)
        all_stores = [
            {
                "store_id": row.store_id,
                "store_name": row.store_name,
                "store_type": row.store_type,
                "location": row.location,
                "contact_info": row.contact_info,
                "closing_time": row.closing_time
            }
            for row in result_stores
        ]

        query_groceries = text("SELECT Member_number, itemDescription FROM Groceries_dataset")
        result_groceries = db_session.execute(query_groceries)
        groceries_df = pd.DataFrame(result_groceries.fetchall(), columns=['Member_number', 'itemDescription'])

        user_id = session['user_id']
        recommended_items = recommend_items_for_user(groceries_df, user_id, n=5)

        query_inventory = text("""
            SELECT DISTINCT store_id 
            FROM FoodInventory 
            WHERE food_item IN :recommended_items
        """)
        result_inventory = db_session.execute(query_inventory, {"recommended_items": tuple(recommended_items)})
        store_ids_with_items = [row.store_id for row in result_inventory]

        filtered_stores = [store for store in all_stores if store['store_id'] in store_ids_with_items]

        return render_template(
            'stores.html',
            stores=all_stores,
            recommendations=recommended_items,
            stores_with_recommendations=filtered_stores
        )

    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        db_session.remove()

@app.route('/store/<int:store_id>', methods=['GET'])
def store_inventory(store_id):
    try:
        query = text("""
            SELECT inventory_id, food_item, quantity, unit_price, available_time, expiry_time 
            FROM FoodInventory 
            WHERE store_id = :store_id
        """)
        result = db_session.execute(query, {"store_id": store_id})
        items = [
            {
                "inventory_id": row.inventory_id,
                "food_item": row.food_item,
                "quantity": row.quantity,
                "unit_price": float(row.unit_price),
                "available_time": row.available_time,
                "expiry_time": row.expiry_time
            }
            for row in result
        ]

        stored_date = session.get('Date')
        if stored_date:
            month = int(stored_date.split('-')[1])  
            day = int(stored_date.split('-')[2])  
        else:
            flash("Login date not found, using default values.", "warning")
            month, day = 3, 15  

        query_groceries = text("SELECT * FROM Groceries_dataset")
        result_groceries = db_session.execute(query_groceries)
        groceries_df = pd.DataFrame(result_groceries.fetchall(), columns=result_groceries.keys())

        for item in items:
            predicted_sales = predict_sales(groceries_df, month, day, item['food_item'])
            if (predicted_sales < 1):
                item['adjusted_price'] = round(item['unit_price'] - predicted_sales, 2)
            else:
                item['adjusted_price'] = round(item['unit_price'] + predicted_sales, 2)


        return render_template('store_inventory.html', items=items, store_id=store_id)

    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        db_session.remove()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            query = text("SELECT user_id, password FROM Users WHERE email = :email")
            result = db_session.execute(query, {"email": email}).fetchone()

            if result:
                user_id, db_password = result
                if password == db_password:
                    session['user_id'] = user_id
                    session['Date'] = datetime.now().date().strftime('%Y-%m-%d') 
                    #session['Date'] = '2023-12-25'
                    flash('Login successful!', 'success')
                    return redirect(url_for('list_stores'))
                else:
                    flash('Invalid password. Please try again.', 'danger')
            else:
                flash('Email not found. Please try again.', 'danger')

        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
        finally:
            db_session.remove()

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET'])
def profile():
    if 'user_id' in session:
        try:
            query_user = text("SELECT name, email, phone_number FROM Users WHERE user_id = :user_id")
            result_user = db_session.execute(query_user, {"user_id": session['user_id']}).fetchone()

            query_purchases = text("""
                SELECT Date, itemDescription 
                FROM Groceries_dataset 
                WHERE Member_number = :member_number 
                ORDER BY Date DESC 
                LIMIT 3
            """)
            result_purchases = db_session.execute(query_purchases, {"member_number": session['user_id']}).fetchall()

            user_data = {
                "name": result_user.name,
                "email": result_user.email,
                "phone_number": result_user.phone_number,
                "date": session.get('Date', 'Date not set'),  
                "purchases": [{"Date": row.Date, "itemDescription": row.itemDescription} for row in result_purchases]
            }

            return render_template('profile.html', user=user_data)
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('login'))
        finally:
            db_session.remove()
    else:
        flash("Please log in to access your profile.", "warning")
        return redirect(url_for('login'))

@app.route('/recommendations')
def recommendations():
    if 'user_id' in session:
        try:
            query = text("SELECT Member_number, itemDescription FROM Groceries_dataset")
            result = db_session.execute(query)
            groceries_df = pd.DataFrame(result.fetchall(), columns=['Member_number', 'itemDescription'])

            user_id = session['user_id'] 
            recommended_items = recommend_items_for_user(groceries_df, user_id, n=5)

            return render_template('recommendations.html', items=recommended_items)

        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            db_session.remove()
    else:
        return "Please log in to see recommendations.", 401

@app.route('/store/<int:store_id>/purchase', methods=['POST'])
def purchase_item(store_id):
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    try:
        # Fetch form data
        inventory_id = request.form.get('inventory_id')
        food_item = request.form.get('food_item')
        adjusted_price = request.form.get('adjusted_price')
        user_id = session['user_id']
        purchase_date = datetime.now().strftime('%Y-%m-%d')

        query = text("""
            INSERT INTO Groceries_dataset (Member_number, Date, itemDescription)
            VALUES (:user_id, :purchase_date, :food_item)
        """)
        db_session.execute(query, {
            "user_id": user_id,
            "purchase_date": purchase_date,
            "food_item": food_item
        })
        db_session.commit()

        flash(f"Purchased {food_item} successfully!", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    finally:
        db_session.remove()

    return redirect(url_for('store_inventory', store_id=store_id))


@app.route('/post_review', methods=['GET'])
def post_review():
    if 'user_id' not in session:
        flash("Please log in to post a review.", "warning")
        return redirect(url_for('login'))
    return render_template('post_review.html')


@app.route('/submit_review', methods=['POST'])
def submit_review():
    if 'user_id' not in session:
        flash("Please log in to post a review.", "warning")
        return redirect(url_for('login'))
    
    try:
        user_id = session['user_id']
        store_id = request.form['store_id']
        comment = request.form['comment']
        review_date = datetime.now().strftime('%Y-%m-%d')

        photo = request.files.get('photo')
        photo_path = None
        if photo and photo.filename != '':
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            photo_path = photo_path.replace("\\", "/")  

            photo.save(photo_path)

        review_data = {"text": comment}
        if photo_path:
            review_data["photo"] = photo_path 

        review_data_json = json.dumps(review_data)

        query = text("""
            INSERT INTO user_reviews (user_id, store_id, review_date, review_data)
            VALUES (:user_id, :store_id, :review_date, :review_data)
        """)
        db_session.execute(query, {
            "user_id": user_id,
            "store_id": store_id,
            "review_date": review_date,
            "review_data": review_data_json
        })
        db_session.commit()

        flash("Review submitted successfully!", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        print("Error:", str(e))
    finally:
        db_session.remove()

    return redirect(url_for('profile'))


@app.route('/store/<int:store_id>/reviews', methods=['GET'])
def store_reviews(store_id):
    try:
        query = text("""
            SELECT review_data
            FROM user_reviews
            WHERE store_id = :store_id
        """)
        result = db_session.execute(query, {"store_id": store_id})
        reviews = [row.review_data for row in result]

        parsed_reviews = []
        for review in reviews:
            review_content = json.loads(review)
            parsed_reviews.append(review_content)

        return render_template('store_reviews.html', store_id=store_id, reviews=parsed_reviews)
    except Exception as e:
        flash(f"Error fetching reviews: {e}", "danger")
        return redirect(url_for('list_stores'))
    finally:
        db_session.remove()



if __name__ == '__main__':
    app.run(debug=True)
