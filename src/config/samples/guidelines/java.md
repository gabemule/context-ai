<language_guidelines>

# ☕ Java Coding Guidelines

<header>
<language_name>Java</language_name>
<paradigm>Object-oriented programming with enterprise focus</paradigm>
<philosophy>Write once, run anywhere. Robust, secure, and maintainable enterprise applications</philosophy>
</header>

When providing Java code suggestions, follow these principles:

<core_principles>

### 📐 Architecture Principles

<solid_principles>
- **Single Responsibility**: Each class should have one reason to change
- **Open/Closed**: Classes open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable for their base types
- **Interface Segregation**: Many specific interfaces better than one general interface
- **Dependency Inversion**: Depend on abstractions, not concretions
</solid_principles>

<dry_principle>
- **Don't Repeat Yourself**: Extract common logic into methods/classes
- **Utility classes**: Create reusable utility methods
- **Inheritance and composition**: Share code through inheritance and composition
- **Generic programming**: Use generics for type-safe reusable code
</dry_principle>

<clean_code>
- **Meaningful names**: Use intention-revealing names for classes, methods, variables
- **Small functions**: Functions should do one thing and do it well
- **Clear abstractions**: Hide complexity behind well-defined interfaces
- **Consistent formatting**: Follow consistent code style throughout
</clean_code>

<yagni>
- **Simple design**: Start with simplest solution that works
- **Avoid over-engineering**: Don't build frameworks before you need them
- **Incremental complexity**: Add complexity only when required
</yagni>

</core_principles>

<language_specific>

### 🛠️ Java-Specific Best Practices

<best_practices>
- **Modern Java features**: Use latest Java features (Records, Switch expressions, etc.)
- **Stream API**: Prefer streams for data processing over traditional loops
- **Optional**: Use Optional to handle null values explicitly  
- **Immutability**: Favor immutable objects when possible
- **Builder pattern**: For objects with many parameters
- **Dependency injection**: Use Spring or similar frameworks for DI
</best_practices>

<idioms>
- **"Favor composition over inheritance"**: Use composition when possible
- **"Program to interfaces"**: Depend on interfaces, not implementations
- **"Fail fast"**: Validate parameters early and throw meaningful exceptions
- **"Use checked exceptions judiciously"**: For recoverable conditions only
- **"Prefer primitives to boxed primitives"**: For performance and simplicity
</idioms>

<performance>
- **JVM optimization**: Understand JVM behavior and garbage collection
- **String handling**: Use StringBuilder for multiple concatenations
- **Collection choice**: Choose appropriate collection types (ArrayList vs LinkedList)
- **Lazy initialization**: Initialize expensive objects only when needed
- **Connection pooling**: Reuse database connections and HTTP clients
</performance>

</language_specific>

### 🎨 Naming Conventions
- **Classes**: PascalCase (UserService, OrderController)
- **Methods/Variables**: camelCase (getUserById, totalPrice)
- **Constants**: SCREAMING_SNAKE_CASE (MAX_RETRY_COUNT)
- **Packages**: lowercase.with.dots (com.example.service)
- **Interfaces**: Often adjectives ending in -able or nouns (Readable, UserRepository)

### 🔍 Error Handling
- **Checked exceptions**: For recoverable conditions
- **Unchecked exceptions**: For programming errors
- **Custom exceptions**: Create domain-specific exception classes
- **Exception chaining**: Use cause parameter to preserve original exception
- **Resource management**: Use try-with-resources for automatic cleanup

### ⚡ Memory Management
- **Object lifecycle**: Understand object creation and garbage collection
- **Memory leaks**: Avoid holding references to objects no longer needed
- **Weak references**: Use for caches and observers
- **String interning**: Understand string pool behavior
- **Collection sizing**: Initialize collections with appropriate capacity

### 🏗️ Enterprise Patterns
- **MVC pattern**: Separate concerns in web applications
- **Repository pattern**: Abstract data access logic
- **Service layer**: Business logic separation
- **DTO pattern**: Data transfer between layers
- **Factory pattern**: Object creation encapsulation

<examples>

### 🌟 Examples of Good Practices

