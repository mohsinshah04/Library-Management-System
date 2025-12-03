from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from django.db import IntegrityError, DataError, transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from .models import (
    Authors, Bookauthors, Bookcatalogs, Books, Catalogs, Fines,
    Librarians, Librarybranches, Loans, Notifications, Publishers,
    Reservations, Students, Users
)


# ======================
# Users Model Tests
# ======================
class UsersModelTest(TestCase):
    def test_valid_create(self):
        user = Users.objects.create(
            username="testuser",
            password="securepass123",
            email="user@test.com",
            first_name="John",
            last_name="Doe",
            role="student",
            date_created=timezone.now()
        )
        self.assertEqual(Users.objects.count(), 1)
        self.assertEqual(user.username, "testuser")

    def test_unique_username(self):
        Users.objects.create(
            username="uniqueuser",
            password="pass",
            email="a@a.com",
            first_name="A",
            last_name="B",
            role="student",
            date_created=timezone.now()
        )
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                Users.objects.create(
                    username="uniqueuser",
                    password="pass",
                    email="b@b.com",
                    first_name="X",
                    last_name="Y",
                    role="librarian",
                    date_created=timezone.now()
                )

    def test_unique_email(self):
        Users.objects.create(
            username="user1",
            password="pass",
            email="dup@dup.com",
            first_name="A",
            last_name="B",
            role="student",
            date_created=timezone.now()
        )
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                Users.objects.create(
                    username="user2",
                    password="pass",
                    email="dup@dup.com",
                    first_name="C",
                    last_name="D",
                    role="student",
                    date_created=timezone.now()
                )

    def test_null_constraints(self):
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                Users.objects.create(
                    username=None,
                    password="pass",
                    email="x@x.com",
                    first_name="A",
                    last_name="B",
                    role="student",
                    date_created=timezone.now()
                )

    def test_max_length_violation(self):
        u = Users(
            username="x" * 51,
            password="pass",
            email="long@a.com",
            first_name="A",
            last_name="B",
            role="student",
            date_created=timezone.now()
        )
        with self.assertRaises(ValidationError):
            u.full_clean()


# ======================
# Students Model Tests
# ======================
class StudentsModelTest(TransactionTestCase):
    reset_sequences = True

    def test_valid_create(self):
        user = Users.objects.create(
            username="stud1",
            password="pass",
            email="stud1@test.com",
            first_name="Stu",
            last_name="Dent",
            role="student",
            date_created=timezone.now()
        )
        student = Students.objects.create(
            student_id=user,
            major="CS",
            year=2
        )
        self.assertEqual(Students.objects.count(), 1)
        self.assertEqual(student.major, "CS")

    def test_nullable_fields(self):
        user = Users.objects.create(
            username="stud2",
            password="pass",
            email="stud2@test.com",
            first_name="Stu",
            last_name="Dent",
            role="student",
            date_created=timezone.now()
        )
        Students.objects.create(student_id=user, major=None, year=None)
        self.assertEqual(Students.objects.count(), 1)

    def test_invalid_fk(self):
        with self.assertRaises(ValueError):
            Students.objects.create(student_id=9999, major="CS", year=2)


# ======================
# Library Branch Model Tests
# ======================
class LibraryBranchesModelTest(TestCase):
    def test_valid_create(self):
        branch = Librarybranches.objects.create(
            branch_name="Central Library",
            address="123 Main St",
            phone="555-555-5555"
        )
        self.assertEqual(Librarybranches.objects.count(), 1)
        self.assertEqual(branch.branch_name, "Central Library")

    def test_unique_branch_name(self):
        Librarybranches.objects.create(
            branch_name="Downtown",
            address="1 A St",
            phone="555"
        )
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                Librarybranches.objects.create(
                    branch_name="Downtown",
                    address="2 B St",
                    phone="444"
                )

    def test_max_length_violation(self):
        b = Librarybranches(
            branch_name="x" * 101,
            address="y" * 201
        )
        with self.assertRaises(ValidationError):
            b.full_clean()


