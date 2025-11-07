USE mydb;

-- ===============================================================
-- USERS TABLE TESTS
-- ===============================================================

-- TEST 1.1: Insert valid users
INSERT INTO Users (username, password, email, first_name, last_name, role)
VALUES 
('student1', 'pass123', 'student1@email.com', 'Alice', 'Smith', 'student'),
('librarian1', 'libpass', 'librarian1@email.com', 'Bob', 'Brown', 'librarian');

SELECT * FROM Users; 
-- EXPECTED: 2 rows (student1 and librarian1)

-- TEST 1.2: Insert duplicate username
INSERT INTO Users (username, password, email, first_name, last_name, role)
VALUES ('student1', 'newpass', 'diff@email.com', 'Another', 'User', 'student');
-- EXPECTED: ERROR - Duplicate entry for username

-- TEST 1.3: Insert duplicate email
INSERT INTO Users (username, password, email, first_name, last_name, role)
VALUES ('student2', 'newpass', 'student1@email.com', 'Charlie', 'Doe', 'student');
-- EXPECTED: ERROR - Duplicate entry for email

-- TEST 1.4: Insert user with invalid role
INSERT INTO Users (username, password, email, first_name, last_name, role)
VALUES ('invalidrole', 'pass', 'invalid@email.com', 'Fake', 'Role', 'manager');
-- EXPECTED: ERROR - invalid value for ENUM('student','librarian')

-- ===============================================================
-- STUDENTS TABLE TESTS
-- ===============================================================

-- TEST 2.1: Insert student only if not already present
INSERT INTO Students (student_id, major, year)
SELECT u.user_id, 'Computer Science', 2
FROM Users AS u
WHERE u.username = 'student1' AND NOT EXISTS (SELECT 1 FROM Students AS s WHERE s.student_id = u.user_id);

SELECT u.user_id AS user_id, u.username, s.major, s.year
FROM Users AS u
LEFT JOIN Students AS s ON u.user_id = s.student_id
WHERE u.username = 'student1';
-- EXPECTED: one row for student1

-- TEST 2.2: Add student for a librarian
INSERT INTO Students (student_id, major, year)
SELECT user_id, 'History', 3 FROM Users WHERE username = 'librarian1';
-- EXPECTED: ERROR - Can't add because librarian1 exists but should not be a student (should fail foreign key)

-- TEST 2.3: Delete the user and check cascade delete
DELETE FROM Users WHERE username = 'student1';
SELECT * FROM Students;
-- EXPECTED: Student record for student1 deleted automatically

-- ===============================================================
-- LIBRARY BRANCHES AND LIBRARIANS
-- ===============================================================

-- TEST 3.1: Add a branch
INSERT INTO LibraryBranches (branch_name, address, phone)
VALUES ('Downtown Branch', '123 Main St', '555-1234');

SELECT * FROM LibraryBranches;

-- TEST 3.2: Duplicate branch name
INSERT INTO LibraryBranches (branch_name, address)
VALUES ('Downtown Branch', '456 Another Rd');
-- EXPECTED: ERROR - Duplicate branch name

-- TEST 3.3: Add librarian linked to branch
INSERT INTO Librarians (librarian_id, employee_id, branch_id)
SELECT user_id, 'EMP001', branch_id 
FROM Users, LibraryBranches 
WHERE username = 'librarian1' AND branch_name = 'Downtown Branch';

SELECT * FROM Librarians;
-- EXPECTED: Librarian assigned to Downtown Branch

-- TEST 3.4: Delete branch and verify librarian branch set to NULL
DELETE FROM LibraryBranches WHERE branch_name = 'Downtown Branch';
SELECT * FROM Librarians;
-- EXPECTED: Branch_id for librarian becomes NULL

-- ===============================================================
-- PUBLISHERS, AUTHORS, AND BOOKS
-- ===============================================================

-- TEST 4.1: Add a publisher
INSERT INTO Publishers (name, address, contact_email)
VALUES ('TechPress', '789 Industrial Rd', 'info@techpress.com');

-- TEST 4.2: Add authors
INSERT INTO Authors (first_name, last_name, bio)
VALUES 
('John', 'Miller', 'Tech writer and researcher'),
('Sara', 'Lee', 'Specializes in AI topics');

-- TEST 4.3: Add a book linked to publisher (publisher_id set)
INSERT INTO Books (title, isbn, pages, publication_year, publisher_id, available_copies)
VALUES ('Intro to Databases', 'ISBN123', 320, 2020, (SELECT publisher_id FROM Publishers WHERE name='TechPress'), 5);

SELECT * FROM Books;

-- TEST 4.4: Add duplicate ISBN (should fail)
INSERT INTO Books (title, isbn, available_copies)
VALUES ('Another Title', 'ISBN123', 2);
-- EXPECTED: ERROR - Duplicate entry for ISBN

-- TEST 4.5: Link authors to book
INSERT INTO BookAuthors (book_id, author_id)
SELECT b.book_id, a.author_id
FROM Books AS b, Authors AS a
WHERE b.isbn='ISBN123' AND a.last_name IN ('Miller','Lee');

