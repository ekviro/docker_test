-- Создаем таблицу пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создаем таблицу адресов
CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    country VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    street VARCHAR(100) NOT NULL,
    house_number VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Вставляем тестовые данные
INSERT INTO users (username, email, full_name) VALUES
('ivanov', 'ivanov@example.com', 'Иван Иванов'),
('petrov', 'petrov@example.com', 'Петр Петров'),
('sidorova', 'sidorova@example.com', 'Мария Сидорова')
ON CONFLICT (username) DO NOTHING;

INSERT INTO addresses (user_id, country, city, street, house_number) VALUES
(1, 'Россия', 'Москва', 'Тверская', '10'),
(1, 'Россия', 'Санкт-Петербург', 'Невский проспект', '25'),
(2, 'Россия', 'Екатеринбург', 'Ленина', '5'),
(3, 'Россия', 'Казань', 'Баумана', '15')
ON CONFLICT DO NOTHING;