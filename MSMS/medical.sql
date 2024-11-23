-- Table: addmp (Medicine Parts)
CREATE TABLE addmp (
  sno INT(11) NOT NULL AUTO_INCREMENT,
  medicine VARCHAR(500) NOT NULL,
  PRIMARY KEY (sno)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: addpd (Product Details)
CREATE TABLE addpd (
  sno INT(11) NOT NULL AUTO_INCREMENT,
  product VARCHAR(200) NOT NULL,
  PRIMARY KEY (sno)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: posts (Medical Facilities)
CREATE TABLE posts (
  mid INT(11) NOT NULL AUTO_INCREMENT,
  medical_name VARCHAR(100) NOT NULL,
  owner_name VARCHAR(100) NOT NULL,
  phone_no VARCHAR(20) NOT NULL UNIQUE,
  address VARCHAR(150) NOT NULL,
  PRIMARY KEY (mid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: medicines (Medications)
CREATE TABLE medicines (
  id INT(11) NOT NULL AUTO_INCREMENT,
  amount INT(11) NOT NULL CHECK (amount >= 0),
  name VARCHAR(100) NOT NULL,
  medicines VARCHAR(500) NOT NULL,
  products VARCHAR(500) NOT NULL,
  email VARCHAR(50) NOT NULL UNIQUE,
  mid INT(11) NOT NULL,
  stock_status ENUM('Low Stock', 'Sufficient Stock', 'High Stock') DEFAULT 'Sufficient Stock',
  PRIMARY KEY (id),
  FOREIGN KEY (mid) REFERENCES posts(mid) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: logs (Tracking Medicine Actions)
CREATE TABLE logs (
  id INT(11) NOT NULL AUTO_INCREMENT,
  mid INT(11) DEFAULT NULL,
  action ENUM('INSERTED', 'UPDATED', 'DELETED', 'ALERT') NOT NULL,
  date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  FOREIGN KEY (mid) REFERENCES posts(mid) ON DELETE SET NULL ON UPDATE CASCADE  -- Adjusted foreign key to reference posts(mid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: users (User Details)
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role ENUM('authority', 'medical_owner') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Triggers for logs (project-specific)
DELIMITER $$

-- Trigger for DELETE action in medicines
CREATE TRIGGER trg_MedicineDelete_log BEFORE DELETE ON medicines 
FOR EACH ROW 
BEGIN
    INSERT INTO logs (mid, action, date) VALUES (OLD.mid, 'DELETED', NOW());
END $$

-- Trigger for INSERT action in medicines
CREATE TRIGGER trg_MedicineInsert_log AFTER INSERT ON medicines 
FOR EACH ROW 
BEGIN
    INSERT INTO logs (mid, action, date) VALUES (NEW.mid, 'INSERTED', NOW());
END $$

-- Trigger for UPDATE action in medicines
CREATE TRIGGER trg_MedicineUpdate_log AFTER UPDATE ON medicines 
FOR EACH ROW 
BEGIN
    INSERT INTO logs (mid, action, date) VALUES (NEW.mid, 'UPDATED', NOW());
END $$

DELIMITER ;

-- Stored Procedure for Posts and Medicines (project-specific retrieval)
DELIMITER $$

CREATE PROCEDURE proc_MedicalSupplyRetrieve()
BEGIN
    SELECT * FROM posts;
    SELECT * FROM medicines;
END $$

DELIMITER ;


-- Function to retrieve user role (specific to this project)
DELIMITER $$

CREATE FUNCTION GetMedicalUserRole(user_name VARCHAR(255))
RETURNS VARCHAR(255)
DETERMINISTIC
BEGIN
    DECLARE user_role VARCHAR(255);
    SELECT role INTO user_role
    FROM users
    WHERE username = user_name
    LIMIT 1;  
    RETURN user_role;
END $$

DELIMITER ;

-- Adding stock_status column to medicines table (if not already added)
ALTER TABLE medicines ADD COLUMN stock_status ENUM('Low Stock', 'Sufficient Stock', 'High Stock') DEFAULT 'Sufficient Stock';

-- New Trigger to Update Medicine Stock Status
DELIMITER $$

CREATE TRIGGER trg_UpdateStockStatus
AFTER UPDATE ON medicines
FOR EACH ROW
BEGIN
    DECLARE threshold_low INT DEFAULT 10;   -- Threshold for low stock
    DECLARE threshold_high INT DEFAULT 100;  -- Threshold for high stock
    DECLARE new_status VARCHAR(50);

    -- Determine the new stock status based on the updated stock amount
    IF NEW.amount < threshold_low THEN
        SET new_status = 'Low Stock';
    ELSEIF NEW.amount >= threshold_low AND NEW.amount <= threshold_high THEN
        SET new_status = 'Sufficient Stock';
    ELSE
        SET new_status = 'High Stock';
    END IF;

    -- Update the stock_status column with the appropriate status
    UPDATE medicines
    SET stock_status = new_status
    WHERE id = NEW.id;
END $$

DELIMITER ;

INSERT INTO addmp (sno, medicine) VALUES
(1, 'Dolo 650'),
(2, 'Carpel 250 mg'),
(3, 'Azythromycin 500'),
(4, 'Azythromycin 250'),
(5, 'Rantac 300'),
(6, 'Omez'),
(7, 'Okacet'),
(8, 'Paracetomol');
INSERT INTO addpd (sno, product) VALUES
(1, 'Colgate'),
(2, 'Perfume'),
(3, 'Garnier Face Wash'),
(4, 'Garnier Face Wash');
INSERT INTO posts (mid, medical_name, owner_name, phone_no, address) VALUES
(1001, 'Ashik Medicals', 'Ashik', '7896541230', 'Kundapura'),
(1002, 'Shree Medicals', 'Shree', '8765432109', 'Udupi'),
(1003, 'Health Plus Medicals', 'HealthPlus', '9876543210', 'Mangalore');
INSERT INTO medicines (id, amount, name, medicines, products, email, mid, stock_status) VALUES
(1, 100, 'Dolo 650', 'Dolo 650, Rantac 300', 'Colgate, Perfume', 'ashik@example.com', 1001, 'Sufficient Stock'),
(2, 200, 'Carpel 250 mg', 'Carpel 250 mg, Azythromycin 500', 'Garnier Face Wash, Perfume', 'shree@example.com', 1002, 'Low Stock'),
(3, 50, 'Azythromycin 500', 'Azythromycin 500, Omez', 'Garnier Face Wash', 'healthplus@example.com', 1003, 'High Stock');
INSERT INTO logs (mid, action, date) VALUES
(1001, 'INSERTED', NOW()),
(1002, 'INSERTED', NOW()),
(1003, 'INSERTED', NOW());
INSERT INTO users (id, username, password, role) VALUES
(1, 'admin', 'admin123', 'authority');

DELIMITER $$

CREATE PROCEDURE proc_MedicineOrderInsert(
    IN p_mid INT,
    IN p_name VARCHAR(255),
    IN p_medicines VARCHAR(255),
    IN p_products VARCHAR(255),
    IN p_email VARCHAR(255),
    IN p_amount INT
)
BEGIN
    -- Insert the new medicine order
    INSERT INTO Medicines (mid, name, medicines, products, email, amount)
    VALUES (p_mid, p_name, p_medicines, p_products, p_email, p_amount);

    -- Update the total_orders for the corresponding mid in the Posts table
    UPDATE Posts
    SET total_orders = total_orders + 1
    WHERE mid = p_mid;
END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE get_all_products()
BEGIN
    -- Select all products (both medicine and products)
    SELECT 'Medicine' AS type, medicine AS name FROM Addmp
    UNION
    SELECT 'Product' AS type, product AS name FROM Addpd;

    -- Select total count of products
    SELECT COUNT(*) AS total_products
    FROM (
        SELECT 'Medicine' AS type, medicine AS name FROM Addmp
        UNION
        SELECT 'Product' AS type, product AS name FROM Addpd
    ) AS all_products;
END $$

DELIMITER ;

CREATE TABLE `OrdersPerHourLog` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `order_count` int DEFAULT NULL,
  `log_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE FUNCTION `GetOrdersPerHour`()
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE order_count INT;

    -- Count the number of orders placed in the last hour
    SELECT COUNT(*) INTO order_count
    FROM Medicines
    WHERE order_time >= NOW() - INTERVAL 1 HOUR;

    -- Insert the order count and the current time into the OrdersPerHourLog table
    INSERT INTO OrdersPerHourLog (order_count, log_time) VALUES (order_count, NOW());

    -- Return the order count
    RETURN order_count;
END;
