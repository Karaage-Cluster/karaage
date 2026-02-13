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

## Quick Start

Get the project running in under 5 minutes:

```bash
# 1. Install system dependencies (Ubuntu/Debian)
sudo apt-get install libcrack2-dev

# 2. Install Python dependencies
uv sync --all-extras --dev --group docs

# 3. Run migrations (uses SQLite for testing)
./manage.py migrate --settings=karaage.tests.settings

# 4. Run tests to verify setup
uv run pytest --cov=karaage

# 5. (Optional) Start development server
./manage.py runserver --settings=dev_settings
```

**Note**: The development server requires additional configuration in `dev_settings.py` for database and LDAP connections.

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

#### Prerequisites

- Python 3.10 or later
- Git
- System dependencies:
  - `libcrack2-dev` - Required for password checking (Ubuntu/Debian: `sudo apt-get install libcrack2-dev`)
  - `slapd` and `ldap-utils` - Required for LDAP testing (optional for basic development)

#### Installation Steps

1. **Clone and enter the repository**:
   ```bash
   git clone https://github.com/Karaage-Cluster/karaage.git
   cd karaage
   ```

2. **Install Python dependencies**:
   ```bash
   # Using uv (preferred - automatically creates and manages virtual environment)
   uv sync --all-extras --dev --group docs
   
   # Or using pip (create virtual environment first)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .[dev,docs]
   ```

3. **Configure settings**:
   - For **testing**: Use `karaage.tests.settings` (SQLite, pre-configured)
   - For **local development**: Copy and modify `dev_settings.py` (requires PostgreSQL/MySQL setup)
   - Never commit local settings files or credentials

4. **Run database migrations**:
   ```bash
   # For testing (SQLite)
   ./manage.py migrate --settings=karaage.tests.settings
   
   # For local development (requires configured database)
   ./manage.py migrate --settings=dev_settings
   ```

5. **Create a superuser** (optional, for development server):
   ```bash
   ./manage.py createsuperuser --settings=dev_settings
   ```

### Running Tests

**Basic test execution**:
```bash
# Run all tests with coverage
uv run pytest --cov=karaage

# Or use the test script
./run_tests.sh
```

**Specific test execution**:
```bash
# Run a specific test file
uv run pytest karaage/tests/projects/test_models.py

# Run a specific test class
uv run pytest karaage/tests/projects/test_models.py::TestProjectModel

# Run a specific test method
uv run pytest karaage/tests/projects/test_models.py::TestProjectModel::test_create_project

# Run tests matching a keyword
uv run pytest -k "project"
```

**LDAP tests** (requires running LDAP server):
```bash
# Run with temporary LDAP server
uv run python -m tldap.test.slapd python -m pytest --cov=karaage

# Run specific LDAP test
uv run python -m tldap.test.slapd python -m pytest karaage/tests/test_ldap.py
```

**Database-specific tests**:
```bash
# The CI runs tests against both MySQL and PostgreSQL
# Local testing uses SQLite by default via karaage.tests.settings
```

**Test output options**:
```bash
# Verbose output
uv run pytest -v

# Show print statements
uv run pytest -s

# Stop on first failure
uv run pytest -x

# Run last failed tests only
uv run pytest --lf
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

### Test Framework and Tools
- **Framework**: pytest with pytest-django plugin
- **Coverage**: pytest-cov for coverage reports
- **Fixtures**: Load test data from `fixtures/` directory or use factory-boy patterns
- **Database**: Tests use `@pytest.mark.django_db` decorator to enable database access

### Test Organization
- Tests mirror the application structure: `karaage/tests/<app_name>/`
- Use `test_*.py` or `*_test.py` naming patterns
- Group related tests in test classes
- Use descriptive test method names: `test_<action>_<expected_result>`

### Writing Tests

**Basic test pattern**:
```python
import pytest
from karaage.tests.factories import PersonFactory, ProjectFactory

@pytest.mark.django_db
class TestProject:
    """Test project functionality."""
    
    fixtures = ["test_karaage.json"]  # Load fixture data if needed
    
    def test_create_project_with_leader(self):
        """Test that a project can be created with a leader."""
        leader = PersonFactory()
        project = ProjectFactory(leaders=[leader])
        
        assert project.leaders.count() == 1
        assert leader in project.leaders.all()
    
    def test_project_requires_name(self):
        """Test that project name is required."""
        with pytest.raises(ValidationError):
            ProjectFactory(name=None)
