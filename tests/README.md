# Bestatic Testing Guide

## Overview
This test suite provides comprehensive coverage for the Bestatic static site generator, including unit tests and integration tests for all major components.

Note that, this test suite (and this document) was primarily generated using the LLMs. While some effort has been made to ensure accuracy, some tests may require adjustments and if you find any issues, please report them.

## Test Structure

```
bestatic/tests/
├── __init__.py              # Package marker
├── conftest.py              # Shared pytest fixtures
├── test_generator.py        # Core generation logic tests
├── test_shortcodes.py       # Shortcode processing tests
├── test_newcontent.py       # Post/page creation tests
├── test_sitemap.py          # Sitemap generation tests
├── test_cli.py              # CLI argument parsing tests
└── test_quickstart.py       # Project setup tests
```

## Prerequisites

### Install Test Dependencies

```bash
# Navigate to the bestatic package directory
cd /home/<username>/Python_files/bestatic

# Install pytest and pytest-cov if not already installed
pip install pytest pytest-cov

# Verify installation
pytest --version
```

### Ensure All Dependencies Are Installed

```bash
pip install -r requirements.txt
```

## Running Tests

### Run All Tests

```bash
# From the bestatic package directory
cd /home/<username>/Python_files/bestatic
pytest tests/
```

### Run Specific Test Files

```bash
# Test generator only
pytest tests/test_generator.py

# Test shortcodes only
pytest tests/test_shortcodes.py

# Test newcontent only
pytest tests/test_newcontent.py

# Test sitemap only
pytest tests/test_sitemap.py

# Test CLI only
pytest tests/test_cli.py

# Test quickstart only
pytest tests/test_quickstart.py
```

### Run Specific Test Classes

```bash
# Run only integration tests from generator
pytest tests/test_generator.py::TestGeneratorIntegration

# Run only shortcode loading tests
pytest tests/test_shortcodes.py::TestShortcodeLoading

# Run only CLI argument parsing tests
pytest tests/test_cli.py::TestCLIArgumentParsing
```

### Run Specific Test Functions

```bash
# Run a single test
pytest tests/test_generator.py::TestGeneratorIntegration::test_basic_site_generation

# Run tests matching a pattern
pytest tests/ -k "test_load"
pytest tests/ -k "sitemap"
```

### Run Tests with Verbose Output

```bash
# Show detailed test output
pytest tests/ -v

# Show even more detail (including print statements)
pytest tests/ -vv

# Show captured output
pytest tests/ -s
```

### Run Tests with Coverage Report

```bash
# Generate coverage report
pytest tests/ --cov=bestatic --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=bestatic --cov-report=html

# Then open htmlcov/index.html in a browser
```

## Test Coverage Summary

### High Priority (80%+ coverage target)
- ✅ **test_generator.py**: Core site generation logic
  - Helper functions (isolate_tags, load_data_files, etc.)
  - Full site generation workflow
  - Markdown processing
  - Template rendering
  - Data files integration

- ✅ **test_newcontent.py**: Content creation utilities
  - Post creation with frontmatter
  - Page creation
  - Directory structure handling

### Medium Priority (60-70% coverage)
- ✅ **test_shortcodes.py**: Shortcode processing
  - Dynamic module loading
  - Syntax parsing
  - Content processing

- ✅ **test_cli.py**: Command-line interface
  - Argument parsing
  - Server functionality (mocked)
  - Workflow scenarios

### Lower Priority (50%+ coverage)
- ✅ **test_sitemap.py**: Sitemap generation
  - XML generation
  - URL formatting
  - Directory traversal

- ✅ **test_quickstart.py**: Interactive setup
  - Configuration generation
  - Sample content creation
  - User input handling (mocked)

## Understanding Test Output

### Successful Test Run
```
========================= test session starts =========================
collected 150 items

tests/test_generator.py ..................              [ 12%]
tests/test_shortcodes.py ..........                     [ 18%]
tests/test_newcontent.py ................               [ 29%]
tests/test_sitemap.py .............                     [ 38%]
tests/test_cli.py ..................                    [ 50%]
tests/test_quickstart.py .......................        [100%]

========================= 150 passed in 5.23s =========================
```

### Failed Test Example
```
FAILED tests/test_generator.py::test_basic_site_generation - AssertionError
```

### Warnings
Some tests may show warnings - these are generally safe to ignore:
```
warnings summary
  tests/test_shortcodes.py::test_parse_empty_shortcode
    UserWarning: Empty shortcode found, skipping
```

## Test Fixtures

The test suite uses pytest fixtures defined in `conftest.py`:

- **minimal_theme**: Creates a basic functional theme with templates
- **sample_config**: Provides a minimal valid configuration
- **sample_posts**: Creates test markdown posts with frontmatter
- **sample_pages**: Creates test markdown pages
- **data_files**: Creates CSV and YAML test data files
- **mock_shortcodes**: Creates test shortcode modules
- **test_site**: Complete site structure ready for generation
- **test_site_with_shortcodes**: Site structure with shortcodes enabled

All fixtures use temporary directories (`tmp_path`) for isolation.

## Troubleshooting

### Tests Fail with Import Errors
```bash
# Make sure you're in the right directory
cd /home/<username>/Python_files/bestatic

# Install the package in development mode
pip install -e .
```

### Tests Fail with Missing Dependencies
```bash
# Install all requirements
pip install -r requirements.txt
pip install pytest pytest-cov
```

### Permission Errors
```bash
# Make sure test directories are writable
# Tests use tmp_path which should be automatically writable
```

### Slow Tests
```bash
# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest tests/ -n auto
```

## Continuous Integration

To integrate with CI/CD systems (GitHub Actions, GitLab CI, etc.):

```yaml
# Example .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt pytest pytest-cov
      - run: pytest tests/ --cov=bestatic
```

## Test Maintenance

### Adding New Tests
1. Create test functions starting with `test_`
2. Use appropriate fixtures from `conftest.py`
3. Follow the existing test structure
4. Run tests to verify they work

### Updating Fixtures
- Modify `conftest.py` to update shared test data
- Keep fixtures minimal and focused
- Use `tmp_path` for all file operations

## Expected Test Results

When all tests pass, you should see approximately:
- **test_generator.py**: ~30 tests (including integration tests)
- **test_shortcodes.py**: ~20 tests
- **test_newcontent.py**: ~20 tests
- **test_sitemap.py**: ~15 tests
- **test_cli.py**: ~20 tests
- **test_quickstart.py**: ~20 tests

**Total: ~125-150 tests**

## Notes

- Tests are designed to be independent and isolated
- Each test uses temporary directories (no pollution)
- File watcher tests are intentionally omitted (too complex)
- HTTP server tests are minimal (mocked only)
- Coverage target: 60-70% overall, 80%+ for core modules

## Getting Help

If tests fail unexpectedly:
1. Run with verbose output: `pytest tests/ -vv`
2. Run specific failing test: `pytest tests/test_file.py::test_name -vv`
3. Check for import errors or missing dependencies
4. Verify you're in the correct directory
5. Check that all fixtures are working: `pytest tests/ --fixtures`

---

**Quick Start:**
```bash
cd /home/<username>/Python_files/bestatic
pip install pytest pytest-cov
pytest tests/ -v
```