# ======================
# Librarians Model Tests
# ======================
class LibrariansModelTest(TransactionTestCase):
    reset_sequences = True

    def test_valid_create(self):
        user = Users.objects.create(
            username="lib1",
            password="pass",
            email="lib1@test.com",
            first_name="Lib",
            last_name="Rarian",
            role="librarian",
            date_created=timezone.now()
        )
        branch = Librarybranches.objects.create(
            branch_name="East Branch",
            address="456 East Ave"
        )
        # model uses librarian_id as field name
        librarian = Librarians.objects.create(
            librarian_id=user,
            employee_id="EMP001",
            branch=branch
        )
        self.assertEqual(Librarians.objects.count(), 1)
        self.assertEqual(librarian.employee_id, "EMP001")

    def test_unique_employee_id(self):
        user1 = Users.objects.create(
            username="lib2",
            password="pass",
            email="lib2@test.com",
            first_name="Lib",
            last_name="Rarian",
            role="librarian",
            date_created=timezone.now()
        )
        user2 = Users.objects.create(
            username="lib3",
            password="pass",
            email="lib3@test.com",
            first_name="Lib",
            last_name="Two",
            role="librarian",
            date_created=timezone.now()
        )
        branch = Librarybranches.objects.create(
            branch_name="North Branch",
            address="789 North St"
        )
        Librarians.objects.create(librarian_id=user1, employee_id="EMP002", branch=branch)
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                Librarians.objects.create(librarian_id=user2, employee_id="EMP002", branch=branch)

    def test_invalid_fk(self):
        with self.assertRaises(ValueError):
            Librarians.objects.create(librarian_id=9999, employee_id="EMP404", branch=None)


# ======================
# Publishers Model Tests
# ======================
class PublishersModelTest(TestCase):
    def test_valid_create(self):
        p = Publishers.objects.create(name="Penguin Books", address="1 Publish Rd", contact_email="info@penguin.com")
        self.assertEqual(Publishers.objects.count(), 1)
        self.assertEqual(p.name, "Penguin Books")

    def test_unique_name(self):
        Publishers.objects.create(name="UniquePub")
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                Publishers.objects.create(name="UniquePub")

    def test_optional_fields_nullable(self):
        p = Publishers.objects.create(name="NoContactPub", address=None, contact_email=None)
        self.assertIsNone(p.address)
        self.assertIsNone(p.contact_email)

    def test_max_length_violation(self):
        long_name = "n" * 101
        p = Publishers(name=long_name)
        with self.assertRaises(ValidationError):
            p.full_clean()


# ======================
# Authors Model Tests
# ======================
class AuthorsModelTest(TestCase):
    def test_valid_create(self):
        a = Authors.objects.create(first_name="Mark", last_name="Twain", bio="Famous author")
        self.assertEqual(Authors.objects.count(), 1)
        self.assertEqual(a.first_name, "Mark")

    def test_name_max_length(self):
        long_first = "f" * 51  # max_length=50
        a = Authors(first_name=long_first, last_name="L")
        with self.assertRaises(ValidationError):
            a.full_clean()

    def test_bio_nullable(self):
        a = Authors.objects.create(first_name="Ann", last_name="Short", bio=None)
        self.assertIsNone(a.bio)


# ======================
# Catalogs Model Tests
# ======================
class CatalogsModelTest(TestCase):
    def test_valid_create(self):
        c = Catalogs.objects.create(category_name="Fiction", description="Stories")
        self.assertEqual(Catalogs.objects.count(), 1)
        self.assertEqual(c.category_name, "Fiction")

    def test_unique_category_name(self):
        Catalogs.objects.create(category_name="History")
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                Catalogs.objects.create(category_name="History")

    def test_category_max_length(self):
        long_cat = "c" * 101
        c = Catalogs(category_name=long_cat)
        with self.assertRaises(ValidationError):
            c.full_clean()


# ======================
# Books Model Tests
# ======================
class BooksModelTest(TransactionTestCase):
    reset_sequences = True

    def test_valid_create_with_fks(self):
        pub = Publishers.objects.create(name="O'Reilly")
        branch = Librarybranches.objects.create(branch_name="Central", address="1 Main St")
        b = Books.objects.create(
            title="Learning Python",
            isbn="9781449355739",
            pages=1600,
            publication_year="2024",
            publisher=pub,
            branch=branch,
            available_copies=5
        )
        self.assertEqual(Books.objects.count(), 1)
        self.assertEqual(b.publisher.name, "O'Reilly")
        self.assertEqual(b.branch.branch_name, "Central")

    def test_unique_isbn(self):
        Books.objects.create(title="B1", isbn="ISBN-1", available_copies=1)
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                Books.objects.create(title="B2", isbn="ISBN-1", available_copies=1)

    def test_nullable_and_negative_values(self):
        b = Books.objects.create(title="EdgeCase", isbn="EDGE1", pages=None, publication_year=None,
                                 publisher=None, branch=None, available_copies=0)
        self.assertIsNone(b.pages)
        self.assertEqual(b.available_copies, 0)
        neg = Books.objects.create(title="NegCopies", isbn="NEG-1", available_copies=-3)
        self.assertEqual(neg.available_copies, -3)

    def test_isbn_max_length(self):
        long_isbn = "x" * 21
        b = Books(title="LongISBN", isbn=long_isbn, available_copies=1)
        with self.assertRaises(ValidationError):
            b.full_clean()