```

**Testing views**:
```python
@pytest.mark.django_db
def test_project_list_view_requires_login(client):
    """Test that project list requires authentication."""
    response = client.get('/projects/')
    assert response.status_code == 302  # Redirect to login

@pytest.mark.django_db
def test_project_list_view_shows_projects(client, django_user_model):
    """Test that authenticated users can see project list."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    client.login(username='testuser', password='testpass')
    
    ProjectFactory.create_batch(3)
    response = client.get('/projects/')
    
    assert response.status_code == 200
    assert len(response.context['project_list']) == 3
```

### Test Settings
- Tests run with `karaage.tests.settings` (SQLite database)
- Test database is created and destroyed automatically
- Use `pytest.ini` for pytest configuration
- Coverage settings in `pyproject.toml`

### Running Specific Tests
```bash
# Run tests for a specific app
uv run pytest karaage/tests/projects/

# Run tests with a marker
uv run pytest -m "not slow"

# Run tests and show coverage for specific module
uv run pytest --cov=karaage.projects --cov-report=term-missing
```

## Django-Specific Guidelines

### Settings Files
- **`karaage.tests.settings`**: For running tests (SQLite, pre-configured, safe to use)
- **`dev_settings.py`**: For local development server (requires manual configuration)
- **Never commit**: Local settings files, credentials, or environment-specific configuration

### Models
- Follow Django ORM best practices
- Use appropriate field types (CharField, IntegerField, ForeignKey, etc.)
- Add `verbose_name` and `help_text` for admin interface
- Implement `__str__()` method for readable object representation
- Use `Meta` class for ordering, permissions, and other options

**Example model pattern**:
```python
from django.db import models

class Project(models.Model):
    """Represents an HPC project."""
    
    name = models.CharField(max_length=255, unique=True, help_text="Project name")
    description = models.TextField(blank=True, help_text="Project description")
    is_active = models.BooleanField(default=True)
    leaders = models.ManyToManyField('Person', related_name='led_projects')
    
    class Meta:
        ordering = ['name']
        permissions = [
            ("view_project_members", "Can view project members"),
        ]
    
    def __str__(self):
        return self.name
```

### Views
- Prefer class-based views (CBVs) for common patterns
- Use Django's generic views when appropriate (ListView, DetailView, CreateView, etc.)
- Implement proper permission checks (LoginRequiredMixin, PermissionRequiredMixin)
- Use get_queryset() to filter data appropriately

### URL Patterns
- Use `path()` for simple routes, `re_path()` for complex patterns
- Name all URL patterns for reverse lookup
- Group related URLs in app-specific `urls.py` files

### Templates
- Use Django template language
- Store templates in `<app>/templates/<app_name>/` directories
- Extend base templates (`base.html`, `admin/base.html`)
- Use `{% load static %}` for static files

### Management Commands
- Place in `<app>/management/commands/` directories
- Inherit from `BaseCommand`
- Implement `handle()` method
- Use `self.stdout.write()` for output

### Migrations
1. Always create migrations when models change
2. Check for migration conflicts: `./manage.py makemigrations --check --dry-run`
3. Review generated SQL: `./manage.py sqlmigrate <app> <migration>`
4. Test migrations can be reversed: `./manage.py migrate <app> <previous_migration>`
5. **Never modify committed migrations** - create new ones instead

## Common Development Tasks

### Creating Database Migrations

```bash
# Check for missing migrations
./manage.py makemigrations --settings=karaage.tests.settings --check --dry-run

# Create migrations
./manage.py makemigrations --settings=karaage.tests.settings

# View SQL for a migration
./manage.py sqlmigrate karaage <migration_name> --settings=karaage.tests.settings

# Apply migrations
./manage.py migrate --settings=karaage.tests.settings
```

### Running the Development Server

```bash
# Start server (requires configured dev_settings.py)
./manage.py runserver --settings=dev_settings

# Access admin interface at http://localhost:8000/admin/
# Requires superuser: ./manage.py createsuperuser --settings=dev_settings
```

### Working with Static Files

```bash
# Collect static files for deployment
./manage.py collectstatic --settings=karaage.tests.settings --noinput

# In development, Django serves static files automatically when DEBUG=True
```

### Using Management Commands

```bash
# List all available commands
./manage.py help --settings=karaage.tests.settings

# Karaage-specific commands (when installed)
kg-manage <command>

# Common commands:
kg-manage shell          # Django shell
kg-manage dbshell        # Database shell
kg-manage check          # Check for problems
kg-manage test           # Run tests
```

## CI/CD

### GitHub Actions Workflow
- **Configuration**: `.github/workflows/pythonapp.yml`
- **Triggers**: Push, pull request, merge group
- **Test matrix**: MySQL and PostgreSQL databases
- **Coverage**: Automatically reported via pytest-cov
- **Docker**: Builds and publishes to GitHub Container Registry on successful main branch builds

### CI Troubleshooting

**Common CI failures and solutions**:

1. **Migration conflicts**:
   ```bash
   # Check locally before pushing
   ./manage.py makemigrations --settings=karaage.tests.settings --check --dry-run
   ```

2. **Test failures**:
   - Run the full test suite locally: `uv run pytest --cov=karaage`
   - Check database-specific issues (SQLite vs MySQL/PostgreSQL)
   - Ensure fixtures are up-to-date

3. **Linting failures**:
   ```bash
   # Format code
   uv run black karaage
   
   # Check linting
   uv run flake8 karaage
   
   # Type checking
   uv run mypy karaage
   ```

4. **Docker build failures**:
   - Verify dependencies in `pyproject.toml` are correct
   - Test Docker build locally: `docker build -t karaage .`

### Pre-Commit Checklist
Before pushing code, run these commands:
```bash
# 1. Format code
uv run black karaage

# 2. Check linting
uv run flake8 karaage

# 3. Check migrations
./manage.py makemigrations --settings=karaage.tests.settings --check --dry-run

# 4. Run tests
uv run pytest --cov=karaage

# 5. Type checking (optional but recommended)
uv run mypy karaage
```

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

### Security and Best Practices
1. **Never commit secrets**: Credentials, API keys, or sensitive configuration
2. **License**: GPL 3.0+ - ensure all contributions are compatible
3. **Copyright**: Copyright 2010-2017, The University of Melbourne and Brian May

### Backwards Compatibility
1. **LDAP schemas**: Maintain compatibility with existing LDAP/Active Directory schemas
2. **Database migrations**: Must work with both PostgreSQL and MySQL
3. **API stability**: Avoid breaking changes to public APIs without deprecation period
4. **Configuration**: Support existing `settings.py` patterns

### LDAP Integration
1. **Testing**: Some tests require a running LDAP server (uses `tldap.test.slapd`)
2. **Libraries**: Uses `ldap3` for LDAP client and `python-tldap` for utilities
3. **Backends**: Support for both OpenLDAP and Active Directory
4. **Local testing**: Install `slapd` and `ldap-utils` for full LDAP test coverage

### Plugin System
- Karaage has a plugin architecture for extending functionality
- Plugins are registered via Django app configuration
- See existing plugins in `karaage/plugins/` for examples
- Plugin development should follow the same code quality standards

### Performance Considerations
- Use `select_related()` and `prefetch_related()` to avoid N+1 queries
- Add database indexes for frequently queried fields
- Cache expensive operations where appropriate
- Monitor query counts in development using Django Debug Toolbar (if installed)

## Documentation

### User Documentation
- **Location**: https://karaage.readthedocs.io/
- **Building docs locally**: 
  ```bash
  cd docs/admin
  make html
  # Output in docs/admin/_build/html/
  ```
- **Documentation source**: `docs/` directory (Sphinx)
- **Configuration**: `docs/conf.py`

### Admin Documentation
- **Location**: `docs/admin/` directory
- **Format**: reStructuredText (.rst)
- **Topics**: Installation, configuration, administration, troubleshooting

### Contributing Documentation
1. Update relevant documentation when adding features
2. Use clear, concise language
3. Include code examples where appropriate
4. Test that documentation builds without errors: `make -C docs/admin html`
5. Update CHANGELOG.md for significant changes

## When Making Changes

### Before You Start
1. **Understand the issue**: Read the issue/PR description thoroughly
2. **Check dependencies**: Understand how your changes affect other components
3. **Plan your approach**: Think about the minimal changes needed
4. **Consider backwards compatibility**: Will this break existing installations?

### During Development
1. **Make small, focused commits**: Each commit should represent a logical unit of work
2. **Write meaningful commit messages**: 
   - First line: Brief summary (50 chars or less)
   - Body: Detailed explanation if needed
   - Reference issues: "Fixes #123" or "Related to #456"
3. **Add/update tests**: New features need tests, bug fixes should include regression tests
4. **Update documentation**: If behavior changes, update relevant docs
5. **Run code quality checks**: Black, Flake8, mypy, and migration checks
6. **Consider LDAP impact**: Will your changes affect LDAP integration?
7. **Test with different databases**: If changing models/queries, test with PostgreSQL and MySQL

### Before Committing
```bash
# Run the complete pre-commit checklist
uv run black karaage
uv run flake8 karaage
./manage.py makemigrations --settings=karaage.tests.settings --check --dry-run
uv run pytest --cov=karaage
```

### Pull Request Guidelines
1. **Title**: Clear, concise description of the change
2. **Description**: 
   - What problem does this solve?
   - What approach did you take?
   - Any breaking changes?
   - Testing notes
3. **Link issues**: Use "Fixes #123" in description
4. **Keep PRs focused**: One feature/fix per PR
5. **Respond to feedback**: Address review comments promptly

### Changelog Updates
Update `CHANGELOG.md` for:
- New features
- Bug fixes
- Breaking changes
- Deprecations
- Security fixes

Format:
```markdown
## [Unreleased]

### Added
- New feature description (#PR_NUMBER)

### Changed
- Changed behavior description (#PR_NUMBER)

### Fixed
- Bug fix description (#PR_NUMBER)
```

## Troubleshooting

### Common Setup Issues

**Issue**: `ImportError: No module named 'karaage'`
- **Solution**: Ensure you've installed the package: `uv sync` or `pip install -e .`

**Issue**: `django.db.utils.OperationalError: no such table`
- **Solution**: Run migrations: `./manage.py migrate --settings=karaage.tests.settings`

**Issue**: `ModuleNotFoundError: No module named '_cracklib'`
- **Solution**: Install libcrack2-dev: `sudo apt-get install libcrack2-dev`, then reinstall Python packages

**Issue**: LDAP tests failing
- **Solution**: Install LDAP tools: `sudo apt-get install slapd ldap-utils`
- **Alternative**: Skip LDAP tests: `uv run pytest -m "not ldap"`

**Issue**: Test database locked (SQLite)
- **Solution**: Close any open database connections, remove `test_db.sqlite3` if it exists

### Development Server Issues

**Issue**: `ALLOWED_HOSTS` error when accessing server
- **Solution**: Add your hostname/IP to `ALLOWED_HOSTS` in `dev_settings.py`

**Issue**: Static files not loading
- **Solution**: Ensure `DEBUG = True` in settings, or run `./manage.py collectstatic`

**Issue**: Admin interface shows "403 Forbidden"
- **Solution**: Check CSRF settings and ensure you're logged in as a superuser

### Database Issues

**Issue**: Migration conflicts
- **Solution**: 
  ```bash
  # Check current state
  ./manage.py showmigrations --settings=karaage.tests.settings
  
  # If needed, merge migrations
  ./manage.py makemigrations --merge --settings=karaage.tests.settings
  ```

**Issue**: Different behavior between SQLite and PostgreSQL/MySQL
- **Solution**: Some database features differ between engines. Test with the target database.

### Getting Help

1. **Check existing issues**: https://github.com/Karaage-Cluster/karaage/issues
2. **Read the documentation**: https://karaage.readthedocs.io/
3. **Review test cases**: Look at existing tests for usage examples
4. **Ask for help**: Open a GitHub issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Your environment (OS, Python version, database)
   - Relevant error messages and logs
