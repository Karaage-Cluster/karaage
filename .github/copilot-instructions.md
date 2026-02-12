# Karaage Project - GitHub Copilot Instructions

## Project Overview

Karaage is a cluster account management tool written in Python using the Django web framework. It manages users and projects in high-performance computing (HPC) clusters, storing data in various backends including LDAP, Active Directory, and databases.

### Key Features
- User and project management for HPC clusters
- LDAP/Active Directory integration for authentication
- Email notifications and auto account creation
- Application workflow for account requests and approvals
- Usage reporting per institute, project, or user
- Software usage tracking

## Technology Stack

- **Language**: Python 3.10+
- **Framework**: Django 4.x (targeting <5.2.0)
- **Package Manager**: uv (preferred), pip (fallback)
- **Databases**: PostgreSQL, MySQL, SQLite (for testing)
- **LDAP**: ldap3, python-tldap
- **Testing**: pytest, pytest-django, pytest-cov
- **Code Quality**: Black (formatter), Flake8 (linter), Ruff
- **Type Checking**: mypy with django-stubs

## Project Structure

```
karaage/
├── karaage/              # Main application code
│   ├── common/          # Common utilities and helpers
│   ├── institutes/      # Institute management
│   ├── machines/        # Machine/cluster management
│   ├── people/          # User/person management
│   ├── projects/        # Project management
│   ├── plugins/         # Plugin system
│   ├── tests/           # Test suite
│   ├── templates/       # Django templates
│   └── static/          # Static files (CSS, JS)
├── docs/                # Documentation (Sphinx)
├── conf/                # Configuration templates
├── sbin/                # System scripts
└── scripts/             # Utility scripts
```

## Development Workflow

### Setting Up Development Environment

1. **Install dependencies**:
   ```bash
   # Using uv (preferred)
   uv sync --all-extras --dev --group docs
   
   # Or using pip
   pip install -e .[dev,docs]
   ```

2. **System dependencies**:
   - `libcrack2-dev` - Required for password checking
   - `slapd` and `ldap-utils` - Required for LDAP testing

3. **Database setup**:
   ```bash
   ./manage.py migrate --settings=karaage.tests.settings
   ```

### Running Tests

- **All tests**:
  ```bash
  uv run pytest --cov=karaage
  # Or use the test script
  ./run_tests.sh
  ```

- **Specific test file**:
  ```bash
  uv run pytest karaage/tests/projects/test_models.py
  ```

- **With LDAP**:
  ```bash
  uv run python -m tldap.test.slapd python -m pytest --cov=karaage
  ```

### Code Quality

- **Format code with Black** (line length: 120):
  ```bash
  uv run black karaage
  ```

- **Check with Flake8**:
  ```bash
  uv run flake8 karaage
  ```

- **Type checking**:
  ```bash
  uv run mypy karaage
  ```

- **Check migrations**:
  ```bash
  ./manage.py makemigrations --settings=karaage.tests.settings --check --dry-run
  ```

## Code Style Guidelines

1. **Formatting**: Use Black with 120-character line length
2. **Linting**: Follow Flake8 rules (ignore W503, E741, E203)
3. **Imports**: Use isort with Black profile
4. **Type hints**: Add type hints where appropriate, use django-stubs
5. **Line length**: Maximum 120 characters
6. **Docstrings**: Use for public modules, functions, classes, and methods

## Testing Guidelines

1. **Framework**: Use pytest with pytest-django
2. **Database**: Tests use `@pytest.mark.django_db` decorator
3. **Fixtures**: Load test data from `fixtures/` directory or use factory-boy
4. **Settings**: Tests run with `karaage.tests.settings`
5. **Coverage**: Maintain or improve test coverage
6. **Test naming**: Use `test_*.py` or `*_test.py` patterns
7. **Test organization**: Mirror the application structure in `karaage/tests/`

### Common Test Patterns

```python
import pytest
from karaage.tests.factories import PersonFactory

@pytest.mark.django_db
class TestMyFeature:
    fixtures = ["test_karaage.json"]
    
    def test_something(self):
        # Test implementation
        pass
```

## Django-Specific Guidelines

1. **Settings**: Use `karaage.tests.settings` for tests, `dev_settings.py` for development
2. **Management commands**: Place in `management/commands/` directories
3. **Migrations**: Always check for migration conflicts before committing
4. **Static files**: Run `collectstatic` during deployment
5. **Templates**: Use Django template language, stored in `templates/` directories
6. **Models**: Follow Django ORM best practices
7. **Views**: Use class-based views where appropriate
8. **URLs**: Use path() or re_path() for URL patterns

## Common Commands

```bash
# Run development server
./manage.py runserver --settings=dev_settings

# Create superuser
./manage.py createsuperuser --settings=dev_settings

# Collect static files
./manage.py collectstatic --settings=karaage.tests.settings --noinput

# Run migrations
./manage.py migrate --settings=karaage.tests.settings

# Create migrations
./manage.py makemigrations --settings=karaage.tests.settings

# Run management command
kg-manage <command>
```

## CI/CD

- **GitHub Actions**: `.github/workflows/pythonapp.yml`
- **Tests run on**: Push, pull request, merge group
- **Database tests**: Both MySQL and PostgreSQL
- **Coverage**: Automatically reported via pytest-cov
- **Docker**: Builds and publishes to GitHub Container Registry

## Key Dependencies

- **Django**: Web framework (4.x)
- **ldap3**: LDAP client
- **python-tldap**: LDAP utilities
- **django-tables2**: Table rendering
- **django-filter**: Filtering support
- **bcrypt**: Password hashing
- **gunicorn**: WSGI server
- **whitenoise**: Static file serving
- **sentry-sdk**: Error tracking

## Important Notes

1. **License**: GPL 3.0+
2. **Copyright**: Copyright 2010-2017, The University of Melbourne and Brian May
3. **Security**: Never commit credentials or secrets
4. **Backwards compatibility**: Maintain compatibility with existing LDAP schemas
5. **Database migrations**: Test with both PostgreSQL and MySQL
6. **LDAP testing**: Some tests require a running LDAP server (uses tldap.test.slapd)

## Documentation

- User docs: https://karaage.readthedocs.org/projects/karaage-user/
- Admin docs: `docs/admin/`
- Build docs: `make -C docs/admin html`

## When Making Changes

1. Maintain backwards compatibility where possible
2. Update relevant documentation
3. Add or update tests for new features
4. Run the full test suite before committing
5. Ensure code passes Black, Flake8, and migration checks
6. Consider impact on LDAP integration
7. Test with different database backends if relevant
8. Update CHANGELOG.md for significant changes
