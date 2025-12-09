from django.db import models

# -----------------------
# USERS
# -----------------------
class Users(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("librarian", "Librarian"),
        ("administrator", "Administrator"),
    ]

    user_id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    role = models.CharField(max_length=13, choices=ROLE_CHOICES, null=False)

    date_created = models.DateTimeField()

    class Meta:
        db_table = "users"
        app_label = "app"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# -----------------------
# AUTHORS
# -----------------------
class Authors(models.Model):
    author_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    bio = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "authors"
        app_label = "app"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# -----------------------
# CATALOGS
# -----------------------
class Catalogs(models.Model):
    catalog_id = models.AutoField(primary_key=True)
    category_name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "catalogs"
        app_label = "app"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# -----------------------
# PUBLISHERS
# -----------------------
class Publishers(models.Model):
    publisher_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    address = models.CharField(max_length=200, blank=True, null=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "publishers"
        app_label = "app"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# -----------------------
# LIBRARY BRANCHES
# -----------------------
class Librarybranches(models.Model):
    branch_id = models.AutoField(primary_key=True)
    branch_name = models.CharField(unique=True, max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = "librarybranches"
        app_label = "app"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# -----------------------
# BOOKS
# -----------------------
class Books(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150)
    isbn = models.CharField(unique=True, max_length=20)
    pages = models.IntegerField(blank=True, null=True)
    publication_year = models.CharField(max_length=4, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    publisher = models.ForeignKey(Publishers, on_delete=models.CASCADE, blank=True, null=True)
    branch = models.ForeignKey(Librarybranches, on_delete=models.CASCADE, blank=True, null=True)

    available_copies = models.IntegerField()
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "books"
        app_label = "app"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# -----------------------
# MANY-TO-MANY FIX FOR BOOKAUTHORS
# -----------------------
class Bookauthors(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    author = models.ForeignKey(Authors, on_delete=models.CASCADE)

    class Meta:
        db_table = "bookauthors"
        app_label = "app"
        unique_together = ("book", "author")


# -----------------------
# MANY-TO-MANY FIX FOR BOOKCATALOGS
# -----------------------
class Bookcatalogs(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    catalog = models.ForeignKey(Catalogs, on_delete=models.CASCADE)

    class Meta:
        db_table = "bookcatalogs"
        app_label = "app"
        unique_together = ("book", "catalog")


# -----------------------
# STUDENTS (One-to-One)
# -----------------------
class Students(models.Model):
    student_id = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column="student_id",
        related_name="student_profile",
    )
    major = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "students"
        app_label = "app"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# -----------------------
# LIBRARIANS (One-to-One)
# -----------------------
class Librarians(models.Model):
    librarian_id = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column="librarian_id",
        related_name="librarian_profile",
    )
    employee_id = models.CharField(unique=True, max_length=20)
    branch = models.ForeignKey(Librarybranches, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = "librarians"
        app_label = "app"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# -----------------------
# LOANS
# -----------------------
class Loans(models.Model):
    loan_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    loan_date = models.DateTimeField()
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "loans"
        app_label = "app"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# -----------------------
# FINES
# -----------------------
class Fines(models.Model):
    fine_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    loan = models.ForeignKey(Loans, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=6, decimal_places=2)

    paid = models.IntegerField()

    date_issued = models.DateTimeField()

    class Meta:
        db_table = "fines"
        app_label = "app"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# -----------------------
# NOTIFICATIONS
# -----------------------
class Notifications(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=11)
    created_at = models.DateTimeField()
    is_read = models.IntegerField()

    class Meta:
        db_table = "notifications"
        app_label = "app"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# -----------------------
# RESERVATIONS
# -----------------------
class Reservations(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    reservation_date = models.DateTimeField()
    status = models.CharField(max_length=9)

    class Meta:
        db_table = "reservations"
        app_label = "app"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
