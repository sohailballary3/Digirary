-- Digirary Complete SQLite Database Schema
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS borrowings;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories Table
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    icon TEXT NOT NULL DEFAULT 'book'
);

-- Books Table
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    isbn TEXT,
    published_year INTEGER,
    summary TEXT,
    cover_gradient TEXT NOT NULL DEFAULT 'linear-gradient(135deg, #4f46e5, #06b6d4)',
    total_pages INTEGER DEFAULT 300,
    rating REAL DEFAULT 4.5,
    available BOOLEAN NOT NULL DEFAULT 1,
    featured BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT
);

-- Borrowings Table
CREATE TABLE borrowings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    borrow_date DATE NOT NULL,
    duration_days INTEGER NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'returned')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
);

-- Seed Default Admin User (Password: admin123)
-- IMPORTANT: User session is NOT active by default. User must log in manually.
INSERT INTO users (username, email, password_hash, is_admin) VALUES
(
    'admin',
    'admin@digirary.local',
    'scrypt:32768:8:1$wukKeO0x9oR2Gb0B$663a0490a358688a07066301e148c52ecd53bcf419ca6c6402c246ff9a65c21653cdac65502f4528f676a96761a2df2be3a221a8f48bd436c32ab6db0ceef58f',
    1
);

-- Seed Categories
INSERT INTO categories (name, slug, icon) VALUES 
    ('Technology & Coding', 'tech', 'code'),
    ('Science & Nature', 'science', 'atom'),
    ('Philosophy & Mind', 'philosophy', 'compass'),
    ('Literature & Fiction', 'fiction', 'feather');

-- Seed Sample Digital Books
INSERT INTO books (title, author, category_id, isbn, published_year, summary, cover_gradient, total_pages, rating, available, featured) VALUES
(
    'Designing Data-Intensive Applications',
    'Martin Kleppmann',
    1,
    '978-1449373320',
    2017,
    'The definitive guide to understanding storage engines, distributed consensus, data modeling, and reliable modern cloud architectures.',
    'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
    616,
    4.9,
    1,
    1
),
(
    'Clean Code: A Handbook of Agile Craftsmanship',
    'Robert C. Martin',
    1,
    '978-0132350884',
    2008,
    'Essential principles, best practices, and code hygiene for writing readable, maintainable, and robust software.',
    'linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%)',
    464,
    4.7,
    1,
    1
),
(
    'Astrophysics for People in a Hurry',
    'Neil deGrasse Tyson',
    2,
    '978-0393609394',
    2017,
    'An illuminating, witty, and digestible journey through quantum mechanics, black holes, the Big Bang, and cosmic mysteries.',
    'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
    224,
    4.8,
    1,
    1
),
(
    'The Pragmatic Programmer',
    'David Thomas & Andrew Hunt',
    1,
    '978-0135957059',
    2019,
    'A timeless journey into career-long development mastery, software architecture, automation, and critical thinking.',
    'linear-gradient(135deg, #10b981 0%, #047857 100%)',
    352,
    4.8,
    1,
    0
),
(
    'Meditations',
    'Marcus Aurelius',
    3,
    '978-0140449334',
    2006,
    'Timeless private reflections of the Roman emperor on resilience, mindfulness, virtue, and tranquility under pressure.',
    'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    256,
    4.9,
    1,
    1
),
(
    'Sapiens: A Brief History of Humankind',
    'Yuval Noah Harari',
    2,
    '978-0062316097',
    2015,
    'How an insignificant ape became the master of planet Earth: explores biology, anthropology, and socio-economic systems.',
    'linear-gradient(135deg, #ec4899 0%, #be185d 100%)',
    464,
    4.7,
    1,
    0
),
(
    '1984',
    'George Orwell',
    4,
    '978-0451524935',
    1949,
    'A dystopian masterpiece that defined surveillance society, doublethink, and the fight for human freedom against authoritarian control.',
    'linear-gradient(135deg, #64748b 0%, #334155 100%)',
    328,
    4.8,
    1,
    1
),
(
    'Atomic Habits',
    'James Clear',
    3,
    '978-0735211292',
    2018,
    'An easy and proven framework to build good habits, break bad ones, and master the tiny behaviors that lead to remarkable results.',
    'linear-gradient(135deg, #14b8a6 0%, #0f766e 100%)',
    320,
    4.9,
    1,
    0
);
