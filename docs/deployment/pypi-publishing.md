# PyPI Publishing Guide

Complete guide to publish Context-AI to PyPI and TestPyPI.

## 📋 Prerequisites

- Python 3.9+
- PyPI account
- TestPyPI account  
- Two-factor authentication enabled
- `pipx` installed for clean testing

## 🏗️ Initial Setup

### Account Creation

1. **Create PyPI account**: https://pypi.org/account/register/
2. **Create TestPyPI account**: https://test.pypi.org/account/register/
3. **Enable 2FA on both accounts** (required for uploads)
4. **Generate API tokens**:
   - PyPI: Account Settings → API tokens → "Add API token"
   - TestPyPI: Account Settings → API tokens → "Add API token"

### Local Configuration

#### Setup Development Environment
```bash
# Create virtual environment and install all dependencies
make setup           # Creates venv
source venv/bin/activate
make install-dev     # Installs all dev dependencies (including twine)

# Verify pipx is available
pipx --version
```

**Note**: `twine` is now included in the dev dependencies, so `make install-dev` installs everything you need.

#### Configure Credentials

Create/edit `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-xxxxx-your-testpypi-token-here

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-xxxxx-your-real-pypi-token-here
```

**Security Note**: Keep tokens secure and never commit them to git.

## 📊 Versioning Strategy

Context-AI uses **PEP 440** versioning format:

### Version Formats
```toml
# Alpha releases (early testing)
version = "0.1.0a1"  # First alpha
version = "0.1.0a2"  # Second alpha

# Beta releases (feature complete)  
version = "0.1.0b1"  # First beta
version = "0.1.0b2"  # Second beta

# Release candidates
version = "0.1.0rc1" # First release candidate

# Production releases
version = "0.1.0"    # Stable release
version = "0.1.1"    # Patch release
```

### When to Use Each
- **Alpha (`a1`, `a2`)**: Breaking changes expected, early testing
- **Beta (`b1`, `b2`)**: Feature complete, minor bugs only  
- **Release Candidate (`rc1`)**: Production ready, final testing
- **Release (`0.1.0`)**: Stable, ready for end users

### Version Ordering
Python automatically understands: `0.1.0a1` < `0.1.0a2` < `0.1.0b1` < `0.1.0rc1` < `0.1.0`

## 🚀 Publishing Workflow

### Development Testing Cycle

#### 1. Prepare Release
```bash
# Run full development checks
make dev

# Update version in pyproject.toml
# Edit: version = "0.1.0a1"
```

#### 2. Test Publish to TestPyPI
```bash
# Build and upload to TestPyPI
make test-publish
```

#### 3. Test Installation
```bash
# Install using pipx (recommended)
make test-install

# Verify it works
make verify-install
```

#### 4. Clean Up for Next Test
```bash
# Uninstall test version
make test-uninstall

# Iterate: update version to 0.1.0a2, repeat...
```

### Production Release

#### 1. Final Preparation
```bash
# Final development checks
make dev

# Update to production version
# Edit pyproject.toml: version = "0.1.0"

# Clean previous builds
make clean
```

#### 2. Publish to PyPI
```bash
# Build and upload to production PyPI
make publish
```

#### 3. Create Git Release
```bash
# Tag the release
git add pyproject.toml
git commit -m "Release v0.1.0"
git tag v0.1.0
git push origin main
git push origin v0.1.0
```

#### 4. Verify Production Installation
```bash
# Test with pipx (user perspective)
pipx install context-ai
context-ai --version

# Test with pip (developer perspective)
pip install context-ai
```

## 📋 Available Make Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `make build` | Build distribution files (.whl, .tar.gz) | After code changes |
| `make test-publish` | Upload to TestPyPI | Testing releases |
| `make publish` | Upload to PyPI | Production releases |
| `make test-install` | Install from TestPyPI with pipx | Test functionality |
| `make test-uninstall` | Remove pipx installation | Clean between tests |
| `make verify-install` | Test CLI commands work | Verify installation |
| `make clean` | Remove build artifacts | Before new builds |

### Complete Testing Workflow
```bash
# Full cycle example
make test-publish    # Upload test version
make test-install    # Install with pipx  
make verify-install  # Test commands
make test-uninstall  # Clean up

# Update version, repeat...
```

### Alpha Testing Workflow (TestPyPI)

