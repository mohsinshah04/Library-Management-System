from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError, DataError, transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import (
    AuthGroup, AuthPermission, AuthUser, AuthGroupPermissions, AuthUserGroups,
    AuthUserUserPermissions, Authors, Bookauthors, Bookcatalogs, Books, Catalogs,
    DjangoAdminLog, DjangoContentType, DjangoMigrations, DjangoSession, Fines,
    Librarians, Librarybranches, Loans, Notifications, Publishers, Reservations,
    Students, Users
)

# ======================
# Users Model Tests
# ======================

class UsersModelTest(TestCase):
    # Tests valid creation of a user
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

    # Tests that username must be unique
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
        with self.assertRaises(IntegrityError):
            Users.objects.create(
                username="uniqueuser",
                password="pass",
                email="b@b.com",
                first_name="X",
                last_name="Y",
                role="librarian",
                date_created=timezone.now()
            )

    # Tests that email must be unique
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
        with self.assertRaises(IntegrityError):
            Users.objects.create(
                username="user2",
                password="pass",
                email="dup@dup.com",
                first_name="C",
                last_name="D",
                role="student",
                date_created=timezone.now()
            )

    # Tests that null violation occurs on required fields
    def test_null_constraints(self):
        with self.assertRaises(IntegrityError):
            Users.objects.create(
                username=None,
                password="pass",
                email="x@x.com",
                first_name="A",
                last_name="B",
                role="student",
                date_created=timezone.now()
            )

    # Tests that overly long strings violate max_length
    def test_max_length_violation(self):
        with self.assertRaises(DataError):
            Users.objects.create(
                username="x" * 51,
                password="pass",
                email="long@a.com",
                first_name="A",
                last_name="B",
                role="student",
                date_created=timezone.now()
            )


# ======================
# Students Model Tests
# ======================

class StudentsModelTest(TestCase):
    # Tests valid creation of a student linked to a user
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
            student=user,
            major="CS",
            year=2
        )
        self.assertEqual(Students.objects.count(), 1)
        self.assertEqual(student.major, "CS")

    # Tests null constraints for major and year
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
        Students.objects.create(student=user, major=None, year=None)
        self.assertEqual(Students.objects.count(), 1)

    # Tests invalid foreign key (nonexistent user)
    def test_invalid_fk(self):
        with self.assertRaises(IntegrityError):
            Students.objects.create(student_id=9999, major="CS", year=2)


# ======================
# Library Branch Model Tests
# ======================

class LibraryBranchesModelTest(TestCase):
    # Tests valid creation of a branch
    def test_valid_create(self):
        branch = Librarybranches.objects.create(
            branch_name="Central Library",
            address="123 Main St",
            phone="555-555-5555"
        )
        self.assertEqual(Librarybranches.objects.count(), 1)
        self.assertEqual(branch.branch_name, "Central Library")

    # Tests branch_name uniqueness
    def test_unique_branch_name(self):
        Librarybranches.objects.create(
            branch_name="Downtown",
            address="1 A St",
            phone="555"
        )
        with self.assertRaises(IntegrityError):
            Librarybranches.objects.create(
                branch_name="Downtown",
                address="2 B St",
                phone="444"
            )

    # Tests max length violations
    def test_max_length_violation(self):
        with self.assertRaises(DataError):
            Librarybranches.objects.create(
                branch_name="x" * 101,
                address="y" * 201
            )


# ======================
# Librarians Model Tests
# ======================

class LibrariansModelTest(TestCase):
    # Tests valid librarian creation linked to user and branch
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
        librarian = Librarians.objects.create(
            librarian=user,
            employee_id="EMP001",
            branch=branch
        )
        self.assertEqual(Librarians.objects.count(), 1)
        self.assertEqual(librarian.employee_id, "EMP001")

    # Tests employee_id uniqueness
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
        Librarians.objects.create(librarian=user1, employee_id="EMP002", branch=branch)
        with self.assertRaises(IntegrityError):
            Librarians.objects.create(librarian=user2, employee_id="EMP002", branch=branch)

    # Tests invalid foreign key references
    def test_invalid_fk(self):
        with self.assertRaises(IntegrityError):
            Librarians.objects.create(librarian_id=9999, employee_id="EMP404", branch=None)


# ======================
# Publishers Model Tests
# ======================

