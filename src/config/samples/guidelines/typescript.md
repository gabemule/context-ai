<language_guidelines>

# 🔷 TypeScript Coding Guidelines

<header>
<language_name>TypeScript</language_name>
<paradigm>JavaScript + static type checking</paradigm>
<philosophy>Extends JavaScript guidelines with type safety and developer experience</philosophy>
</header>

**Inherits all JavaScript guidelines** with these TypeScript-specific additions:

<core_principles>

### 📐 TypeScript-Specific Principles

<type_safety>
- **Type-first development**: Define interfaces before implementation
- **Make impossible states impossible**: Use types to prevent invalid states
- **Fail at compile time**: Catch errors during development, not runtime
- **Type as documentation**: Let types document your code's contracts
</type_safety>

</core_principles>

<language_specific>

### 🛠️ TypeScript-Specific Best Practices

<best_practices>
- **Strict configuration**: Enable strict mode and all strict flags
- **Never use any**: Prefer unknown, proper types, or type assertions
- **Interfaces over types**: For object shapes that might be extended
- **Utility types**: Leverage Pick, Omit, Partial, Record, etc.
- **Generic constraints**: Use constraints to make generics safer
- **Discriminated unions**: For type-safe state management
</best_practices>

<idioms>
- **"Narrow, then widen"**: Start specific, generalize when needed
- **"Types are free at runtime"**: Use them liberally for safety
- **"Explicit over implicit"**: Prefer explicit type annotations for public APIs
</idioms>

</language_specific>

### 🎨 Type Design Guidelines
- **Interfaces**: For extensible object shapes
- **Type aliases**: For unions, primitives, and computed types
- **Generics**: For reusable, type-safe abstractions
- **Branded types**: For additional domain-specific type safety

### 🔍 Advanced TypeScript Features
- **Discriminated unions**: Type-safe state representation
- **Generic constraints**: `<T extends SomeType>`
- **Conditional types**: `T extends U ? X : Y`
- **Template literal types**: String pattern validation
- **Mapped types**: Transform object types

### ⚡ TypeScript Configuration
- **Strict mode**: Enable all strict compiler flags
- **No implicit any**: Require explicit type annotations
- **Null safety**: Handle null/undefined explicitly
- **Type assertions**: Use sparingly with type guards

<examples>

### 🌟 TypeScript-Specific Examples

```typescript
// ✅ Interfaces for extensible object shapes
interface User {
  readonly id: string;
  name: string;
  email: string;
  avatar?: string;
  createdAt: Date;
}

interface UserRepository extends Repository<User> {
  findByEmail(email: string): Promise<User | null>;
  updateLastLogin(userId: string): Promise<void>;
}

// ✅ Type aliases for unions and computations
type UserStatus = 'active' | 'inactive' | 'pending' | 'suspended';
type UserRole = 'admin' | 'moderator' | 'user' | 'guest';
type ApiResponse<T> = { success: true; data: T } | { success: false; error: string };

// ✅ Enums for constants (prefer const assertions when possible)
enum HttpStatus {
  OK = 200,
  CREATED = 201,
  BAD_REQUEST = 400,
  UNAUTHORIZED = 401,
  NOT_FOUND = 404,
  INTERNAL_SERVER_ERROR = 500
}

// ✅ Const assertions (preferred over enums for string constants)
const UserEvents = {
  CREATED: 'user.created',
  UPDATED: 'user.updated', 
  DELETED: 'user.deleted'
} as const;

type UserEvent = typeof UserEvents[keyof typeof UserEvents];

// ✅ Discriminated unions for type safety
type LoadingState = 
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: User[] }
  | { status: 'error'; error: string };

// ✅ Generic constraints
interface Repository<T extends { id: string }> {
  findById(id: string): Promise<T | null>;
  save(entity: T): Promise<T>;
  delete(id: string): Promise<boolean>;
}

// ✅ Branded types for domain safety
type UserId = string & { __brand: 'UserId' };
type Email = string & { __brand: 'Email' };
type Timestamp = number & { __brand: 'Timestamp' };

const createUserId = (id: string): UserId => id as UserId;
const createEmail = (email: string): Email => {
  if (!email.includes('@')) throw new Error('Invalid email');
  return email as Email;
};

// ✅ Utility types for transformations
type CreateUserRequest = Omit<User, 'id' | 'createdAt'>;
type UserUpdate = Partial<Pick<User, 'name' | 'email' | 'avatar'>>;
type UserKeys = keyof User;
type RequiredUser = Required<User>;

// ✅ Conditional types
type NonNullable<T> = T extends null | undefined ? never : T;
type ExtractArray<T> = T extends (infer U)[] ? U : never;

// ✅ Mapped types
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// ✅ Template literal types
type EventName<T extends string> = `on${Capitalize<T>}`;
type UserEventHandler = EventName<'click' | 'submit' | 'change'>;

// ✅ Function overloads
function processData(data: string): string;
function processData(data: number): number;
function processData(data: string | number): string | number {
  return typeof data === 'string' ? data.toUpperCase() : data * 2;
}
```

</examples>

**Remember**: TypeScript should enhance JavaScript with type safety, not complicate it. Focus on preventing runtime errors through compile-time checking.

</language_guidelines>
