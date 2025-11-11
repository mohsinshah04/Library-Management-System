# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Authors(models.Model):
    author_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    bio = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'authors'


class Bookauthors(models.Model):
    book = models.ForeignKey('Books', models.DO_NOTHING, primary_key=True)
    author = models.ForeignKey('Authors', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'bookauthors'
        unique_together = (('book', 'author'),)


class Bookcatalogs(models.Model):
    book = models.ForeignKey('Books', models.DO_NOTHING, primary_key=True)
    catalog = models.ForeignKey('Catalogs', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'bookcatalogs'
        unique_together = (('book', 'catalog'),)


class Books(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150)
    isbn = models.CharField(unique=True, max_length=20)
    pages = models.IntegerField(blank=True, null=True)
    publication_year = models.TextField(blank=True, null=True)  # This field type is a guess.
    publisher = models.ForeignKey('Publishers', models.DO_NOTHING, blank=True, null=True)
    branch = models.ForeignKey('Librarybranches', models.DO_NOTHING, blank=True, null=True)
    available_copies = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'books'


class Catalogs(models.Model):
    catalog_id = models.AutoField(primary_key=True)
    category_name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'catalogs'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Fines(models.Model):
    fine_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    loan = models.ForeignKey('Loans', models.DO_NOTHING)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    paid = models.IntegerField()
    date_issued = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'fines'


class Librarians(models.Model):
    librarian = models.OneToOneField('Users', models.DO_NOTHING, primary_key=True)
    employee_id = models.CharField(unique=True, max_length=20)
    branch = models.ForeignKey('Librarybranches', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'librarians'


class Librarybranches(models.Model):
    branch_id = models.AutoField(primary_key=True)
    branch_name = models.CharField(unique=True, max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'librarybranches'


class Loans(models.Model):
    loan_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    book = models.ForeignKey(Books, models.DO_NOTHING)
    loan_date = models.DateTimeField()
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'loans'


class Notifications(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    message = models.TextField()
    notification_type = models.CharField(max_length=11)
    created_at = models.DateTimeField()
    is_read = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'notifications'


class Publishers(models.Model):
    publisher_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    address = models.CharField(max_length=200, blank=True, null=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'publishers'


class Reservations(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    book = models.ForeignKey(Books, models.DO_NOTHING)
    reservation_date = models.DateTimeField()
    status = models.CharField(max_length=9)

    class Meta:
        managed = False
        db_table = 'reservations'


class Students(models.Model):
    student = models.OneToOneField('Users', models.DO_NOTHING, primary_key=True)
    major = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'students'


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=9)
    date_created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'users'