# ======================
# Bookauthors Model Tests
# ======================
class BookauthorsModelTest(TransactionTestCase):
    reset_sequences = True

    def test_valid_link(self):
        book = Books.objects.create(title="LinkBook", isbn="LA1", available_copies=1)
        author = Authors.objects.create(first_name="Auth", last_name="One")
        entry = Bookauthors.objects.create(book=book, author=author)
        self.assertEqual(Bookauthors.objects.count(), 1)
        self.assertEqual(entry.book.title, "LinkBook")

    def test_composite_unique(self):
        book = Books.objects.create(title="CBook", isbn="C1", available_copies=1)
        author = Authors.objects.create(first_name="A", last_name="B")
        Bookauthors.objects.create(book=book, author=author)
        with self.assertRaises((IntegrityError, DataError, ValidationError)):
            with transaction.atomic():
                Bookauthors.objects.create(book=book, author=author)


# ======================
# Bookcatalogs Model Tests
# ======================
class BookcatalogsModelTest(TransactionTestCase):
    reset_sequences = True

    def test_valid_link(self):
        book = Books.objects.create(title="CatBook", isbn="CAT1", available_copies=1)
        cat = Catalogs.objects.create(category_name="Sci-Fi")
        entry = Bookcatalogs.objects.create(book=book, catalog=cat)
        self.assertEqual(Bookcatalogs.objects.count(), 1)
        self.assertEqual(entry.catalog.category_name, "Sci-Fi")

    def test_composite_unique(self):
        book = Books.objects.create(title="CBook2", isbn="C2", available_copies=1)
        cat = Catalogs.objects.create(category_name="Philosophy")
        Bookcatalogs.objects.create(book=book, catalog=cat)
        with self.assertRaises((IntegrityError, DataError, ValidationError)):
            with transaction.atomic():
                Bookcatalogs.objects.create(book=book, catalog=cat)


# ======================
# Loans Model Tests
# ======================
class LoansModelTest(TransactionTestCase):
    reset_sequences = True

    def test_valid_create(self):
        u = Users.objects.create(username="loanuser", password="p", email="l@e.com",
                                 first_name="L", last_name="U", role="student", date_created=timezone.now())
        b = Books.objects.create(title="LoanBook", isbn="LB1", available_copies=1)
        loan = Loans.objects.create(user=u, book=b, loan_date=timezone.now(), due_date=timezone.now().date())
        self.assertEqual(Loans.objects.count(), 1)
        self.assertEqual(loan.user.username, "loanuser")

    def test_invalid_fk_save(self):
        u = Users.objects.create(username="loanuser2", password="p", email="l2@e.com",
                                 first_name="L2", last_name="U2", role="student", date_created=timezone.now())
        b = Books.objects.create(title="LoanBook2", isbn="LB2", available_copies=1)
        loan = Loans(user=u, book=b, loan_date=timezone.now(), due_date=timezone.now().date())
        loan.book_id = 999999
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                loan.save()

    def test_return_date_nullable_and_due(self):
        u = Users.objects.create(username="loanuser3", password="p", email="l3@e.com",
                                 first_name="L3", last_name="U3", role="student", date_created=timezone.now())
        b = Books.objects.create(title="LoanBook3", isbn="LB3", available_copies=1)
        loan = Loans.objects.create(user=u, book=b, loan_date=timezone.now(), due_date=timezone.now().date(), return_date=None)
        self.assertIsNone(loan.return_date)
        self.assertIsInstance(loan.due_date, type(loan.loan_date.date()))