<good_practices>
```java
// ✅ Modern Java record for immutable data
public record User(
    Long id,
    String name,
    String email,
    LocalDateTime createdAt
) {
    public User {
        Objects.requireNonNull(id, "ID cannot be null");
        Objects.requireNonNull(name, "Name cannot be null");
        Objects.requireNonNull(email, "Email cannot be null");
        if (name.isBlank()) {
            throw new IllegalArgumentException("Name cannot be blank");
        }
    }
}

// ✅ Repository interface with clean API
public interface UserRepository {
    Optional<User> findById(Long id);
    List<User> findByEmail(String email);
    User save(User user);
    void deleteById(Long id);
    Page<User> findAll(Pageable pageable);
}

// ✅ Service class with dependency injection
@Service
@Transactional
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;
    
    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }
    
    public User createUser(CreateUserRequest request) {
        validateUserRequest(request);
        
        User user = new User(
            null,
            request.name(),
            request.email(),
            LocalDateTime.now()
        );
        
        User savedUser = userRepository.save(user);
        emailService.sendWelcomeEmail(savedUser);
        
        return savedUser;
    }
    
    public Optional<User> getUserById(Long id) {
        Objects.requireNonNull(id, "User ID cannot be null");
        return userRepository.findById(id);
    }
    
    private void validateUserRequest(CreateUserRequest request) {
        if (request.name().isBlank()) {
            throw new IllegalArgumentException("Name is required");
        }
        if (!isValidEmail(request.email())) {
            throw new IllegalArgumentException("Invalid email format");
        }
    }
    
    private boolean isValidEmail(String email) {
        return email.contains("@") && email.contains(".");
    }
}

// ✅ REST Controller with proper error handling
@RestController
@RequestMapping("/api/users")
@Validated
public class UserController {
    private final UserService userService;
    
    public UserController(UserService userService) {
        this.userService = userService;
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        return userService.getUserById(id)
            .map(user -> ResponseEntity.ok(user))
            .orElse(ResponseEntity.notFound().build());
    }
    
    @PostMapping
    public ResponseEntity<User> createUser(
        @Valid @RequestBody CreateUserRequest request
    ) {
        try {
            User user = userService.createUser(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(user);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    @GetMapping
    public ResponseEntity<Page<User>> getUsers(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size,
        @RequestParam(defaultValue = "id") String sort
    ) {
        Pageable pageable = PageRequest.of(page, size, Sort.by(sort));
        Page<User> users = userService.getAllUsers(pageable);
        return ResponseEntity.ok(users);
    }
}

// ✅ Configuration class with proper bean definitions
@Configuration
@EnableConfigurationProperties(AppProperties.class)
public class AppConfig {
    
    @Bean
    @ConditionalOnMissingBean
    public ObjectMapper objectMapper() {
        return new ObjectMapper()
            .registerModule(new JavaTimeModule())
            .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
            .setPropertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE);
    }
    
    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
            .setConnectTimeout(Duration.ofSeconds(10))
            .setReadTimeout(Duration.ofSeconds(30))
            .build();
    }
    
    @Bean
    @ConditionalOnProperty(name = "app.cache.enabled", havingValue = "true")
    public CacheManager cacheManager() {
        return new ConcurrentMapCacheManager("users", "orders");
    }
}

// ✅ Custom exception with proper inheritance
public class UserNotFoundException extends RuntimeException {
    private final Long userId;
    
    public UserNotFoundException(Long userId) {
        super(String.format("User with ID %d not found", userId));
        this.userId = userId;
    }
    
    public UserNotFoundException(Long userId, Throwable cause) {
        super(String.format("User with ID %d not found", userId), cause);
        this.userId = userId;
    }
    
    public Long getUserId() {
        return userId;
    }
}

// ✅ Utility class with private constructor
public final class ValidationUtils {
    private ValidationUtils() {
        throw new UnsupportedOperationException("Utility class");
    }
    
    public static boolean isValidEmail(String email) {
        return email != null && email.matches("^[A-Za-z0-9+_.-]+@(.+)$");
    }
    
    public static void requireNonBlank(String value, String fieldName) {
        Objects.requireNonNull(value, fieldName + " cannot be null");
        if (value.isBlank()) {
            throw new IllegalArgumentException(fieldName + " cannot be blank");
        }
    }
    
    public static <T extends Comparable<T>> void requireInRange(
        T value, T min, T max, String fieldName
    ) {
        Objects.requireNonNull(value, fieldName + " cannot be null");
        if (value.compareTo(min) < 0 || value.compareTo(max) > 0) {
            throw new IllegalArgumentException(
                String.format("%s must be between %s and %s", fieldName, min, max)
            );
        }
    }
}

// ✅ Stream API for data processing
public class OrderAnalytics {
    
    public Map<String, BigDecimal> calculateRevenueByCategory(List<Order> orders) {
        return orders.stream()
            .filter(order -> order.getStatus() == OrderStatus.COMPLETED)
            .flatMap(order -> order.getItems().stream())
            .collect(Collectors.groupingBy(
                OrderItem::getCategory,
                Collectors.reducing(
                    BigDecimal.ZERO,
                    OrderItem::getPrice,
                    BigDecimal::add
                )
            ));
    }
    
    public List<Customer> findTopCustomers(List<Order> orders, int limit) {
        return orders.stream()
            .collect(Collectors.groupingBy(
                Order::getCustomer,
                Collectors.reducing(
                    BigDecimal.ZERO,
                    Order::getTotal,
                    BigDecimal::add
                )
            ))
            .entrySet()
            .stream()
            .sorted(Map.Entry.<Customer, BigDecimal>comparingByValue().reversed())
            .limit(limit)
            .map(Map.Entry::getKey)
            .collect(Collectors.toList());
    }
}

// ✅ Builder pattern for complex objects
public class EmailMessage {
    private final String to;
    private final String subject;
    private final String body;
    private final List<String> cc;
    private final List<String> bcc;
    private final List<Attachment> attachments;
    private final Priority priority;
    
    private EmailMessage(Builder builder) {
        this.to = builder.to;
        this.subject = builder.subject;
        this.body = builder.body;
        this.cc = List.copyOf(builder.cc);
        this.bcc = List.copyOf(builder.bcc);
        this.attachments = List.copyOf(builder.attachments);
        this.priority = builder.priority;
    }
    
    public static Builder builder() {
        return new Builder();
    }
    
    public static class Builder {
        private String to;
        private String subject;
        private String body;
        private List<String> cc = new ArrayList<>();
        private List<String> bcc = new ArrayList<>();
        private List<Attachment> attachments = new ArrayList<>();
        private Priority priority = Priority.NORMAL;
        
        public Builder to(String to) {
            this.to = to;
            return this;
        }
        
        public Builder subject(String subject) {
            this.subject = subject;
            return this;
        }
        
        public Builder body(String body) {
            this.body = body;
            return this;
        }
        
        public Builder addCc(String cc) {
            this.cc.add(cc);
            return this;
        }
        
        public Builder priority(Priority priority) {
            this.priority = priority;
            return this;
        }
        
        public EmailMessage build() {
            Objects.requireNonNull(to, "Recipient is required");
            Objects.requireNonNull(subject, "Subject is required");
            Objects.requireNonNull(body, "Body is required");
            
            return new EmailMessage(this);
        }
    }
}
```
</good_practices>

