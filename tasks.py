from invoke import task
import os


@task
def init(c):
    """Initialize the Django project, nuking migrations and database before,
    and populating database after."""
    # Remove old database and migrations

    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
    if os.path.exists("catalog/migrations"):
        os.system("rm -rf catalog/migrations")
    os.makedirs("catalog/migrations", exist_ok=True)
    open("catalog/migrations/__init__.py", "a").close()

    # Hack path if run outside of venv
    os.environ["PATH"] = (
        f"{os.path.join(os.path.dirname(__file__), '.venv/bin')}:{os.environ['PATH']}"
    )

    # Make and apply migrations
    c.run("python manage.py makemigrations")
    c.run("python manage.py migrate")

    # Create users
    for name in ("admin", "librarian", "member"):
        email = f"{name}@localhost"
        password = f"{name}pass"
        function = "create_superuser" if name == "admin" else "create_user"
        c.run(
            f"echo \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.{function}('{name}', '{email}', '{password}')\" | python manage.py shell"
        )

    # Make librarian staff and add catalog permissions
    c.run(
        '''python manage.py shell -c "
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Author, Book, BookInstance, Genre, Language

# Get librarian user
User = get_user_model()
librarian = User.objects.get(username='librarian')
librarian.is_staff = True

# Get all permissions for catalog models
catalog_models = [Author, Book, BookInstance, Genre, Language]
for model in catalog_models:
    content_type = ContentType.objects.get_for_model(model)
    permissions = Permission.objects.filter(content_type=content_type)
    librarian.user_permissions.add(*permissions)

librarian.save()
"'''
    )

    #  Load initial data
    c.run("python manage.py loaddata initial_data.json")


@task
def clean(c):
    """Remove database and migrations"""
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
    if os.path.exists("catalog/migrations"):
        os.system("rm -rf catalog/migrations")


@task
def run(c):
    """Run the development server"""
    # Hack path
    os.environ["PATH"] = (
        f"{os.path.join(os.path.dirname(__file__), '.venv/bin')}:{os.environ['PATH']}"
    )
    c.run("python manage.py runserver")