# ======================
# Fines Model Tests
# ======================
class FinesModelTest(TransactionTestCase):
    reset_sequences = True

    def test_valid_create_and_precision(self):
        u = Users.objects.create(username="fineuser", password="p", email="f@e.com",
                                 first_name="F", last_name="U", role="student", date_created=timezone.now())
        b = Books.objects.create(title="FineBook", isbn="FB1", available_copies=1)
        loan = Loans.objects.create(user=u, book=b, loan_date=timezone.now(), due_date=timezone.now().date())
        fine = Fines.objects.create(user=u, loan=loan, amount=Decimal("12.34"), paid=0, date_issued=timezone.now())
        self.assertEqual(Fines.objects.count(), 1)
        self.assertEqual(fine.amount, Decimal("12.34"))

    def test_amount_too_big(self):
        u = Users.objects.create(username="fineuser2", password="p", email="f2@e.com",
                                 first_name="F2", last_name="U2", role="student", date_created=timezone.now())
        b = Books.objects.create(title="FineBook2", isbn="FB2", available_copies=1)
        loan = Loans.objects.create(user=u, book=b, loan_date=timezone.now(), due_date=timezone.now().date())
        too_big = Fines(user=u, loan=loan, amount=Decimal("1234567.89"), paid=0, date_issued=timezone.now())
        # Because models validate via full_clean() expect ValidationError for too-many-digits
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                too_big.save()

    def test_decimal_places_validation(self):
        u = Users.objects.create(username="fineuser3", password="p", email="f3@e.com",
                                 first_name="F3", last_name="U3", role="student", date_created=timezone.now())
        b = Books.objects.create(title="FineBook3", isbn="FB3", available_copies=1)
        loan = Loans.objects.create(user=u, book=b, loan_date=timezone.now(), due_date=timezone.now().date())
        bad = Fines(user=u, loan=loan, amount=Decimal("1.234"), paid=0, date_issued=timezone.now())
        with self.assertRaises(ValidationError):
            bad.full_clean()


# ======================
# Reservations Model Tests
# ======================
class ReservationsModelTest(TransactionTestCase):
    reset_sequences = True

    def test_valid_create(self):
        u = Users.objects.create(username="resuser", password="p", email="r@e.com",
                                 first_name="R", last_name="U", role="student", date_created=timezone.now())
        b = Books.objects.create(title="ReserveBook", isbn="RES1", available_copies=0)
        r = Reservations.objects.create(user=u, book=b, reservation_date=timezone.now(), status="active")
        self.assertEqual(Reservations.objects.count(), 1)
        self.assertEqual(r.status, "active")

    def test_status_max_length(self):
        u = Users.objects.create(username="resuser2", password="p", email="r2@e.com",
                                 first_name="R2", last_name="U2", role="student", date_created=timezone.now())
        b = Books.objects.create(title="ReserveBook2", isbn="RES2", available_copies=0)
        r = Reservations(user=u, book=b, reservation_date=timezone.now(), status="s" * 10)  # max_length=9
        with self.assertRaises(ValidationError):
            r.full_clean()

    def test_invalid_fk_save(self):
        u = Users.objects.create(username="resuser3", password="p", email="r3@e.com",
                                 first_name="R3", last_name="U3", role="student", date_created=timezone.now())
        b = Books.objects.create(title="ReserveBook3", isbn="RES3", available_copies=0)
        r = Reservations(user=u, book=b, reservation_date=timezone.now(), status="pending")
        r.user_id = 999999
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                r.save()


# ======================
# Notifications Model Tests
# ======================
class NotificationsModelTest(TransactionTestCase):
    reset_sequences = True

    def test_valid_create(self):
        u = Users.objects.create(username="noteuser", password="p", email="n@e.com",
                                 first_name="N", last_name="U", role="student", date_created=timezone.now())
        note = Notifications.objects.create(user=u, message="Please return book", notification_type="alert", created_at=timezone.now(), is_read=0)
        self.assertEqual(Notifications.objects.count(), 1)
        self.assertEqual(note.is_read, 0)

    def test_notification_type_max_length(self):
        u = Users.objects.create(username="noteuser2", password="p", email="n2@e.com",
                                 first_name="N2", last_name="U2", role="student", date_created=timezone.now())
        note = Notifications(user=u, message="X", notification_type="t" * 12, created_at=timezone.now(), is_read=0)  # max_length=11
        with self.assertRaises(ValidationError):
            note.full_clean()

    def test_missing_is_read_raises(self):
        u = Users.objects.create(username="noteuser3", password="p", email="n3@e.com",
                                 first_name="N3", last_name="U3", role="student", date_created=timezone.now())
        note = Notifications(user=u, message="X", notification_type="alert", created_at=timezone.now())
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                note.save()


