# Installation

## Requirements

PyValidX requires Python 3.10 or higher and depends on:

- **Pydantic 2.11.7+** - For model validation and type checking
- **typing-extensions** - For enhanced type annotations

## Install PyValidX

### Using pip

```bash
pip install pyvalidx
```

### Using poetry

```bash
poetry add pyvalidx
```

### Development Installation

If you want to contribute to PyValidX or need the latest development version:

```bash
# Clone the repository
git clone https://github.com/harrsion-gaviria/pyvalidx.git
cd pyvalidx

# Install in development mode
pip install -e .

# Or with poetry
poetry install
```

## Verify Installation

After installation, verify that PyValidX is working correctly:

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required

class TestModel(ValidatedModel):
    name: str = field_validated(is_required())

# This should work without errors
test = TestModel(name="PyValidX")
print(f"Installation successful! Created model with name: {test.name}")
```

If you see the success message, PyValidX is installed and ready to use!

## Next Steps

- [Quick Start Guide](quick-start.md) - Learn the basics in 5 minutes
- [Basic Concepts](basic-concepts.md) - Understand core PyValidX concepts
- [Core Validators](../validators/core.md) - Explore available validators
