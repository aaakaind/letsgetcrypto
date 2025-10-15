# GitHub Copilot Setup Documentation

This repository is configured with comprehensive GitHub Copilot instructions to provide context-aware code suggestions and assistance.

## 📁 Files Overview

### Main Instructions
- **`.github/copilot-instructions.md`** (264 lines)
  - Complete repository overview and architecture
  - Technology stack and dependencies
  - Code style guidelines and conventions
  - Security and error handling best practices
  - Development workflow and testing
  - Common development tasks
  - External resources and documentation

### Path-Specific Instructions

Path-specific instructions are automatically applied when working in specific parts of the codebase:

#### 1. Django API Instructions
- **File**: `.github/instructions/django-api.instructions.md` (57 lines)
- **Applies to**: 
  - `crypto_api/**/*.py`
  - `letsgetcrypto_django/**/*.py`
  - `manage.py`
- **Coverage**: REST API patterns, Django ORM, URL routing, security

#### 2. Machine Learning Instructions
- **File**: `.github/instructions/machine-learning.instructions.md` (72 lines)
- **Applies to**:
  - `main.py`
  - `**/feedback_loop*.py`
  - `**/test_feedback_loop*.py`
- **Coverage**: ML model architecture, feedback loop, data preparation, risk disclaimers

#### 3. MCP Server Instructions
- **File**: `.github/instructions/mcp-server.instructions.md` (84 lines)
- **Applies to**:
  - `crypto_mcp_server.py`
  - `mcp_server.py`
  - `examples/mcp_client_example.py`
  - `test_mcp_server.py`
- **Coverage**: MCP protocol compliance, tool definitions, Claude Desktop integration

#### 4. Testing Instructions
- **File**: `.github/instructions/testing.instructions.md` (145 lines)
- **Applies to**:
  - `test_*.py`
  - `**/*test*.py`
- **Coverage**: Test structure, pytest/unittest, mocking, Django testing

## 📊 Statistics

- **Total instruction lines**: 622
- **Main instructions**: 264 lines
- **Path-specific instructions**: 358 lines (4 files)
- **Coverage areas**: 5 major code areas

## 🚀 How It Works

### Automatic Context
When you work in different parts of the repository, GitHub Copilot automatically:
1. Loads the main `copilot-instructions.md` for general context
2. Applies relevant path-specific instructions based on the file you're editing
3. Provides suggestions that follow project conventions and patterns

### Example Scenarios

#### Working in Django API (`crypto_api/views.py`)
Copilot will know to:
- Use Django REST framework patterns
- Return JSON with proper status codes
- Follow RESTful URL conventions
- Implement CSRF protection

#### Working on ML Models (`main.py`)
Copilot will know to:
- Use appropriate model architectures (LSTM, XGBoost)
- Implement feedback loop patterns
- Include risk disclaimers
- Handle training/prediction errors gracefully

#### Writing Tests (`test_integration.py`)
Copilot will know to:
- Use pytest conventions
- Mock external API calls
- Structure tests with Arrange-Act-Assert
- Test both success and error cases

#### Developing MCP Server (`crypto_mcp_server.py`)
Copilot will know to:
- Follow MCP protocol specifications
- Define tools with JSON schemas
- Handle errors properly
- Format responses consistently

## 💡 Best Practices

### For Contributors
1. **Review instructions** relevant to your work area
2. **Follow the patterns** suggested by Copilot
3. **Update instructions** if you establish new patterns
4. **Keep instructions current** as the codebase evolves

### For Maintainers
1. **Update main instructions** when architecture changes
2. **Add new path-specific files** for new major components
3. **Review Copilot suggestions** to ensure they align with instructions
4. **Refine instructions** based on common issues or questions

## 📚 References

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Custom Instructions Guide](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [Path-Specific Instructions](https://docs.github.com/en/copilot/configuring-github-copilot/custom-instructions-for-github-copilot)

## 🔄 Maintenance

### When to Update Instructions

Update the instructions when:
- **New features** are added to the project
- **Architecture changes** occur
- **New technologies** are adopted
- **Code conventions** evolve
- **Common issues** emerge that could be prevented with better guidance

### How to Update

1. Edit the relevant `.instructions.md` file
2. Test that Copilot provides appropriate suggestions
3. Commit changes with descriptive message
4. Update this documentation if structure changes

## ✅ Verification

To verify the setup is working:

1. **Open a file** in VS Code or GitHub Codespaces
2. **Check that Copilot is active** (icon in status bar)
3. **Start typing** and observe suggestions
4. **Suggestions should follow** the patterns described in instructions

Example verification:
```python
# In crypto_api/views.py, start typing:
def get_crypto_price
# Copilot should suggest a view that returns JSON with status codes

# In test_integration.py, start typing:
def test_
# Copilot should suggest test functions with proper structure
```

## 🎯 Goals Achieved

✅ Consistent code style across repository  
✅ Context-aware suggestions for different code areas  
✅ Security best practices enforcement  
✅ Proper error handling patterns  
✅ Testing conventions guidance  
✅ ML model development patterns  
✅ Django REST API standards  
✅ MCP protocol compliance  

## 📞 Support

For questions or issues with Copilot instructions:
1. Review the instruction files in `.github/`
2. Check the [main README](../README.md) for project documentation
3. Open an issue if instructions need clarification or updates

---

**Last Updated**: 2025-10-14  
**Total Instructions**: 622 lines across 5 files
