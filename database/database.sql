-- ============================================================
-- Database: stock_dashboard
-- ============================================================

CREATE DATABASE IF NOT EXISTS `stock_dashboard` 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `stock_dashboard`;

-- ============================================================
-- Table: users
-- ============================================================
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `is_active` BOOLEAN DEFAULT TRUE,
    `is_admin` BOOLEAN DEFAULT FALSE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_username` (`username`),
    INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: profiles
-- ============================================================
CREATE TABLE IF NOT EXISTS `profiles` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `user_id` INT(11) NOT NULL,
    `full_name` VARCHAR(100) NOT NULL,
    `mobile_number` VARCHAR(20),
    `profile_picture` VARCHAR(255) DEFAULT 'default.png',
    `bio` TEXT,
    `date_of_birth` DATE,
    `address` TEXT,
    `city` VARCHAR(50),
    `country` VARCHAR(50),
    `timezone` VARCHAR(50) DEFAULT 'UTC',
    `preferred_currency` VARCHAR(10) DEFAULT 'USD',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: login_history
-- ============================================================
CREATE TABLE IF NOT EXISTS `login_history` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `user_id` INT(11) NOT NULL,
    `ip_address` VARCHAR(45),
    `user_agent` TEXT,
    `login_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `logout_time` TIMESTAMP NULL,
    `session_id` VARCHAR(255),
    `is_successful` BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_login` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: stocks
-- ============================================================
CREATE TABLE IF NOT EXISTS `stocks` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `symbol` VARCHAR(20) NOT NULL UNIQUE,
    `company_name` VARCHAR(255) NOT NULL,
    `sector` VARCHAR(100),
    `industry` VARCHAR(100),
    `market_cap` BIGINT,
    `pe_ratio` DECIMAL(10,2),
    `dividend_yield` DECIMAL(10,2),
    `fifty_two_week_high` DECIMAL(15,2),
    `fifty_two_week_low` DECIMAL(15,2),
    `logo_url` VARCHAR(255),
    `description` TEXT,
    `website` VARCHAR(255),
    `ceo` VARCHAR(100),
    `employees` INT(11),
    `exchange` VARCHAR(50),
    `currency` VARCHAR(10) DEFAULT 'USD',
    `last_updated` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_symbol` (`symbol`),
    INDEX `idx_sector` (`sector`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: stock_prices (historical data)
-- ============================================================
CREATE TABLE IF NOT EXISTS `stock_prices` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `stock_id` INT(11) NOT NULL,
    `date` DATE NOT NULL,
    `open` DECIMAL(15,4),
    `high` DECIMAL(15,4),
    `low` DECIMAL(15,4),
    `close` DECIMAL(15,4),
    `volume` BIGINT,
    `adj_close` DECIMAL(15,4),
    PRIMARY KEY (`id`),
    FOREIGN KEY (`stock_id`) REFERENCES `stocks`(`id`) ON DELETE CASCADE,
    INDEX `idx_stock_date` (`stock_id`, `date`),
    UNIQUE KEY `uk_stock_date` (`stock_id`, `date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: watchlist
-- ============================================================
CREATE TABLE IF NOT EXISTS `watchlist` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `user_id` INT(11) NOT NULL,
    `stock_id` INT(11) NOT NULL,
    `is_favorite` BOOLEAN DEFAULT FALSE,
    `notes` TEXT,
    `price_alert` DECIMAL(15,4),
    `alert_enabled` BOOLEAN DEFAULT FALSE,
    `added_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`stock_id`) REFERENCES `stocks`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_user_stock` (`user_id`, `stock_id`),
    INDEX `idx_user_watchlist` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: portfolio
-- ============================================================
CREATE TABLE IF NOT EXISTS `portfolio` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `user_id` INT(11) NOT NULL,
    `stock_id` INT(11) NOT NULL,
    `quantity` DECIMAL(15,4) NOT NULL,
    `buy_price` DECIMAL(15,4) NOT NULL,
    `buy_date` DATE NOT NULL,
    `current_price` DECIMAL(15,4),
    `investment` DECIMAL(15,4),
    `current_value` DECIMAL(15,4),
    `profit_loss` DECIMAL(15,4),
    `profit_loss_percentage` DECIMAL(10,2),
    `notes` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`stock_id`) REFERENCES `stocks`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_user_stock_portfolio` (`user_id`, `stock_id`),
    INDEX `idx_user_portfolio` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: transactions
-- ============================================================
CREATE TABLE IF NOT EXISTS `transactions` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `user_id` INT(11) NOT NULL,
    `stock_id` INT(11) NOT NULL,
    `transaction_type` ENUM('BUY', 'SELL') NOT NULL,
    `quantity` DECIMAL(15,4) NOT NULL,
    `price` DECIMAL(15,4) NOT NULL,
    `total_amount` DECIMAL(15,4) NOT NULL,
    `commission` DECIMAL(15,4) DEFAULT 0,
    `transaction_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `notes` TEXT,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`stock_id`) REFERENCES `stocks`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_transaction` (`user_id`),
    INDEX `idx_transaction_date` (`transaction_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: news
-- ============================================================
CREATE TABLE IF NOT EXISTS `news` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `stock_id` INT(11),
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `content` LONGTEXT,
    `source` VARCHAR(100),
    `url` VARCHAR(500),
    `image_url` VARCHAR(500),
    `category` VARCHAR(50),
    `published_date` TIMESTAMP,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`stock_id`) REFERENCES `stocks`(`id`) ON DELETE CASCADE,
    INDEX `idx_news_stock` (`stock_id`),
    INDEX `idx_news_date` (`published_date`),
    INDEX `idx_news_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: notifications
-- ============================================================
CREATE TABLE IF NOT EXISTS `notifications` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `user_id` INT(11) NOT NULL,
    `type` VARCHAR(50) NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `message` TEXT NOT NULL,
    `is_read` BOOLEAN DEFAULT FALSE,
    `link` VARCHAR(500),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_notification` (`user_id`),
    INDEX `idx_notification_read` (`is_read`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: user_settings
-- ============================================================
CREATE TABLE IF NOT EXISTS `user_settings` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `user_id` INT(11) NOT NULL,
    `theme` VARCHAR(20) DEFAULT 'light',
    `dark_mode` BOOLEAN DEFAULT FALSE,
    `auto_refresh` BOOLEAN DEFAULT TRUE,
    `refresh_interval` INT(11) DEFAULT 30,
    `email_notifications` BOOLEAN DEFAULT TRUE,
    `price_alerts` BOOLEAN DEFAULT TRUE,
    `news_notifications` BOOLEAN DEFAULT TRUE,
    `language` VARCHAR(10) DEFAULT 'en',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_user_settings` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Insert Sample Data
-- ============================================================

-- Insert sample users (password: 'password123' hashed)
INSERT INTO `users` (`username`, `email`, `password_hash`, `is_admin`) VALUES
('john_doe', 'john@example.com', '$2b$12$KIXq3Z8kLJ5XQZ7H9vE4jO6VwZvHnKp7LQwRdEfTgYhUjKlMnOpQrS', FALSE),
('admin', 'admin@example.com', '$2b$12$KIXq3Z8kLJ5XQZ7H9vE4jO6VwZvHnKp7LQwRdEfTgYhUjKlMnOpQrS', TRUE),
('jane_smith', 'jane@example.com', '$2b$12$KIXq3Z8kLJ5XQZ7H9vE4jO6VwZvHnKp7LQwRdEfTgYhUjKlMnOpQrS', FALSE);

-- Insert profiles
INSERT INTO `profiles` (`user_id`, `full_name`, `mobile_number`) VALUES
(1, 'John Doe', '+1234567890'),
(2, 'Admin User', '+1234567891'),
(3, 'Jane Smith', '+1234567892');

-- Insert sample stocks
INSERT INTO `stocks` (`symbol`, `company_name`, `sector`, `industry`, `market_cap`, `pe_ratio`, `dividend_yield`, `fifty_two_week_high`, `fifty_two_week_low`, `logo_url`) VALUES
('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics', 2800000000000, 28.5, 0.55, 198.23, 143.90, 'https://logo.clearbit.com/apple.com'),
('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Content & Information', 1700000000000, 26.3, 0.00, 142.80, 93.00, 'https://logo.clearbit.com/google.com'),
('MSFT', 'Microsoft Corporation', 'Technology', 'Software', 2800000000000, 32.1, 0.92, 384.30, 245.00, 'https://logo.clearbit.com/microsoft.com'),
('AMZN', 'Amazon.com Inc.', 'Consumer Cyclical', 'Internet Retail', 1850000000000, 48.2, 0.00, 145.80, 83.00, 'https://logo.clearbit.com/amazon.com'),
('TSLA', 'Tesla Inc.', 'Consumer Cyclical', 'Auto Manufacturers', 780000000000, 75.6, 0.00, 278.00, 150.00, 'https://logo.clearbit.com/tesla.com'),
('META', 'Meta Platforms Inc.', 'Technology', 'Social Media', 900000000000, 32.8, 0.00, 358.00, 187.00, 'https://logo.clearbit.com/meta.com'),
('NVDA', 'NVIDIA Corporation', 'Technology', 'Semiconductors', 2200000000000, 92.5, 0.03, 950.00, 400.00, 'https://logo.clearbit.com/nvidia.com'),
('NFLX', 'Netflix Inc.', 'Technology', 'Entertainment', 250000000000, 48.3, 0.00, 485.00, 290.00, 'https://logo.clearbit.com/netflix.com');

-- Insert sample stock prices (last 30 days)
INSERT INTO `stock_prices` (`stock_id`, `date`, `open`, `high`, `low`, `close`, `volume`) 
SELECT 
    s.id,
    DATE_SUB(CURDATE(), INTERVAL n DAY) as date,
    ROUND(100 + (RAND() * 100), 2) as open,
    ROUND(110 + (RAND() * 90), 2) as high,
    ROUND(90 + (RAND() * 80), 2) as low,
    ROUND(100 + (RAND() * 100), 2) as close,
    FLOOR(1000000 + (RAND() * 50000000)) as volume
FROM stocks s
CROSS JOIN (
    SELECT 1 as n UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
    UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
    UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
    UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20
    UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25
    UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29 UNION SELECT 30
) days
ORDER BY s.id, date;

-- Insert sample watchlist
INSERT INTO `watchlist` (`user_id`, `stock_id`, `is_favorite`, `notes`) VALUES
(1, 1, TRUE, 'Apple - My favorite stock'),
(1, 2, FALSE, 'Google - Good potential'),
(1, 3, TRUE, 'Microsoft - Stable investment'),
(3, 4, TRUE, 'Amazon - E-commerce leader'),
(3, 5, FALSE, 'Tesla - EV pioneer');

-- Insert sample portfolio
INSERT INTO `portfolio` (`user_id`, `stock_id`, `quantity`, `buy_price`, `buy_date`, `current_price`, `investment`, `current_value`, `profit_loss`, `profit_loss_percentage`) VALUES
(1, 1, 10, 150.00, CURDATE() - INTERVAL 30 DAY, 175.50, 1500.00, 1755.00, 255.00, 17.00),
(1, 2, 5, 130.00, CURDATE() - INTERVAL 60 DAY, 142.30, 650.00, 711.50, 61.50, 9.46),
(1, 3, 8, 320.00, CURDATE() - INTERVAL 45 DAY, 335.80, 2560.00, 2686.40, 126.40, 4.94),
(3, 4, 15, 140.00, CURDATE() - INTERVAL 20 DAY, 145.20, 2100.00, 2178.00, 78.00, 3.71),
(3, 5, 20, 200.00, CURDATE() - INTERVAL 15 DAY, 210.75, 4000.00, 4215.00, 215.00, 5.38);

-- Insert sample transactions
INSERT INTO `transactions` (`user_id`, `stock_id`, `transaction_type`, `quantity`, `price`, `total_amount`, `commission`) VALUES
(1, 1, 'BUY', 10, 150.00, 1500.00, 5.00),
(1, 2, 'BUY', 5, 130.00, 650.00, 3.50),
(1, 3, 'BUY', 8, 320.00, 2560.00, 7.50),
(3, 4, 'BUY', 15, 140.00, 2100.00, 6.00),
(3, 5, 'BUY', 20, 200.00, 4000.00, 10.00);

-- Insert sample news
INSERT INTO `news` (`stock_id`, `title`, `description`, `source`, `category`, `published_date`) VALUES
(1, 'Apple Announces New Product Lineup', 'Apple Inc. revealed its latest product lineup at the annual developer conference.', 'TechCrunch', 'Technology', NOW() - INTERVAL 2 HOUR),
(NULL, 'Market Update: Tech Stocks Rally', 'Technology stocks led the market rally today with strong gains across the sector.', 'Reuters', 'Market', NOW() - INTERVAL 5 HOUR),
(3, 'Microsoft Cloud Revenue Surpasses Expectations', 'Microsoft\'s cloud division reported higher than expected revenue growth.', 'Bloomberg', 'Business', NOW() - INTERVAL 8 HOUR);

-- Insert sample user settings
INSERT INTO `user_settings` (`user_id`, `dark_mode`, `auto_refresh`, `refresh_interval`) VALUES
(1, FALSE, TRUE, 30),
(2, TRUE, TRUE, 60),
(3, FALSE, TRUE, 30);

-- Insert sample notifications
INSERT INTO `notifications` (`user_id`, `type`, `title`, `message`, `is_read`) VALUES
(1, 'INFO', 'Welcome to Stock Dashboard', 'Thank you for joining our platform!', FALSE),
(1, 'PRICE_ALERT', 'AAPL Price Alert', 'AAPL has reached your target price of $175', FALSE);

-- ============================================================
-- Indexes for better performance
-- ============================================================
CREATE INDEX idx_stocks_symbol ON stocks(symbol);
CREATE INDEX idx_stock_prices_date ON stock_prices(date);
CREATE INDEX idx_transactions_user_date ON transactions(user_id, transaction_date);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);
CREATE INDEX idx_news_published ON news(published_date DESC);

-- ============================================================
-- Views for reporting
-- ============================================================

-- View: User Portfolio Summary
CREATE OR REPLACE VIEW vw_portfolio_summary AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(DISTINCT p.stock_id) as total_stocks,
    SUM(p.investment) as total_investment,
    SUM(p.current_value) as total_current_value,
    SUM(p.profit_loss) as total_profit_loss,
    ROUND(AVG(p.profit_loss_percentage), 2) as avg_return_percentage
FROM users u
LEFT JOIN portfolio p ON u.id = p.user_id
GROUP BY u.id, u.username;

-- View: Market Summary
CREATE OR REPLACE VIEW vw_market_summary AS
SELECT 
    s.sector,
    COUNT(*) as total_stocks,
    ROUND(AVG(sp.close), 2) as avg_price,
    ROUND(SUM(sp.volume), 0) as total_volume
FROM stocks s
JOIN stock_prices sp ON s.id = sp.stock_id
WHERE sp.date = (SELECT MAX(date) FROM stock_prices)
GROUP BY s.sector;

-- ============================================================
-- Triggers for automatic calculations
-- ============================================================

-- Trigger: Update portfolio calculations on insert/update
DELIMITER //
CREATE TRIGGER trg_calculate_portfolio_values
BEFORE INSERT ON portfolio
FOR EACH ROW
BEGIN
    SET NEW.investment = NEW.quantity * NEW.buy_price;
    SET NEW.current_value = NEW.quantity * COALESCE(NEW.current_price, NEW.buy_price);
    SET NEW.profit_loss = NEW.current_value - NEW.investment;
    SET NEW.profit_loss_percentage = (NEW.profit_loss / NEW.investment) * 100;
END//
DELIMITER ;

-- ============================================================
-- Sample queries for testing
-- ============================================================

-- Get user portfolio summary
SELECT * FROM vw_portfolio_summary WHERE user_id = 1;

-- Get market summary
SELECT * FROM vw_market_summary;

-- Get top gaining stocks
SELECT 
    s.symbol,
    s.company_name,
    sp.close as current_price,
    LAG(sp.close) OVER (PARTITION BY s.id ORDER BY sp.date) as prev_close,
    ROUND(((sp.close - LAG(sp.close) OVER (PARTITION BY s.id ORDER BY sp.date)) / LAG(sp.close) OVER (PARTITION BY s.id ORDER BY sp.date)) * 100, 2) as gain_percentage
FROM stocks s
JOIN stock_prices sp ON s.id = sp.stock_id
WHERE sp.date = (SELECT MAX(date) FROM stock_prices)
ORDER BY gain_percentage DESC
LIMIT 5;