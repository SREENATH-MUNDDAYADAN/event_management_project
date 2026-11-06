CREATE DATABASE IF NOT EXISTS event_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE event_management;
CREATE TABLE IF NOT EXISTS users (
 user_id INT AUTO_INCREMENT PRIMARY KEY, full_name VARCHAR(100) NOT NULL,
 email VARCHAR(150) NOT NULL UNIQUE, phone VARCHAR(25), password_hash VARCHAR(255) NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS admins (
 admin_id INT AUTO_INCREMENT PRIMARY KEY, admin_name VARCHAR(100) NOT NULL,
 email VARCHAR(150) NOT NULL UNIQUE, password_hash VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
 event_id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL,
 event_name VARCHAR(150) NOT NULL, category VARCHAR(80) NOT NULL,
 description TEXT, event_date DATE NOT NULL, event_time TIME,
 venue VARCHAR(150) NOT NULL, organizer_name VARCHAR(100), contact_number VARCHAR(25),
 expected_participants INT DEFAULT 0, status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
 submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, approved_by INT NULL,
 approval_date DATETIME NULL, rejection_reason VARCHAR(255) NULL,
 FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
 FOREIGN KEY (approved_by) REFERENCES admins(admin_id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS venues (
 venue_id INT AUTO_INCREMENT PRIMARY KEY, venue_name VARCHAR(150) UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS venue_edges (
 edge_id INT AUTO_INCREMENT PRIMARY KEY, venue_from INT NOT NULL, venue_to INT NOT NULL,
 UNIQUE KEY unique_edge(venue_from, venue_to),
 FOREIGN KEY (venue_from) REFERENCES venues(venue_id) ON DELETE CASCADE,
 FOREIGN KEY (venue_to) REFERENCES venues(venue_id) ON DELETE CASCADE
);
-- Create first admin through the application's /setup-admin route, then remove/disable that route for deployment.
