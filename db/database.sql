START TRANSACTION;
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT,
    surname VARCHAR(255),
    name VARCHAR(255),
    birth_date DATE,
    phone_number VARCHAR(20),
    email VARCHAR(255),
    status VARCHAR(20),
    hashed_password VARCHAR(255),
    PRIMARY KEY (id),
    UNIQUE (phone_number),
    UNIQUE (email)
);


INSERT INTO users (id, surname, name, birth_date, phone_number, email, status, hashed_password) VALUES
(1, 'kush', 'alina', '2024-04-05', '+79328532268', 'alina.kush2009@gmail.com', 'super', 'scrypt:32768:8:1$YCFHN7hJkJRpHRxM$3661c0001d89dd8ef80bf950c5e2d1c17f6ba32c182dfa30ca0ca2674e212045b1f5c2660fdb0567a563374595b30ecba9096b9810daa64e2e4ed9b6d07dab0f'),
(2, 'user', 'test', '2024-04-11', '+79000000000', 'test@test.email', 'user', 'scrypt:32768:8:1$VvyGxZVQQWgN4XEr$225a2c70ffb800502526e2cc9dd3bdbe9808d9bb86552792b82231d8787e03e17ca86c88cf8ba7ea58697a22d23aab9740a0301ea0ddd63d793c2c0387f3cf35');

CREATE TABLE IF NOT EXISTS types (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(255),
    PRIMARY KEY (id)
);

INSERT INTO types (id, title) VALUES
(1, 'rolls'),
(2, 'pizza'),
(3, 'sets'),
(4, 'snacks');

CREATE TABLE IF NOT EXISTS images (
    id INT NOT NULL AUTO_INCREMENT,
    path VARCHAR(255),
    PRIMARY KEY (id)
);

INSERT INTO images (id, path) VALUES
(1, 'upload/img/2024-04-25_152417594905.png'),
(2, 'upload/img/2024-04-25_152447225460.png'),
(3, 'upload/img/2024-04-25_152516722039.jpg'),
(4, 'upload/img/2024-04-25_152545257513.jpg'),
(5, 'upload/img/2024-04-26_152807362457.png');

CREATE TABLE IF NOT EXISTS statuses (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(255),
    PRIMARY KEY (id)
);

INSERT INTO statuses (id, title) VALUES
(1, 'Ожидает подтверждения'),
(2, 'Готовиться'),
(3, 'Доставлен');

CREATE TABLE IF NOT EXISTS dishes (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(255),
    weight INT,
    description VARCHAR(255),
    structure VARCHAR(255),
    price INT,
    type_id INT,
    image_id INT,
    PRIMARY KEY (id),
    FOREIGN KEY(type_id) REFERENCES types (id),
    FOREIGN KEY(image_id) REFERENCES images (id)
);

INSERT INTO dishes (id, title, weight, description, structure, price, type_id, image_id) VALUES
(1, 'roll', 1900, 'nothing', 'hz', 3199, 1, 1),
(2, 'pizza', 600, 'hey grl', 'kolbaski grill', 989, 2, 2),
(3, 'salad', 300, 'vkusno', 'kapusta', 459, 4, 3),
(4, 'set', 1300, 'hehehe', 'horoshiy', 1900, 3, 4),
(5, 'position', 1000, 'description', 'sostav', 1000, 2, 5);

CREATE TABLE IF NOT EXISTS orders (
    id INT NOT NULL AUTO_INCREMENT,
    customer_id INT,
    delivery_address VARCHAR(255),
    total_amount FLOAT,
    datetime DATETIME,
    comment VARCHAR(255),
    status_id INT,
    PRIMARY KEY (id),
    FOREIGN KEY(customer_id) REFERENCES users (id),
    FOREIGN KEY(status_id) REFERENCES statuses (id)
);
INSERT INTO orders (customer_id, delivery_address, total_amount, datetime, comment, status_id) VALUES
(1, 'Оренбургский район, аэропорт Оренбург (Центральный) имени Ю.А. Гагарина', 4188.0, '2024-04-25 15:38:24.972550', 1, 3),
(1, 'Москва, проспект Андропова, 1', 4188.0, '2024-04-25 16:10:04.655614', 2, 3),
(NULL, 'Оренбург, проспект Победы, 13, корп. 3', 4188.0, '2024-04-25 20:18:17.727794', 1, 3),
(NULL, 'Оренбург, проспект Победы, 13, корп. 3', 4188.0, '2024-04-25 20:20:43.759658', 1, 3),
(NULL, 'Оренбург, проспект Победы, 13, корп. 3', 4188.0, '2024-04-25 20:21:43.780014', 1, 2),
(NULL, 'Оренбург, проспект Победы, 13, корп. 3', 4188.0, '2024-04-25 20:21:51.480620', 1, 1),
(NULL, 'Оренбург, проспект Победы, 13, корп. 3', 4188.0, '2024-04-25 21:00:37.234075', 2, 1),
(NULL, 'Оренбург, проспект Победы, 13, корп. 3', 4188.0, '2024-04-25 21:00:54.967150', 2, 1),
(NULL, 'Оренбург, проспект Победы, 13, корп. 3', 4188.0, '2024-04-25 21:02:11.399159', 1, 1),
(NULL, 'Оренбург, проспект Победы, 13, корп. 3', 4188.0, '2024-04-25 21:04:42.630854', 1, 1),
(NULL, 'Оренбург, проспект Победы, 13, корп. 3', 4188.0, '2024-04-25 21:23:33.107169', 1, 1),
(NULL, 'Оренбург, проспект Победы, 13, корп. 3', 4188.0, '2024-04-25 21:23:46.711783', 1, 1),
(NULL, 'Оренбург, проспект Победы, 13, корп. 3', 4188.0, '2024-04-25 21:23:47.055153', 1, 1),
(NULL, 'Оренбург, проспект Победы, 13, корп. 3', 4188.0, '2024-04-25 21:24:20.353495', 1, 1),
(NULL, 'Оренбург, проспект Победы, 13, корп. 3', 4188.0, '2024-04-25 21:28:25.198200', 1, 1),
(NULL, 'Оренбургский район, аэропорт Оренбург (Центральный) имени Ю.А. Гагарина', 3199.0, '2024-04-25 23:16:05.565802', 1, 1),
(NULL, 'Оренбургский район, аэропорт Оренбург (Центральный) имени Ю.А. Гагарина', 3199.0, '2024-04-25 23:19:27.395848', 1, 1),
(2, 'Оренбург, проспект Победы, 13, корп. 3', 989.0, '2024-04-26 15:27:08.259635', 2, 1),
(NULL, 'Оренбург, проспект Победы, 13, корп. 3', 7077.0, '2024-04-26 17:17:40.354311', 1, 1);
CREATE TABLE IF NOT EXISTS order_details (
    id INT NOT NULL AUTO_INCREMENT,
    order_id INT,
    item_id INT,
    quantity INT,
    PRIMARY KEY (id),
    FOREIGN KEY(order_id) REFERENCES orders (id),
    FOREIGN KEY(item_id) REFERENCES dishes (id)
);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (1, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (1, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (2, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (2, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (3, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (3, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (4, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (4, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (5, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (5, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (6, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (6, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (7, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (7, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (8, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (8, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (9, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (9, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (10, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (10, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (11, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (11, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (12, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (12, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (13, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (13, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (14, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (14, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (15, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (15, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (16, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (17, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (18, 2, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (19, 1, 1);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (19, 2, 2);
INSERT INTO order_details (order_id, item_id, quantity) VALUES (19, 4, 1);

COMMIT;