Complete workflow from development setup to alpha testing:

```bash
# === INITIAL SETUP (one time only) ===
# 1. Setup development environment
make setup
source venv/bin/activate
make install-dev

# 2. Configure API tokens in ~/.pypirc (see setup section above)

# === DEVELOPMENT & TESTING CYCLE ===
# 3. Develop your changes (ensure you're in venv)
source venv/bin/activate  # if not already active

# 4. Run development checks
make dev  # format, lint, type-check, test

# 5. Update version in pyproject.toml (e.g., version = "0.1.0a1")

# 6. Publish alpha to TestPyPI (done in venv)
make alpha-publish

# 7. Exit venv for clean testing environment
deactivate

# 8. Install and test globally with pipx
make alpha-install

# 9. Test installation works for end users
context-ai --version
context-ai --help

# 10. Remove test installation
make alpha-uninstall

# 11. Return to development (repeat from step 3 for next iteration)
source venv/bin/activate
```

**Key Points:**
- **Publishing** happens inside venv (needs twine, build tools)
- **Testing** happens outside venv (simulates end user experience)
- **TestPyPI** allows you to delete packages if needed
- Update version (e.g., `0.1.0a1` → `0.1.0a2`) for each iteration

## 🔧 Manual Commands (if needed)

### Direct twine usage:
```bash
# TestPyPI
twine upload --repository testpypi dist/*

# Production PyPI  
twine upload dist/*

# Check before upload
twine check dist/*
```

### Direct pipx usage:
```bash
# Install from TestPyPI
pipx install --index-url https://test.pypi.org/simple/ context-ai --prerelease

# Install from PyPI
pipx install context-ai

# Uninstall
pipx uninstall context-ai

# List installed
pipx list
```

## ❗ Troubleshooting

### Common Issues

#### "File already exists" error
```
ERROR: File already exists. 
See https://pypi.org/help/#file-name-reuse for details.
```
**Solution**: Once published, you cannot reuse the same version number. Increment version (e.g., `0.1.0a1` → `0.1.0a2`).

#### Authentication errors
```
ERROR: Invalid username/password
```
**Solutions**:
- Verify API token in `~/.pypirc`
- Check if 2FA is enabled  
- Regenerate API token if needed

#### "context-ai: command not found"
**Solutions**:
```bash
# Ensure pipx path is configured
pipx ensurepath

# Reload shell
source ~/.bashrc  # or ~/.zshrc

# Or install pipx if missing
python -m pip install --user pipx
```

#### Dependencies not found on TestPyPI
TestPyPI might not have all dependencies. This is normal - users should install from production PyPI.

### Useful Verification Commands
```bash
# Check package info
pip show context-ai

# List pipx packages
pipx list

# Check twine config
twine check dist/*

# Verify build contents
tar -tzf dist/context_ai-0.1.0a1.tar.gz | head -20
```

## 🔒 Security Best Practices

### API Tokens
- ✅ Use API tokens, never passwords
- ✅ Store tokens in `~/.pypirc` only
- ✅ Never commit tokens to git
- ✅ Use scoped tokens when possible
- ✅ Rotate tokens periodically

### Account Security
- ✅ Enable 2FA on both PyPI accounts
- ✅ Use unique, strong passwords
- ✅ Monitor login activity
- ✅ Keep email address updated

### Build Security  
- ✅ Always run `twine check dist/*` before upload
- ✅ Review build contents: `tar -tzf dist/*.tar.gz`
- ✅ Test in isolated environment first

## 🤖 Automation (Future Enhancement)

### GitHub Actions Workflow
Consider adding automated publishing:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI
on:
  release:
    types: [published]
    
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Build and publish
        run: |
          make dev
          make publish
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

### Automatic Version Bumping
Tools like `bump2version` can help automate version updates:

```bash
pip install bump2version
bump2version patch  # 0.1.0 -> 0.1.1
bump2version minor  # 0.1.1 -> 0.2.0  
bump2version major  # 0.2.0 -> 1.0.0
```

## 📚 Additional Resources

- [PyPI Help](https://pypi.org/help/)
- [Python Packaging Guide](https://packaging.python.org/)
- [PEP 440 - Versioning](https://www.python.org/dev/peps/pep-0440/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [pipx Documentation](https://pypa.github.io/pipx/)

---

**Happy Publishing! 🚀**