<anti_patterns>
### 🚫 Anti-patterns to Avoid

```java
// ❌ Mutable data class with public fields
public class BadUser {
    public String name;
    public String email;
    public Date createdAt; // Mutable Date!
    
    // No validation, no encapsulation
}

// ✅ Better: use proper encapsulation or records
public class GoodUser {
    private final String name;
    private final String email;
    private final LocalDateTime createdAt;
    
    public GoodUser(String name, String email) {
        this.name = Objects.requireNonNull(name);
        this.email = Objects.requireNonNull(email);
        this.createdAt = LocalDateTime.now();
    }
    
    // Getters only, no setters for immutability
}

// ❌ Catching Exception instead of specific exceptions
try {
    processUser(user);
} catch (Exception e) { // Too broad!
    log.error("Something went wrong", e);
}

// ✅ Better: catch specific exceptions
try {
    processUser(user);
} catch (ValidationException e) {
    log.warn("User validation failed: {}", e.getMessage());
    throw new BadRequestException("Invalid user data");
} catch (DataAccessException e) {
    log.error("Database error while processing user", e);
    throw new ServiceUnavailableException("Service temporarily unavailable");
}

// ❌ String concatenation in loops
String result = "";
for (String item : items) {
    result += item + ", "; // Creates new string each time!
}

// ✅ Better: use StringBuilder or String.join()
StringBuilder sb = new StringBuilder();
for (String item : items) {
    sb.append(item).append(", ");
}
// Or even better:
String result = String.join(", ", items);

// ❌ Not using try-with-resources
FileInputStream fis = null;
try {
    fis = new FileInputStream("file.txt");
    // Process file
} finally {
    if (fis != null) {
        fis.close(); // Can throw exception!
    }
}

// ✅ Better: use try-with-resources
try (FileInputStream fis = new FileInputStream("file.txt")) {
    // Process file
    // Automatic cleanup
}

// ❌ Returning null instead of Optional
public User findUserById(Long id) {
    return userMap.get(id); // Can return null
}

// ✅ Better: use Optional
public Optional<User> findUserById(Long id) {
    return Optional.ofNullable(userMap.get(id));
}
```
</anti_patterns>

