import os
import sys
import subprocess

def run_server(port=8000):
    """Run the development server"""
    try:
        subprocess.run([sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{port}'])
    except KeyboardInterrupt:
        print('\nServer stopped')

def make_migrations():
    """Make database migrations"""
    subprocess.run([sys.executable, 'manage.py', 'makemigrations'])

def migrate():
    """Apply database migrations"""
    subprocess.run([sys.executable, 'manage.py', 'migrate'])

def create_superuser():
    """Create a superuser account"""
    subprocess.run([sys.executable, 'manage.py', 'createsuperuser'])

def collect_static():
    """Collect static files"""
    subprocess.run([sys.executable, 'manage.py', 'collectstatic'])

def shell():
    """Open Django shell"""
    subprocess.run([sys.executable, 'manage.py', 'shell'])

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'server':
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
            run_server(port)
        elif command == 'makemigrations':
            make_migrations()
        elif command == 'migrate':
            migrate()
        elif command == 'superuser':
            create_superuser()
        elif command == 'static':
            collect_static()
        elif command == 'shell':
            shell()
        else:
            print(f'Unknown command: {command}')
    else:
        print('Available commands:')
        print('  server [port]    - Run development server (default port: 8000)')
        print('  makemigrations  - Create database migrations')
        print('  migrate         - Apply database migrations')
        print('  superuser       - Create superuser account')
        print('  static          - Collect static files')
        print('  shell           - Open Django shell')