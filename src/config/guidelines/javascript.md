<language_guidelines>

# ⚡ JavaScript Coding Guidelines

<header>
<language_name>JavaScript</language_name>
<paradigm>Functional-first programming with ES6+ features</paradigm>
<philosophy>Immutable, composable, and declarative code</philosophy>
</header>

When providing JavaScript code suggestions, follow these principles:

<core_principles>

### 📐 Architecture Principles

<solid_principles>
- **Single Responsibility**: Each function should have one clear purpose
- **Open/Closed**: Use higher-order functions and composition for extensibility
- **Dependency Inversion**: Depend on abstractions through function parameters
</solid_principles>

<dry_principle>
- **Don't Repeat Yourself**: Use higher-order functions and composition
- **Functional composition**: Break complex logic into small, reusable functions
- **Shared utilities**: Extract common patterns to utility functions
- **Module reusability**: Create composable modules and functions
</dry_principle>

<clean_code>
- **Meaningful names**: Use descriptive function and variable names
- **Pure functions**: Functions without side effects and predictable outputs
- **Small functions**: Keep functions focused and testable
- **Declarative style**: Express what, not how
</clean_code>

<yagni>
- **Start simple**: Don't implement features until they're actually needed
- **Avoid over-abstraction**: Keep solutions simple until complexity is required
- **Progressive enhancement**: Build basic functionality first, enhance later
</yagni>

</core_principles>

<language_specific>

### 🛠️ JavaScript-Specific Best Practices

<best_practices>
- **Functional programming**: Prefer functions over classes for most use cases
- **Immutability**: Use const, avoid mutations, prefer pure functions
- **ES6+ features**: Arrow functions, destructuring, template literals
- **Async/await**: Modern asynchronous programming patterns
- **Module system**: ES6 imports/exports with named exports preferred
- **Error handling**: Explicit error handling with Result/Either patterns
</best_practices>

<idioms>
- **"Functions first"**: Use functions and composition over classes
- **"Immutable by default"**: Avoid mutations, use pure functions
- **"Compose don't inherit"**: Build complexity through function composition
- **"Explicit is better"**: Make side effects and dependencies explicit
- **"Fail fast"**: Validate inputs early and throw meaningful errors
</idioms>

<performance>
- **Lazy evaluation**: Load and compute only when needed
- **Memoization**: Cache expensive computations
- **Event optimization**: Debounce/throttle frequent events
- **Bundle optimization**: Tree shaking and code splitting
- **Memory management**: Clean up event listeners and subscriptions
</performance>

</language_specific>

### 🎨 Naming Conventions
- **Functions/variables**: camelCase (getUserData, isValid)
- **Constants**: SCREAMING_SNAKE_CASE (API_BASE_URL, MAX_RETRIES)
- **Classes**: PascalCase (only when necessary - UserService, ApiClient)
- **Files**: kebab-case (user-service.js, api-client.js)
- **Descriptive names**: Express intent clearly (calculateTotal vs calc)

### 🔍 Functional Programming Guidelines
- **Pure functions**: No side effects, same input = same output
- **Immutability**: Don't mutate data, return new copies
- **Higher-order functions**: Functions that take/return other functions
- **Function composition**: Build complex logic from simple functions
- **Avoid classes**: Use functions and closures for encapsulation

### ⚡ Modern JavaScript Features
- **Arrow functions**: Preferred for most function expressions
- **Destructuring**: Clean object/array property extraction
- **Template literals**: String interpolation with backticks
- **Optional chaining**: Safe property access with `?.`
- **Nullish coalescing**: Use `??` for null/undefined checks
- **Async/await**: Modern promise handling

### 🎯 Error Handling Patterns
- **Result/Either pattern**: Return success/error objects instead of throwing
- **Explicit error handling**: Always handle errors explicitly
- **Meaningful errors**: Include context and actionable information
- **Fail fast**: Validate inputs early in function execution
- **No silent failures**: Don't ignore or suppress errors

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