class PublishersModelTest(TestCase):
    # Tests valid creation of a publisher
    def test_valid_create(self):
        p = Publishers.objects.create(name="Penguin Books", address="1 Publish Rd", contact_email="info@penguin.com")
        self.assertEqual(Publishers.objects.count(), 1)
        self.assertEqual(p.name, "Penguin Books")

    # Tests unique name constraint for publishers
    def test_unique_name(self):
        Publishers.objects.create(name="UniquePub")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Publishers.objects.create(name="UniquePub")

    # Tests optional fields can be null
    def test_optional_fields_nullable(self):
        p = Publishers.objects.create(name="NoContactPub", address=None, contact_email=None)
        self.assertIsNone(p.address)
        self.assertIsNone(p.contact_email)

    # Tests max_length violations for name and contact_email (name max_length=100)
    def test_max_length_violation(self):
        long_name = "n" * 101
        p = Publishers(name=long_name)
        with self.assertRaises(ValidationError):
            p.full_clean()


# ======================
# Authors Model Tests
# ======================

class AuthorsModelTest(TestCase):
    # Tests valid creation of an author
    def test_valid_create(self):
        a = Authors.objects.create(first_name="Mark", last_name="Twain", bio="Famous author")
        self.assertEqual(Authors.objects.count(), 1)
        self.assertEqual(a.first_name, "Mark")

    # Tests max_length enforcement on names (max_length=50)
    def test_name_max_length(self):
        long_first = "f" * 51
        a = Authors(first_name=long_first, last_name="L")
        with self.assertRaises(ValidationError):
            a.full_clean()

    # Tests that bio can be null or blank
    def test_bio_nullable(self):
        a = Authors.objects.create(first_name="Ann", last_name="Short", bio=None)
        self.assertIsNone(a.bio)


# ======================
# Catalogs Model Tests
# ======================

