# Contributing to Game Deals Assistant

First off, thank you for considering contributing to Game Deals Assistant! It's people like you that make this project such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs if possible**
* **Include your environment details** (OS, Python version, browser, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and the expected behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

* Follow the Python styleguides outlined below
* Include appropriate test cases
* Update documentation as needed
* Use clear commit messages
* Reference related issues in your PR

## Development Setup

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Set up the development environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   pip install pytest pytest-cov flake8 black isort
   ```
4. Make your changes
5. Format code and run linters:
   ```bash
   black app/
   isort app/
   flake8 app/
   ```
6. Test your changes:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
7. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
8. Push to the branch (`git push origin feature/AmazingFeature`)
9. Open a Pull Request

## Styleguides

### Python Code Style

* We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Use type hints for function parameters and return values
* Maximum line length: 127 characters
* Use meaningful variable names

Example:
```python
def fetch_deals(
    min_discount: int = 10,
    max_discount: int = 100,
    title: Optional[str] = None
) -> List[Dict]:
    """Fetch filtered game deals from APIs."""
    # Implementation
    pass
```

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Example:
```
Add Steam library sync feature

- Implement Steam API integration
- Add user preference for auto-sync
- Update database schema for connected accounts

Closes #42
```

### Documentation

* Use clear, concise language
* Include code examples where appropriate
* Keep README.md up to date
* Add docstrings to new functions and classes

## Testing

* Write tests for new features
* Ensure all tests pass before submitting PR
* Aim for high code coverage
* Test edge cases and error conditions

```python
def test_discount_validation():
    assert validate_discount_range(10, 100) is True
    assert validate_discount_range(-10, 100) is False
    assert validate_discount_range(100, 10) is False
```

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Improvements or additions to documentation
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed
* `question` - Further information is requested

### Project Structure Best Practices

* Keep functions focused and small
* Use meaningful names
* Add error handling with informative messages
* Log important operations for debugging
* Use type hints throughout

### Performance Considerations

* Optimize database queries (use appropriate indexes)
* Cache frequently accessed data
* Minimize external API calls
* Consider pagination for large result sets

## Recognition

Contributors will be recognized in:
* The README.md file
* Release notes
* GitHub contributors page

## Questions?

Feel free to open an issue with the `question` label or contact the maintainer at nodirmuhammedov_acer@outlook.com

Thank you for your contribution! 🎉
