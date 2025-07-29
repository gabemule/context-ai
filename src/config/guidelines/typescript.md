## 🔷 TypeScript Coding Guidelines

Extends JavaScript guidelines with TypeScript-specific best practices:

### 🔷 TypeScript Specific Guidelines

- **Strict mode**: Enable strict TypeScript configuration
- **Type-first**: Define types/interfaces before implementation
- **Utility types**: Use built-in utility types (Pick, Omit, Partial, etc.)
- **Generic constraints**: Use constraints to make generics safer
- **Branded types**: For additional type safety
- **Discriminated unions**: For type-safe state management
- **Never use `any`**: Prefer `unknown` or proper typing

### 🎯 Type Design Principles

- **Prefer interfaces over types** for object shapes that might be extended
- **Use type aliases** for union types, primitives, and computed types
- **Make impossible states impossible** through careful type design
- **Leverage the type system** to prevent runtime errors

### 🛠️ Advanced TypeScript Patterns

```typescript
// ✅ Discriminated unions for type safety
type LoadingState = 
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: any }
  | { status: 'error'; error: string };

// ✅ Generic constraints
interface Repository<T extends { id: string }> {
  findById(id: string): Promise<T | null>;
  save(entity: T): Promise<T>;
}

// ✅ Branded types for additional safety
type UserId = string & { __brand: 'UserId' };
type Email = string & { __brand: 'Email' };

const createUserId = (id: string): UserId => id as UserId;
const createEmail = (email: string): Email => {
  if (!email.includes('@')) throw new Error('Invalid email');
  return email as Email;
};

// ✅ Utility types for transformations
type CreateUserRequest = Omit<User, 'id' | 'createdAt' | 'updatedAt'>;
type UserUpdate = Partial<Pick<User, 'name' | 'email' | 'avatar'>>;

// ✅ Conditional types for advanced logic
type NonNullable<T> = T extends null | undefined ? never : T;
type ApiResponse<T> = T extends string 
  ? { message: T } 
  : { data: T };
```

### 📝 Type Documentation

- **Document complex types** with JSDoc comments
- **Use meaningful type names** that explain intent
- **Export types** that external consumers might need
- **Group related types** in dedicated files

### 🚫 TypeScript Anti-patterns

- **Avoid `any`**: Use `unknown`, proper types, or type assertions
- **Don't over-type**: Simple cases don't need complex type gymnastics
- **Avoid deep nesting**: Keep type definitions readable
- **Don't ignore compiler errors**: Fix them properly

**Remember**: TypeScript should make your code more reliable and maintainable, not more complex.