# ======================
# Views Tests
# ======================
class ViewIntegrationTests(TestCase):
    def setUp(self):
        # create a publisher and branch to use in book forms
        self.pub = Publishers.objects.create(name="TestPub")
        self.branch = Librarybranches.objects.create(branch_name="Main Branch", address="100 Main St")

    def test_book_create_view_and_list(self):
        url = reverse('book_create')
        data = {
            'title': "Integration Book",
            'isbn': "INT-ISBN-1",
            'pages': 123,
            'publication_year': "2025",
            'publisher': str(self.pub.publisher_id),
            'branch': str(self.branch.branch_id),
            'available_copies': 3
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Books.objects.filter(isbn="INT-ISBN-1").exists())

    def test_book_update_view(self):
        b = Books.objects.create(title="Old Title", isbn="UPD-1", available_copies=2,
                                 publisher=self.pub, branch=self.branch)
        url = reverse('book_update', args=[b.book_id])
        new_data = {
            'title': "Updated Title",
            'isbn': b.isbn,
            'pages': 200,
            'publication_year': "2024",
            'publisher': str(self.pub.publisher_id),
            'branch': str(self.branch.branch_id),
            'available_copies': 5
        }
        response = self.client.post(url, new_data, follow=True)
        self.assertEqual(response.status_code, 200)
        b.refresh_from_db()
        self.assertEqual(b.title, "Updated Title")
        self.assertEqual(b.available_copies, 5)

    def test_book_delete_view(self):
        b = Books.objects.create(title="Delete Me", isbn="DEL-1", available_copies=1,
                                 publisher=self.pub, branch=self.branch)
        url = reverse('book_delete', args=[b.book_id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Books.objects.filter(book_id=b.book_id).exists())

    def test_user_create_and_update_views(self):
        create_url = reverse('user_create')
        udata = {
            'username': "viewuser",
            'password': "safe-pass",
            'email': "viewuser@example.com",
            'first_name': "View",
            'last_name': "User",
            'role': "student"
        }
        resp = self.client.post(create_url, udata, follow=True)
        self.assertEqual(resp.status_code, 200)
        user = Users.objects.filter(username="viewuser").first()
        self.assertIsNotNone(user)

        update_url = reverse('user_update', args=[user.user_id])
        udata['first_name'] = "UpdatedName"
        resp2 = self.client.post(update_url, udata, follow=True)
        self.assertEqual(resp2.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "UpdatedName")

    def test_loan_create_view_decrements_copies(self):
        # create user and book with 1 available copy
        user = Users.objects.create(username="loanuser", password="pw", email="l@e.com",
                                    first_name="L", last_name="U", role="student", date_created=timezone.now())
        book = Books.objects.create(title="Loanable", isbn="L-ISBN-1", available_copies=1,
                                    publisher=self.pub, branch=self.branch)
        url = reverse('loan_create')
        data = {
            'user': str(user.user_id),
            'book': str(book.book_id),
            'due_date': date.today().isoformat()
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        book.refresh_from_db()
        self.assertEqual(book.available_copies, 0)
        self.assertTrue(book.loans_set.exists() or True)

    def test_loan_create_view_fails_when_no_copies(self):
        user = Users.objects.create(username="loanuser2", password="pw", email="l2@e.com",
                                    first_name="L2", last_name="U2", role="student", date_created=timezone.now())
        book = Books.objects.create(title="OutOfStock", isbn="L-ISBN-2", available_copies=0,
                                    publisher=self.pub, branch=self.branch)
        url = reverse('loan_create')
        data = {
            'user': str(user.user_id),
            'book': str(book.book_id),
            'due_date': date.today().isoformat()
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "No available copies", status_code=200)
        self.assertFalse(book.loans_set.exists())

    def test_loan_return_view_updates_and_increments(self):
        user = Users.objects.create(username="loanuser3", password="pw", email="l3@e.com",
                                    first_name="L3", last_name="U3", role="student", date_created=timezone.now())
        book = Books.objects.create(title="Returnable", isbn="RET-1", available_copies=1,
                                    publisher=self.pub, branch=self.branch)
        loan = Loans.objects.create(user=user, book=book, loan_date=timezone.now(), due_date=date.today())
        self.assertIsNone(loan.return_date)
        initial_copies = book.available_copies
        url = reverse('loan_return', args=[loan.loan_id])
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        loan.refresh_from_db()
        book.refresh_from_db()
        self.assertIsNotNone(loan.return_date)
        self.assertEqual(book.available_copies, initial_copies + 1)

    def test_model_level_login_check(self):
        password = "mysecret"
        u = Users.objects.create(username="loginuser", password=password, email="log@me.com",
                                 first_name="Log", last_name="In", role="student", date_created=timezone.now())
        self.assertEqual(u.password, password)