SELECT * FROM BookAuthors;
-- EXPECTED: Two rows (one per author)

-- TEST 4.6: Delete author and check cascade
DELETE FROM Authors WHERE last_name='Lee';
SELECT * FROM BookAuthors;
-- EXPECTED: Only 1 author remains linked

-- ===============================================================
-- CATALOGS AND BOOK CATALOGS
-- ===============================================================

-- TEST 5.1: Add categories
INSERT INTO Catalogs (category_name, description)
VALUES ('Technology', 'Books on technology and computing');

-- TEST 5.2: Link book to category
INSERT INTO BookCatalogs (book_id, catalog_id)
SELECT b.book_id, c.catalog_id
FROM Books AS b, Catalogs AS c
WHERE b.isbn='ISBN123' AND c.category_name='Technology';

SELECT * FROM BookCatalogs;

SELECT b.book_id, b.isbn, b.title, c.catalog_id, c.category_name
FROM BookCatalogs AS bc
JOIN Books AS b ON bc.book_id = b.book_id
JOIN Catalogs AS c ON bc.catalog_id = c.catalog_id;
-- EXPECTED: One row linking book to Technology

-- TEST 5.3: Delete catalog and confirm cascade
DELETE FROM Catalogs WHERE category_name='Technology';
SELECT * FROM BookCatalogs;
-- EXPECTED: BookCatalog entry deleted

-- ===============================================================
-- LOANS
-- ===============================================================

-- TEST 6.1: Create new student and user for loan test
INSERT INTO Users (username, password, email, first_name, last_name, role)
VALUES ('loanstudent', 'pass', 'loanstudent@email.com', 'Jane', 'White', 'student');

INSERT INTO Students (student_id, major, year)
SELECT user_id, 'IT', 1 
FROM Users 
WHERE username='loanstudent';

-- TEST 6.2: Create a loan
INSERT INTO Loans (user_id, book_id, due_date)
SELECT u.user_id, b.book_id, DATE_ADD(CURDATE(), INTERVAL 7 DAY)
FROM Users AS u, Books AS b
WHERE u.username='loanstudent' AND b.isbn='ISBN123';

SELECT l.loan_id, CONCAT(u.first_name, ' ', u.last_name) AS student_name, b.title AS book_title, l.loan_date, l.due_date, l.return_date
FROM Loans AS l
JOIN Users AS u ON l.user_id = u.user_id
JOIN Books AS b ON l.book_id = b.book_id
WHERE u.username = 'loanstudent';
-- EXPECTED: One loan record

-- TEST 6.3: Try deleting a book with active loan
DELETE FROM Books WHERE isbn='ISBN123';
-- EXPECTED: ERROR - Cannot delete or update parent row (book still loaned)

-- ===============================================================
-- RESERVATIONS
-- ===============================================================

-- TEST 7.1: Create reservation
INSERT INTO Reservations (user_id, book_id)
SELECT u.user_id, b.book_id
FROM Users AS u, Books AS b
WHERE u.username='loanstudent' AND b.isbn='ISBN123';

SELECT * FROM Reservations;
-- EXPECTED: One reservation (status = 'active')

-- TEST 7.2: Invalid ENUM value
INSERT INTO Reservations (user_id, book_id, status)
SELECT u.user_id, b.book_id, 'waiting'
FROM Users AS u, Books AS b
WHERE u.username='loanstudent' AND b.isbn='ISBN123';
-- EXPECTED: ERROR - invalid ENUM value

-- ===============================================================
-- FINES
-- ===============================================================

-- TEST 8.1: Add fine linked to loan
INSERT INTO Fines (user_id, loan_id, amount, paid)
SELECT u.user_id, l.loan_id, 15.00, 0 
FROM Users AS u, Loans AS l 
WHERE u.username='loanstudent';

SELECT * FROM Fines;
-- EXPECTED: Fine created

-- TEST 8.2: Delete loan and check cascade delete for fine
DELETE FROM Loans 
WHERE user_id=(SELECT user_id FROM Users WHERE username='loanstudent');

SELECT * FROM Fines;
-- EXPECTED: Fine record deleted

-- ===============================================================
-- NOTIFICATIONS
-- ===============================================================

-- TEST 9.1: Add notification
INSERT INTO Notifications (user_id, message, notification_type)
SELECT user_id, 'Book due soon', 'overdue'
FROM Users
WHERE username='loanstudent';

SELECT * FROM Notifications;

-- TEST 9.2: Invalid ENUM for notification_type
INSERT INTO Notifications (user_id, message, notification_type)
SELECT user_id, 'Invalid test', 'alert'
FROM Users
WHERE username='loanstudent';
-- EXPECTED: ERROR - invalid ENUM value

-- TEST 9.3: Delete user and confirm cascade delete for notifications
DELETE FROM Users WHERE username='loanstudent';
SELECT * FROM Notifications;
-- EXPECTED: Notification deleted automatically

-- ===============================================================
-- CLEANUP
-- ===============================================================

DELETE FROM Users WHERE username='librarian1';
DELETE FROM Publishers;
DELETE FROM Books;
DELETE FROM Authors;
DELETE FROM LibraryBranches;
DELETE FROM Catalogs;
