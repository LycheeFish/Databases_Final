import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor

def predict_sales(data, month, day, item_type):
    """
    Predict sales based on the provided month, day, and item type.

    Parameters:
        data (pd.DataFrame): Data containing the Date, itemDescription, and other columns.
        month (int): Month for prediction.
        day (int): Day of the month for prediction.
        item_type (str): The specific item type (e.g., milk, vegetables) to predict sales for.

    Returns:
        float: Predicted sales for the specified month, day, and item type.
    """
    data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')

    filtered_data = data[data['itemDescription'] == item_type]

    grouped = filtered_data.groupby(['Date', 'itemDescription']).size().reset_index(name='count')

    le = LabelEncoder()
    grouped['item_encoded'] = le.fit_transform(grouped['itemDescription'])

    grouped['month'] = grouped['Date'].dt.month
    grouped['day_of_month'] = grouped['Date'].dt.day

    X = grouped[['month', 'day_of_month']]
    y = grouped['count']

    if len(X) == 0:  
        return 1.0
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1)
    model.fit(X_train, y_train)

    example_features = pd.DataFrame({
        'month': [month],
        'day_of_month': [day]
    })
    predicted_sales = model.predict(example_features)
    return predicted_sales[0]
