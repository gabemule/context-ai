## ⚡ JavaScript Coding Guidelines

When providing JavaScript code suggestions, follow these principles:

### 📐 Architecture Principles
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **DRY (Don't Repeat Yourself)**: Eliminate code duplication through abstraction
- **YAGNI (You Aren't Gonna Need It)**: Don't implement features until they're actually needed
- **Clean Code**: Write self-documenting, readable code with meaningful names

### 🔧 Functional Programming Focus
- **PREFER functional programming over classes** - Use functions, higher-order functions, and composition
- **Immutability**: Prefer const, avoid mutations, use spread operators and pure functions
- **Pure functions**: Functions should not have side effects and return predictable outputs
- **Function composition**: Break complex logic into small, composable functions
- **Avoid classes** unless absolutely necessary (e.g., for React components, specific APIs)

### 🛠️ Code Style Guidelines
- **Arrow functions**: Prefer `const fn = () => {}` over `function fn() {}`
- **Destructuring**: Use object/array destructuring for cleaner code
- **Template literals**: Use backticks for string interpolation
- **Async/await**: Prefer over .then() chains for promises
- **Optional chaining**: Use `?.` for safe property access
- **Nullish coalescing**: Use `??` instead of `||` when checking for null/undefined

### 📦 Module Organization
- **ES6 modules**: Use import/export syntax
- **Named exports**: Prefer named exports over default exports for better refactoring
- **Barrel exports**: Use index.js files to create clean public APIs
- **Dependency injection**: Pass dependencies as parameters rather than importing globally

### 🎨 Naming Conventions
- **camelCase**: For variables, functions, and methods
- **PascalCase**: For types, interfaces, and React components
- **SCREAMING_SNAKE_CASE**: For constants
- **Descriptive names**: Use clear, descriptive names that explain intent

### 🔍 Error Handling
- **Explicit error handling**: Always handle errors explicitly
- **Result/Either pattern**: Consider using Result types for error handling
- **Fail fast**: Validate inputs early and throw meaningful errors
- **No silent failures**: Don't ignore or suppress errors

### ⚡ Performance Guidelines
- **Lazy loading**: Load code/data only when needed
- **Memoization**: Cache expensive computations
- **Debouncing/throttling**: For event handlers and API calls
- **Bundle optimization**: Use tree shaking and code splitting

### 🧪 Testing Philosophy
- **Test-driven development**: Write tests first when possible
- **Unit tests**: Test individual functions in isolation
- **Integration tests**: Test component interactions
- **Pure functions are easier to test**: Another reason to prefer functional style

### 📝 Documentation
- **JSDoc comments**: For public APIs and complex functions
- **Type annotations**: Use TypeScript types for better documentation
- **README files**: Document setup, usage, and architecture decisions

### 🚫 Anti-patterns to Avoid
- **Classes for stateless logic**: Don't use classes just for namespacing
- **Inheritance**: Prefer composition over inheritance
- **Global state**: Minimize global variables and state
- **Magic numbers/strings**: Use named constants
- **Deep nesting**: Keep cyclomatic complexity low
- **Premature optimization**: Focus on clean code first, optimize later

### 💡 Recommended Patterns
- **Higher-order functions**: For reusable logic
- **Currying**: For creating specialized functions
- **Closures**: For encapsulation without classes
- **Module pattern**: For organizing related functionality
- **Observer/PubSub**: For decoupled communication
- **Command pattern**: For encapsulating operations
- **Strategy pattern**: Using function composition instead of class inheritance

### 🌟 Examples of Good Practices

```javascript
// ✅ Functional approach with pure functions
const calculateTotal = (items) =>
  items.reduce((sum, item) => sum + item.price, 0);

const applyDiscount = (total, discountPercent) =>
  total * (1 - discountPercent / 100);

const formatCurrency = (amount) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);

// ✅ Composition over classes
const createOrderProcessor = (taxRate, shippingCost) => ({
  calculate: (items, discount = 0) => {
    const subtotal = calculateTotal(items);
    const discounted = applyDiscount(subtotal, discount);
    const tax = discounted * taxRate;
    return discounted + tax + shippingCost;
  },
  format: (amount) => formatCurrency(amount)
});

// ✅ Error handling with Result pattern
const processPayment = async (paymentData) => {
  try {
    const result = await paymentAPI.charge(paymentData);
    return { success: true, data: result };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

// ✅ Higher-order functions for reusability
const withLogging = (fn, label) => (...args) => {
  console.time(label);
  const result = fn(...args);
  console.timeEnd(label);
  return result;
};

const withRetry = (fn, maxRetries = 3) => async (...args) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn(...args);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * i));
    }
  }
};

// ✅ Functional data transformation
const processUserData = (users) =>
  users
    .filter(user => user.isActive)
    .map(user => ({
      ...user,
      fullName: `${user.firstName} ${user.lastName}`,
      avatar: user.avatar || '/default-avatar.png'
    }))
    .sort((a, b) => a.lastName.localeCompare(b.lastName));

// ✅ Immutable state updates
const updateUser = (users, userId, updates) =>
  users.map(user =>
    user.id === userId
      ? { ...user, ...updates, updatedAt: new Date().toISOString() }
      : user
  );

// ✅ Async data fetching with error handling
const fetchUserData = async (userId) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 5000);

  try {
    const response = await fetch(`/api/users/${userId}`, {
      signal: controller.signal
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    if (error.name === 'AbortError') {
      return { success: false, error: 'Request timeout' };
    }
    return { success: false, error: error.message };
  } finally {
    clearTimeout(timeoutId);
  }
};
```

### 🎯 Modern JavaScript Features

- **Optional chaining**: `user?.profile?.avatar`
- **Nullish coalescing**: `name ?? 'Anonymous'`
- **BigInt**: For large integers beyond Number.MAX_SAFE_INTEGER
- **Dynamic imports**: `const module = await import('./feature.js')`
- **Private fields**: `#privateField` in classes (when classes are necessary)
- **Top-level await**: In modules and modern environments
- **Array methods**: `flatMap()`, `at()`, `findLast()`, `toSorted()`

**Remember**: Always prioritize readability, maintainability, and testability over clever one-liners or premature optimization.