class CatalogsModelTest(TestCase):
    # Tests valid creation of a catalog category
    def test_valid_create(self):
        c = Catalogs.objects.create(category_name="Fiction", description="Stories")
        self.assertEqual(Catalogs.objects.count(), 1)
        self.assertEqual(c.category_name, "Fiction")

    # Tests unique constraint on category_name
    def test_unique_category_name(self):
        Catalogs.objects.create(category_name="History")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Catalogs.objects.create(category_name="History")

    # Tests max_length violation for category_name (max_length=100)
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

    # Tests valid book creation with publisher and branch
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

    # Tests unique ISBN constraint
    def test_unique_isbn(self):
        Books.objects.create(title="B1", isbn="ISBN-1", available_copies=1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Books.objects.create(title="B2", isbn="ISBN-1", available_copies=1)

    # Tests nullable fields and negative numeric values
    def test_nullable_and_negative_values(self):
        b = Books.objects.create(title="EdgeCase", isbn="EDGE1", pages=None, publication_year=None,
                                 publisher=None, branch=None, available_copies=0)
        self.assertIsNone(b.pages)
        self.assertEqual(b.available_copies, 0)
        # negative copies allowed by model (no validator) — should persist unless DB restriction exists
        neg = Books.objects.create(title="NegCopies", isbn="NEG-1", available_copies=-3)
        self.assertEqual(neg.available_copies, -3)

    # Tests isbn max_length enforcement (max_length=20)
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

    # Tests linking a book to an author
    def test_valid_link(self):
        book = Books.objects.create(title="LinkBook", isbn="LA1", available_copies=1)
        author = Authors.objects.create(first_name="Auth", last_name="One")
        entry = Bookauthors.objects.create(book=book, author=author)
        self.assertEqual(Bookauthors.objects.count(), 1)
        self.assertEqual(entry.book.title, "LinkBook")

    # Tests composite-uniqueness enforcement for book-author pairs
    def test_composite_unique(self):
        book = Books.objects.create(title="CBook", isbn="C1", available_copies=1)
        author = Authors.objects.create(first_name="A", last_name="B")
        Bookauthors.objects.create(book=book, author=author)
        with self.assertRaises((IntegrityError, DataError)):
            with transaction.atomic():
                Bookauthors.objects.create(book=book, author=author)


# ======================
# Bookcatalogs Model Tests
# ======================

class BookcatalogsModelTest(TransactionTestCase):
    reset_sequences = True

    # Tests linking a book to a catalog
    def test_valid_link(self):
        book = Books.objects.create(title="CatBook", isbn="CAT1", available_copies=1)
        cat = Catalogs.objects.create(category_name="Sci-Fi")
        entry = Bookcatalogs.objects.create(book=book, catalog=cat)
        self.assertEqual(Bookcatalogs.objects.count(), 1)
        self.assertEqual(entry.catalog.category_name, "Sci-Fi")

    # Tests composite-uniqueness enforcement for book-catalog pairs
    def test_composite_unique(self):
        book = Books.objects.create(title="CBook2", isbn="C2", available_copies=1)
        cat = Catalogs.objects.create(category_name="Philosophy")
        Bookcatalogs.objects.create(book=book, catalog=cat)
        with self.assertRaises((IntegrityError, DataError)):
            with transaction.atomic():
                Bookcatalogs.objects.create(book=book, catalog=cat)


# ======================
# Loans Model Tests
# ======================

class LoansModelTest(TransactionTestCase):
    reset_sequences = True

    # Tests valid loan creation
    def test_valid_create(self):
        u = Users.objects.create(username="loanuser", password="p", email="l@e.com",
                                 first_name="L", last_name="U", role="student", date_created=timezone.now())
        b = Books.objects.create(title="LoanBook", isbn="LB1", available_copies=1)
        loan = Loans.objects.create(user=u, book=b, loan_date=timezone.now(), due_date=timezone.now().date())
        self.assertEqual(Loans.objects.count(), 1)
        self.assertEqual(loan.user.username, "loanuser")

    # Tests invalid FK for book/user on save
    def test_invalid_fk_save(self):
        u = Users.objects.create(username="loanuser2", password="p", email="l2@e.com",
                                 first_name="L2", last_name="U2", role="student", date_created=timezone.now())
        b = Books.objects.create(title="LoanBook2", isbn="LB2", available_copies=1)
        loan = Loans(user=u, book=b, loan_date=timezone.now(), due_date=timezone.now().date())
        loan.book_id = 999999  # non-existent
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                loan.save()

    # Tests return_date nullable and due_date logical placement
    def test_return_date_nullable_and_due(self):
        u = Users.objects.create(username="loanuser3", password="p", email="l3@e.com",
                                 first_name="L3", last_name="U3", role="student", date_created=timezone.now())
        b = Books.objects.create(title="LoanBook3", isbn="LB3", available_copies=1)
        loan = Loans.objects.create(user=u, book=b, loan_date=timezone.now(), due_date=timezone.now().date(), return_date=None)
        self.assertIsNone(loan.return_date)
        # business logic not enforced at model: due_date can be before loan_date; show as saved
        self.assertTrue(isinstance(loan.due_date, type(loan.loan_date.date())))


# ======================
# Fines Model Tests
# ======================

class FinesModelTest(TransactionTestCase):
    reset_sequences = True

    # Tests valid fine creation and decimal precision
    def test_valid_create_and_precision(self):
        u = Users.objects.create(username="fineuser", password="p", email="f@e.com",
                                 first_name="F", last_name="U", role="student", date_created=timezone.now())
        b = Books.objects.create(title="FineBook", isbn="FB1", available_copies=1)
        loan = Loans.objects.create(user=u, book=b, loan_date=timezone.now(), due_date=timezone.now().date())
        fine = Fines.objects.create(user=u, loan=loan, amount=Decimal("12.34"), paid=0, date_issued=timezone.now())
        self.assertEqual(Fines.objects.count(), 1)
        self.assertEqual(fine.amount, Decimal("12.34"))

    # Tests amount with too many digits triggers DB error
    def test_amount_too_big(self):
        u = Users.objects.create(username="fineuser2", password="p", email="f2@e.com",
                                 first_name="F2", last_name="U2", role="student", date_created=timezone.now())
        b = Books.objects.create(title="FineBook2", isbn="FB2", available_copies=1)
        loan = Loans.objects.create(user=u, book=b, loan_date=timezone.now(), due_date=timezone.now().date())
        too_big = Fines(user=u, loan=loan, amount=Decimal("1234567.89"), paid=0, date_issued=timezone.now())
        with self.assertRaises((DataError, IntegrityError)):
            with transaction.atomic():
                too_big.save()

    # Tests decimal places validation via full_clean
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

class ReservationsModelTest(TestCase):
    # Tests valid reservation creation
    def test_valid_create(self):
        u = Users.objects.create(username="resuser", password="p", email="r@e.com",
                                 first_name="R", last_name="U", role="student", date_created=timezone.now())
        b = Books.objects.create(title="ReserveBook", isbn="RES1", available_copies=0)
        r = Reservations.objects.create(user=u, book=b, reservation_date=timezone.now(), status="active")
        self.assertEqual(Reservations.objects.count(), 1)
        self.assertEqual(r.status, "active")

    # Tests status max_length enforcement via full_clean
    def test_status_max_length(self):
        u = Users.objects.create(username="resuser2", password="p", email="r2@e.com",
                                 first_name="R2", last_name="U2", role="student", date_created=timezone.now())
        b = Books.objects.create(title="ReserveBook2", isbn="RES2", available_copies=0)
        r = Reservations(user=u, book=b, reservation_date=timezone.now(), status="s" * 10)  # max_length=9
        with self.assertRaises(ValidationError):
            r.full_clean()

    # Tests invalid FK behaviour on save
    def test_invalid_fk_save(self):
        u = Users.objects.create(username="resuser3", password="p", email="r3@e.com",
                                 first_name="R3", last_name="U3", role="student", date_created=timezone.now())
        b = Books.objects.create(title="ReserveBook3", isbn="RES3", available_copies=0)
        r = Reservations(user=u, book=b, reservation_date=timezone.now(), status="pending")
        r.user_id = 999999
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                r.save()


# ======================
# Notifications Model Tests
# ======================

class NotificationsModelTest(TestCase):
    # Tests valid notification creation
    def test_valid_create(self):
        u = Users.objects.create(username="noteuser", password="p", email="n@e.com",
                                 first_name="N", last_name="U", role="student", date_created=timezone.now())
        note = Notifications.objects.create(user=u, message="Please return book", notification_type="alert", created_at=timezone.now(), is_read=0)
        self.assertEqual(Notifications.objects.count(), 1)
        self.assertEqual(note.is_read, 0)

    # Tests notification_type max_length validation
    def test_notification_type_max_length(self):
        u = Users.objects.create(username="noteuser2", password="p", email="n2@e.com",
                                 first_name="N2", last_name="U2", role="student", date_created=timezone.now())
        note = Notifications(user=u, message="X", notification_type="t" * 12, created_at=timezone.now(), is_read=0)  # max_length=11
        with self.assertRaises(ValidationError):
            note.full_clean()

    # Tests missing is_read causes IntegrityError at save (not nullable)
    def test_missing_is_read_raises(self):
        u = Users.objects.create(username="noteuser3", password="p", email="n3@e.com",
                                 first_name="N3", last_name="U3", role="student", date_created=timezone.now())
        note = Notifications(user=u, message="X", notification_type="alert", created_at=timezone.now())
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                note.save()


# ======================
# Auth Models Tests
# ======================

class AuthModelsTest(TransactionTestCase):
    reset_sequences = True

    # Tests AuthContentType unique_together constraint
    def test_content_type_unique(self):
        DjangoContentType.objects.create(app_label="appA", model="mA")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DjangoContentType.objects.create(app_label="appA", model="mA")

    # Tests AuthPermission unique_together constraint
    def test_auth_permission_unique(self):
        ct = DjangoContentType.objects.create(app_label="appB", model="mB")
        AuthPermission.objects.create(name="CanX", content_type=ct, codename="can_x")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AuthPermission.objects.create(name="Other", content_type=ct, codename="can_x")

    # Tests AuthGroup create and unique name
    def test_auth_group_unique(self):
        AuthGroup.objects.create(name="Admins")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AuthGroup.objects.create(name="Admins")

    # Tests AuthUser create and unique username
    def test_auth_user_create_and_unique(self):
        AuthUser.objects.create(username="authu", password="p", email="a@e.com", first_name="", last_name="", is_superuser=0, is_staff=0, is_active=1, date_joined=timezone.now())
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AuthUser.objects.create(username="authu", password="p", email="b@e.com", first_name="", last_name="", is_superuser=0, is_staff=0, is_active=1, date_joined=timezone.now())

    # Tests AuthUserGroups unique_together and linking
    def test_auth_user_groups_unique(self):
        ag = AuthGroup.objects.create(name="G1")
        au = AuthUser.objects.create(username="au1", password="p", email="au1@e.com", first_name="", last_name="", is_superuser=0, is_staff=0, is_active=1, date_joined=timezone.now())
        AuthUserGroups.objects.create(user=au, group=ag)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AuthUserGroups.objects.create(user=au, group=ag)

    # Tests AuthGroupPermissions unique_together
    def test_auth_group_permissions_unique(self):
        ag = AuthGroup.objects.create(name="G2")
        ct = DjangoContentType.objects.create(app_label="appC", model="mC")
        perm = AuthPermission.objects.create(name="Perm", content_type=ct, codename="perm_c")
        AuthGroupPermissions.objects.create(group=ag, permission=perm)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AuthGroupPermissions.objects.create(group=ag, permission=perm)

    # Tests AuthUserUserPermissions unique_together
    def test_auth_user_user_permissions_unique(self):
        au = AuthUser.objects.create(username="au2", password="p", email="au2@e.com", first_name="", last_name="", is_superuser=0, is_staff=0, is_active=1, date_joined=timezone.now())
        ct = DjangoContentType.objects.create(app_label="appD", model="mD")
        perm = AuthPermission.objects.create(name="Perm2", content_type=ct, codename="perm_d")
        AuthUserUserPermissions.objects.create(user=au, permission=perm)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AuthUserUserPermissions.objects.create(user=au, permission=perm)
