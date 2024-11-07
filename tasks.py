from invoke import task
import os

@task
def init(c):
    """Initialize the Django project"""
    # Remove old database and migrations
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
    if os.path.exists('catalog/migrations'):
        os.system('rm -rf catalog/migrations')
    os.makedirs('catalog/migrations', exist_ok=True)
    open('catalog/migrations/__init__.py', 'a').close()

    # Make and apply migrations
    c.run('python manage.py makemigrations')
    c.run('python manage.py migrate')

    # Create superuser
    c.run('echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser(\'admin\', \'admin@example.com\', \'adminpass\')" | python manage.py shell')

    # Load initial data
    c.run('python manage.py loaddata initial_data.json')

@task
def clean(c):
    """Remove database and migrations"""
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
    if os.path.exists('catalog/migrations'):
        os.system('rm -rf catalog/migrations')

@task
def run(c):
    """Run the development server"""
    c.run('python manage.py runserver')
