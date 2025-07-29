<language_guidelines>

# 🐍 Python Coding Guidelines

<header>
<language_name>Python</language_name>
<paradigm>Functional-first programming with Pythonic idioms</paradigm>
<philosophy>"Simple is better than complex" - The Zen of Python</philosophy>
</header>

When providing Python code suggestions, follow these principles:

<core_principles>

### 📐 Architecture Principles

<solid_principles>
- **Single Responsibility**: Each function/class should have one clear purpose
- **Open/Closed**: Use protocols and composition for extensibility
- **Liskov Substitution**: Ensure consistent interfaces and behavior
- **Interface Segregation**: Create focused, specific protocols and interfaces
- **Dependency Inversion**: Depend on abstractions through protocols and ABC
</solid_principles>

<dry_principle>
- **Don't Repeat Yourself**: "There should be one obvious way to do it"
- **Functional composition**: Break complex logic into small, reusable functions
- **Decorators**: Extract cross-cutting concerns (logging, caching, validation)
- **Generators**: Reusable, memory-efficient data processing patterns
</dry_principle>

<clean_code>
- **"Readability counts"**: Write self-documenting, clear code
- **"Explicit is better than implicit"**: Make intent obvious
- **"Simple is better than complex"**: Prefer straightforward solutions
- **Meaningful names**: Use descriptive, intention-revealing names
</clean_code>

<yagni>
- **"You aren't gonna need it"**: Don't implement features until needed
- **Start simple**: "Simple is better than complex"
- **Progressive enhancement**: Build basic functionality first
</yagni>

</core_principles>

<language_specific>

### 🛠️ Python-Specific Best Practices

<best_practices>
- **Functional programming**: Prefer functions over classes for most use cases
- **Type hints**: Always use type annotations for better documentation and tooling
- **Dataclasses**: Use @dataclass for data containers instead of regular classes
- **Context managers**: Use `with` statements for resource management
- **Generators**: For memory-efficient iteration and processing
- **Pathlib**: Use pathlib.Path instead of os.path
</best_practices>

<idioms>
- **"Pythonic code"**: Follow Python's idioms and conventions
- **"Duck typing"**: "If it walks like a duck and quacks like a duck..."
- **"EAFP"**: Easier to Ask for Forgiveness than Permission
- **"Batteries included"**: Leverage Python's rich standard library
- **"Import this"**: Follow the Zen of Python principles
</idioms>

<performance>
- **Built-in functions**: Leverage map(), filter(), any(), all()
- **List comprehensions**: Often faster than equivalent loops
- **Generators**: Memory-efficient iteration
- **Caching**: Use @lru_cache for expensive computations
- **NumPy/Pandas**: For numerical computations and data processing
</performance>

</language_specific>

### 🎨 Naming Conventions (PEP 8)
- **Functions/variables**: snake_case (get_user_data, is_valid)
- **Classes**: PascalCase (UserService, DataProcessor)
- **Constants**: SCREAMING_SNAKE_CASE (API_BASE_URL, MAX_RETRIES)
- **Private attributes**: _private_method, __very_private
- **Files/modules**: snake_case (user_service.py, data_utils.py)

### 🔍 Pythonic Programming Guidelines
- **Functions first**: Use functions and composition over classes
- **Immutability**: Prefer immutable data structures and pure functions
- **Generators**: For lazy evaluation and memory efficiency
- **Context managers**: For resource management and setup/teardown
- **Decorators**: For cross-cutting concerns and function enhancement

### ⚡ Modern Python Features
- **Type hints**: Static type checking with mypy
- **Dataclasses**: Automatic generation of special methods
- **f-strings**: Modern string formatting
- **Pathlib**: Object-oriented filesystem paths
- **Context managers**: Custom `with` statement behavior
- **Async/await**: Asynchronous programming patterns

### 🎯 Error Handling Patterns
- **Specific exceptions**: Catch specific exception types
- **Custom exceptions**: Create domain-specific exception classes
- **Exception chaining**: Use `raise ... from` to preserve context
- **EAFP**: "Easier to Ask for Forgiveness than Permission"
- **Fail fast**: Validate inputs early with meaningful messages

<examples>

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

</examples>

<ecosystem>

### 🧪 Testing Philosophy

<testing>
- **pytest**: Modern Python testing framework
- **Test-driven development**: Write tests first when possible
- **Pure functions**: Easier to test, prefer functional style
- **Fixtures**: Use pytest fixtures for test setup
- **Mock external dependencies**: Isolate units under test
</testing>

### 📝 Documentation

<documentation>
- **Docstrings**: Google or NumPy style for all public functions/classes
- **Type hints**: Serve as inline documentation
- **README files**: Setup, usage, and architecture decisions
- **Examples in docstrings**: Include usage examples when helpful
</documentation>

### 🔧 Tools

<tools>
- **mypy**: Static type checking
- **black**: Code formatting
- **pytest**: Testing framework
- **pylint/flake8**: Code quality and linting
- **poetry/pip-tools**: Dependency management
</tools>

</ecosystem>

### 💡 Python Philosophy
- **"Beautiful is better than ugly"**: Write aesthetically pleasing code
- **"Explicit is better than implicit"**: Make intentions clear
- **"Simple is better than complex"**: Prefer straightforward solutions
- **"Readability counts"**: Code is read more than written
- **"There should be one obvious way to do it"**: Follow Python idioms

### 🔷 Advanced Python Patterns
- **Metaclasses**: Only when absolutely necessary, prefer class decorators
- **Descriptors**: For advanced attribute access control
- **Async/await**: For I/O-bound operations, prefer over threading
- **Type variables**: For generic functions and classes
- **Union types**: For functions that can accept multiple types
- **Literal types**: For string/numeric constants with type safety
- **Final**: For constants and methods that shouldn't be overridden

**Remember**: Always prioritize readability, maintainability, and testability over clever one-liners or premature optimization. "Explicit is better than implicit" - The Zen of Python.

</language_guidelines>
