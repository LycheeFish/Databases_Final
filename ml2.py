import warnings
warnings.filterwarnings("ignore")

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def recommend_items_for_user(data, user_id, n=5):
    data['item_id'] = data['itemDescription'].astype('category').cat.codes
    data['user_id'] = data['Member_number'].astype('category').cat.codes

    data['interaction'] = 1

    unique_users = data['user_id'].unique()
    unique_items = data['item_id'].unique()
    all_interactions = set(zip(data['user_id'], data['item_id']))

    negative_samples = []
    for user in unique_users:
        for item in unique_items:
            if (user, item) not in all_interactions:
                negative_samples.append([user, item, 0])

    negative_df = pd.DataFrame(negative_samples, columns=['user_id', 'item_id', 'interaction'])

    full_data = pd.concat([data[['user_id', 'item_id', 'interaction']], negative_df])

    X = full_data[['user_id', 'item_id']]
    y = full_data['interaction']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.2f}")

    def recommend_items(user_id, n=5):
        interacted_items = full_data[(full_data['user_id'] == user_id) & (full_data['interaction'] == 1)]['item_id'].unique()
        items_to_predict = [item for item in unique_items if item not in interacted_items]
        
        predictions = [
            (item, model.predict_proba([[user_id, item]])[0][1]) for item in items_to_predict
        ]
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        item_descriptions = data[['item_id', 'itemDescription']].drop_duplicates()
        recommended_items = [
            item_descriptions[item_descriptions['item_id'] == item_id]['itemDescription'].iloc[0]
            for item_id, _ in predictions[:n]
        ]
        return recommended_items

    return recommend_items(user_id, n)
