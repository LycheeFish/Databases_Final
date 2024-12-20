-- Users Table
CREATE TABLE users (
    userid INT AUTO_INCREMENT PRIMARY KEY, 
    username VARCHAR(50) NOT NULL UNIQUE,  
    password VARCHAR(255) NOT NULL        
);

-- Stores Table
CREATE TABLE Stores (
    store_id INT AUTO_INCREMENT PRIMARY KEY,
    store_name VARCHAR(255) NOT NULL,
    location TEXT NOT NULL,
    closing_time TIME,
    contact_info TEXT,
    store_type VARCHAR(50)
);

-- Food Inventory Table
CREATE TABLE FoodInventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    food_item VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    available_time DATETIME NOT NULL,
    expiry_time DATETIME NOT NULL,
    FOREIGN KEY (store_id) REFERENCES Stores(store_id)
);

-- Orders Table
CREATE TABLE Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    store_id INT NOT NULL,
    inventory_id INT NOT NULL,
    order_time DATETIME NOT NULL,
    pickup_time DATETIME NOT NULL,
    payment_status VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (store_id) REFERENCES Stores(store_id),
    FOREIGN KEY (inventory_id) REFERENCES FoodInventory(inventory_id)
);

-- Reviews Table
CREATE TABLE Reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comments TEXT,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Detailed Inventory Table
CREATE TABLE DetailedInventory (
    food_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50),
    nutrition_info TEXT,
    batch_number VARCHAR(50)
);

-- Expiration Tracking Table
CREATE TABLE ExpirationTracking (
    inventory_id INT NOT NULL,
    expiry_date DATETIME NOT NULL,
    remaining_quantity INT,
    PRIMARY KEY (inventory_id, expiry_date),
    FOREIGN KEY (inventory_id) REFERENCES FoodInventory(inventory_id)
);

-- Usage Metrics Table
CREATE TABLE UsageMetrics (
    metric_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_start_time DATETIME NOT NULL,
    session_end_time DATETIME NOT NULL,
    actions_performed INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Sales Analytics Table
CREATE TABLE SalesAnalytics (
    sales_id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    time_period VARCHAR(50) NOT NULL,
    revenue_generated DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (store_id) REFERENCES Stores(store_id)
);

-- Support Tickets Table
CREATE TABLE SupportTickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    store_id INT,
    issue_type VARCHAR(255),
    status VARCHAR(50),
    created_at DATETIME NOT NULL,
    resolved_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (store_id) REFERENCES Stores(store_id)
);

-- Transaction Table
CREATE TABLE Transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    user_id INT NOT NULL,
    store_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50),
    transaction_status VARCHAR(50),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (store_id) REFERENCES Stores(store_id)
);

-- Payout Table
CREATE TABLE Payouts (
    payout_id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    payout_amount DECIMAL(10, 2) NOT NULL,
    payout_date DATETIME NOT NULL,
    FOREIGN KEY (store_id) REFERENCES Stores(store_id)
);

CREATE TABLE Groceries_dataset (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    Member_number INT NOT NULL,    
    Date DATE,
    itemDescription VARCHAR(255)
);

CREATE TABLE user_reviews (
    user_id INT NOT NULL,        
    store_id INT NOT NULL,        
    review_date DATE NOT NULL,   
    review_data JSON,         
    PRIMARY KEY (user_id, store_id, review_date) 
);