</examples>

<ecosystem>

### 🧪 Testing Philosophy

<testing>
- **JUnit 5**: Modern testing framework with parameterized tests
- **Mockito**: Mock external dependencies in unit tests
- **TestContainers**: Integration testing with real databases
- **AssertJ**: Fluent assertions for better readability
- **Spring Boot Test**: Integration testing for Spring applications
</testing>

### 📝 Documentation

<documentation>
- **Javadoc**: Document public APIs with proper @param, @return, @throws
- **README.md**: Project overview, setup instructions, examples
- **OpenAPI/Swagger**: API documentation for REST services
- **Architecture Decision Records**: Document important design decisions
</documentation>

### 🔧 Tools

<tools>
- **Maven/Gradle**: Build and dependency management
- **SonarQube**: Code quality analysis
- **SpotBugs**: Static analysis for bug detection
- **Checkstyle**: Code style enforcement
- **JaCoCo**: Code coverage analysis
- **Docker**: Containerization for deployment
</tools>

</ecosystem>

### 💡 Java Philosophy
- **"Write once, run anywhere"**: Platform independence through JVM
- **"Readability counts"**: Code should be self-documenting
- **"Robustness"**: Handle errors gracefully and recover when possible
- **"Security"**: Built-in security features and safe programming practices
- **"Performance"**: JVM optimizations make well-written Java fast
- **"Simplicity"**: Avoid unnecessary complexity

### 🔷 Advanced Patterns
- **Dependency Injection**: Use Spring Framework for IoC
- **Aspect-Oriented Programming**: Cross-cutting concerns with AOP
- **Reactive Programming**: Use Project Reactor for async processing
- **Event-Driven Architecture**: Decouple components with events
- **CQRS**: Separate read and write models for complex domains
- **Hexagonal Architecture**: Ports and adapters pattern

### 🚀 Performance Tips
- **Profile first**: Use JProfiler, YourKit, or JVM built-in profiling
- **GC tuning**: Understand and tune garbage collector settings
- **Connection pooling**: Reuse expensive resources like DB connections
- **Caching**: Use appropriate caching strategies (in-memory, distributed)
- **Async processing**: Use CompletableFuture for non-blocking operations
- **Bulk operations**: Batch database operations when possible

### 🌱 Spring Framework Best Practices
- **Constructor injection**: Prefer constructor over field injection
- **Configuration properties**: Use @ConfigurationProperties for external config
- **Profiles**: Use Spring profiles for environment-specific configuration
- **Actuator**: Monitor application health and metrics
- **Security**: Use Spring Security for authentication and authorization
- **Testing**: Use @SpringBootTest and test slices for efficient testing

**Remember**: Java excels in enterprise environments with its strong typing, robust ecosystem, and mature tooling. Focus on writing clean, maintainable code that leverages Java's strengths in object-oriented design and the rich Spring ecosystem.

</language_guidelines>
