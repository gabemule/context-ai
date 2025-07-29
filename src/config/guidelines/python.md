## 🐍 Python Coding Guidelines

When providing Python code suggestions, follow these principles:

### 📐 Architecture Principles
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **DRY (Don't Repeat Yourself)**: Eliminate code duplication through abstraction
- **YAGNI (You Aren't Gonna Need It)**: Don't implement features until they're actually needed
- **Clean Code**: Write self-documenting, readable code with meaningful names

### 🔧 Pythonic Programming Focus
- **PREFER functions over classes** - Use functions, decorators, and composition
- **Immutability**: Use dataclasses with frozen=True, avoid mutations, use pure functions
- **Pure functions**: Functions should not have side effects and return predictable outputs
- **Function composition**: Break complex logic into small, composable functions
- **Use classes sparingly**: Only for stateful objects, data containers, or specific APIs

### 🛠️ Code Style Guidelines (PEP 8+)
- **Type hints**: Always use type annotations for function parameters and returns
- **f-strings**: Use f"" for string formatting instead of .format() or %
- **List/dict comprehensions**: Prefer over loops when readable
- **Context managers**: Use `with` statements for resource management
- **Pathlib**: Use `pathlib.Path` instead of `os.path`
- **Dataclasses**: Use `@dataclass` for simple data containers

### 📦 Module Organization
- **Clear imports**: Use absolute imports, group by standard/third-party/local
- **__all__**: Define public API explicitly in modules
- **Package structure**: Use __init__.py to create clean public APIs
- **Dependency injection**: Pass dependencies as parameters rather than importing globally

### 🎨 Naming Conventions
- **snake_case**: For variables, functions, and methods
- **PascalCase**: For classes and exceptions
- **SCREAMING_SNAKE_CASE**: For constants
- **Descriptive names**: Use clear, descriptive names that explain intent
- **Private attributes**: Use single underscore for internal use

### 🔍 Error Handling
- **Specific exceptions**: Catch specific exception types, not bare except
- **Custom exceptions**: Create domain-specific exception classes
- **Fail fast**: Validate inputs early with meaningful error messages
- **Context in exceptions**: Include relevant context in error messages
- **Exception chaining**: Use `raise ... from` to preserve original traceback

### ⚡ Performance Guidelines
- **Generators**: Use generators for memory-efficient iteration
- **Built-in functions**: Leverage built-ins like map(), filter(), any(), all()
- **Caching**: Use @lru_cache for expensive computations
- **Lazy evaluation**: Load data only when needed
- **List comprehensions**: Often faster than equivalent loops

### 🧪 Testing Philosophy
- **Test-driven development**: Write tests first when possible
- **pytest**: Use pytest for testing framework
- **Pure functions are easier to test**: Another reason to prefer functional style
- **Fixtures**: Use pytest fixtures for test setup
- **Mock external dependencies**: Isolate units under test

### 📝 Documentation
- **Docstrings**: Use Google or NumPy style docstrings for all public functions/classes
- **Type hints**: Serve as inline documentation and enable better IDE support
- **README files**: Document setup, usage, and architecture decisions
- **Examples in docstrings**: Include usage examples when helpful

### 🚫 Anti-patterns to Avoid
- **Classes for stateless logic**: Don't use classes just for namespacing
- **Inheritance**: Prefer composition over inheritance
- **Global state**: Minimize global variables and state
- **Magic numbers/strings**: Use named constants or enums
- **Deep nesting**: Keep cyclomatic complexity low
- **Bare except**: Always catch specific exceptions
- **Mutable default arguments**: Use None and initialize inside function

### 💡 Recommended Patterns
- **Decorators**: For cross-cutting concerns (logging, timing, caching)
- **Context managers**: For resource management and setup/teardown
- **Generators**: For memory-efficient data processing
- **Dataclasses**: For data containers and configuration objects
- **Protocols**: For structural typing (duck typing with types)
- **Dependency injection**: For testable, modular code
- **Factory functions**: Instead of complex class hierarchies

### 🌟 Examples of Good Practices

```python
# ✅ Functional approach with pure functions
from dataclasses import dataclass
from typing import List, Optional, Protocol
from decimal import Decimal
from functools import lru_cache

@dataclass(frozen=True)
class Item:
    name: str
    price: Decimal
    category: str

def calculate_total(items: List[Item]) -> Decimal:
    """Calculate total price of items."""
    return sum(item.price for item in items)

def apply_discount(total: Decimal, discount_percent: float) -> Decimal:
    """Apply percentage discount to total."""
    return total * (1 - Decimal(str(discount_percent)) / 100)

@lru_cache(maxsize=128)
def format_currency(amount: Decimal, currency: str = "USD") -> str:
    """Format amount as currency string."""
    return f"${amount:.2f}" if currency == "USD" else f"{amount:.2f} {currency}"

# ✅ Composition over classes using protocols
class PaymentProcessor(Protocol):
    def process(self, amount: Decimal) -> bool: ...

def create_order_processor(
    tax_rate: float, 
    shipping_cost: Decimal,
    payment_processor: PaymentProcessor
) -> dict:
    """Create order processor with injected dependencies."""
    
    def calculate(items: List[Item], discount: float = 0) -> Decimal:
        subtotal = calculate_total(items)
        discounted = apply_discount(subtotal, discount)
        tax = discounted * Decimal(str(tax_rate))
        return discounted + tax + shipping_cost
    
    def format_amount(amount: Decimal) -> str:
        return format_currency(amount)
    
    def process_order(items: List[Item], discount: float = 0) -> dict:
        total = calculate(items, discount)
        success = payment_processor.process(total)
        return {
            "total": total,
            "formatted_total": format_amount(total),
            "payment_success": success
        }
    
    return {
        "calculate": calculate,
        "format": format_amount,
        "process": process_order
    }

# ✅ Error handling with custom exceptions
class PaymentError(Exception):
    """Raised when payment processing fails."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code

async def process_payment(payment_data: dict) -> dict:
    """Process payment and return result."""
    try:
        result = await payment_api.charge(payment_data)
        return {"success": True, "data": result}
    except PaymentError as error:
        return {
            "success": False, 
            "error": str(error),
            "error_code": error.error_code
        }
    except Exception as error:
        raise PaymentError("Unexpected payment error") from error

# ✅ Context manager for resource management
from contextlib import contextmanager
from pathlib import Path

@contextmanager
def file_processor(file_path: Path):
    """Context manager for safe file processing."""
    file_handle = None
    try:
        file_handle = file_path.open("r", encoding="utf-8")
        yield file_handle
    except IOError as error:
        raise FileProcessingError(f"Cannot process {file_path}") from error
    finally:
        if file_handle:
            file_handle.close()

# ✅ Generator for memory-efficient processing
def process_large_dataset(data_source: List[dict]) -> Iterator[dict]:
    """Process large dataset efficiently using generator."""
    for item in data_source:
        if item.get("valid", False):
            processed = transform_item(item)
            if processed:
                yield processed
```

### 🔷 Advanced Python Patterns

- **Metaclasses**: Only when absolutely necessary, prefer class decorators
- **Descriptors**: For advanced attribute access control
- **Async/await**: For I/O-bound operations, prefer over threading
- **Type variables**: For generic functions and classes
- **Union types**: For functions that can accept multiple types
- **Literal types**: For string/numeric constants with type safety
- **Final**: For constants and methods that shouldn't be overridden

**Remember**: Always prioritize readability, maintainability, and testability over clever one-liners or premature optimization. "Explicit is better than implicit" - The Zen of Python.
