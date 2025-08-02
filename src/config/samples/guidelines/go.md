<language_guidelines>

# 🐹 Go Coding Guidelines

<header>
<language_name>Go</language_name>
<paradigm>Procedural with concurrent programming</paradigm>
<philosophy>Simplicity, readability, and efficiency. "Less is more"</philosophy>
</header>

When providing Go code suggestions, follow these principles:

<core_principles>

### 📐 Architecture Principles

<solid_principles>
- **Single Responsibility**: Each function/package should have one clear purpose
- **Open/Closed**: Use interfaces for extensibility without modification
- **Liskov Substitution**: Interface implementations should be interchangeable
- **Interface Segregation**: Keep interfaces small and focused
- **Dependency Inversion**: Depend on interfaces, not concrete types
</solid_principles>

<dry_principle>
- **Don't Repeat Yourself**: Extract common logic into functions/packages
- **Use composition**: Embed types instead of inheritance
- **Create reusable packages**: Build modular, reusable components
</dry_principle>

<clean_code>
- **Simplicity over cleverness**: Write obvious, straightforward code
- **Clear naming**: Use descriptive names that explain intent
- **Short functions**: Keep functions focused and concise
- **Minimal interfaces**: Interface with only necessary methods
</clean_code>

<yagni>
- **Start simple**: Don't add features until needed
- **Avoid premature abstraction**: Let patterns emerge naturally
- **Minimize dependencies**: Only add what's necessary
</yagni>

</core_principles>

<language_specific>

### 🛠️ Go-Specific Best Practices

<best_practices>
- **Effective Go principles**: Follow the official Go guidelines
- **Goroutines and channels**: Use for concurrent programming
- **Error handling**: Explicit error handling, no exceptions
- **Package organization**: Group related functionality in packages
- **Zero values**: Design types with useful zero values
- **Receiver methods**: Use pointer receivers for mutations, value receivers for read-only
</best_practices>

<idioms>
- **"Don't communicate by sharing memory; share memory by communicating"**
- **Interface{} sparingly**: Use specific types when possible
- **Accept interfaces, return structs**: Function parameters as interfaces, return concrete types
- **Check errors**: Always handle errors explicitly
- **Use channels for coordination**: Sync goroutines with channels, not shared variables
</idioms>

<performance>
- **Efficient allocations**: Minimize heap allocations
- **Buffer reuse**: Reuse slices and buffers when possible
- **Profile first**: Use go tool pprof before optimizing
- **Concurrent design**: Leverage goroutines for I/O bound operations
</performance>

</language_specific>

### 🎨 Naming Conventions
- **Packages**: Short, lowercase, no underscores
- **Variables/Functions**: camelCase
- **Exported identifiers**: Start with uppercase letter
- **Acronyms**: ALL_CAPS (HTTP, URL, XML)
- **Interfaces**: Often end with -er (Reader, Writer, Stringer)

### 🔍 Error Handling
- **Explicit errors**: Return error as last value
- **Error wrapping**: Use fmt.Errorf with %w verb
- **Custom errors**: Implement error interface for domain-specific errors
- **Error checking**: Check every error, don't ignore
- **Fail fast**: Handle errors close to where they occur

### ⚡ Concurrency Guidelines
- **Channel ownership**: Clear ownership of channel lifecycle
- **Context usage**: Use context.Context for cancellation and timeouts
- **Worker pools**: For limiting concurrent operations
- **Select statements**: For multiplexing channel operations
- **Sync package**: Use sync.Mutex, sync.RWMutex for shared state

<examples>

### 🌟 Examples of Good Practices

<good_practices>
```go
// ✅ Clear interface definition
type UserRepository interface {
    GetUser(ctx context.Context, id string) (*User, error)
    SaveUser(ctx context.Context, user *User) error
}

// ✅ Struct with useful zero value
type Config struct {
    Host     string
    Port     int    // zero value (0) can be meaningful
    Debug    bool   // zero value (false) is useful default
    Timeout  time.Duration
}

// ✅ Constructor function
func NewConfig() *Config {
    return &Config{
        Host:    "localhost",
        Port:    8080,
        Timeout: 30 * time.Second,
    }
}

// ✅ Method with pointer receiver (mutation)
func (c *Config) SetDebug(debug bool) {
    c.Debug = debug
}

// ✅ Method with value receiver (read-only)
func (c Config) Address() string {
    return fmt.Sprintf("%s:%d", c.Host, c.Port)
}

// ✅ Proper error handling with wrapping
func (r *userRepository) GetUser(ctx context.Context, id string) (*User, error) {
    query := "SELECT name, email FROM users WHERE id = ?"
    row := r.db.QueryRowContext(ctx, query, id)
    
    var user User
    if err := row.Scan(&user.Name, &user.Email); err != nil {
        if err == sql.ErrNoRows {
            return nil, fmt.Errorf("user not found: %s", id)
        }
        return nil, fmt.Errorf("failed to get user %s: %w", id, err)
    }
    
    return &user, nil
}

// ✅ Concurrent processing with worker pool
func ProcessItems(ctx context.Context, items []Item) error {
    const maxWorkers = 10
    jobs := make(chan Item, len(items))
    results := make(chan error, len(items))
    
    // Start workers
    for i := 0; i < maxWorkers; i++ {
        go worker(ctx, jobs, results)
    }
    
    // Send jobs
    for _, item := range items {
        jobs <- item
    }
    close(jobs)
    
    // Collect results
    for i := 0; i < len(items); i++ {
        if err := <-results; err != nil {
            return fmt.Errorf("processing failed: %w", err)
        }
    }
    
    return nil
}

func worker(ctx context.Context, jobs <-chan Item, results chan<- error) {
    for job := range jobs {
        select {
        case <-ctx.Done():
            results <- ctx.Err()
            return
        default:
            results <- processItem(job)
        }
    }
}

// ✅ Table-driven tests
func TestCalculate(t *testing.T) {
    tests := []struct {
        name     string
        input    int
        expected int
        wantErr  bool
    }{
        {
            name:     "positive number",
            input:    5,
            expected: 25,
            wantErr:  false,
        },
        {
            name:    "negative number",
            input:   -1,
            wantErr: true,
        },
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := Calculate(tt.input)
            
            if tt.wantErr {
                assert.Error(t, err)
                return
            }
            
            assert.NoError(t, err)
            assert.Equal(t, tt.expected, result)
        })
    }
}

// ✅ Context usage for timeouts
func FetchData(ctx context.Context, url string) ([]byte, error) {
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, fmt.Errorf("creating request: %w", err)
    }
    
    client := &http.Client{Timeout: 10 * time.Second}
    resp, err := client.Do(req)
    if err != nil {
        return nil, fmt.Errorf("executing request: %w", err)
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("unexpected status: %d", resp.StatusCode)
    }
    
    data, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, fmt.Errorf("reading response: %w", err)
    }
    
    return data, nil
}
```
</good_practices>

<anti_patterns>
### 🚫 Anti-patterns to Avoid

```go
// ❌ Ignoring errors
result, _ := SomeFunction()  // DON'T ignore errors

// ❌ Empty interface{} when specific type is known
func Process(data interface{}) // Use specific types instead

// ❌ Goroutine without proper cleanup
go func() {
    // This goroutine might leak
    for {
        doWork()
    }
}()

// ❌ Shared mutable state without synchronization
var counter int // Multiple goroutines accessing without mutex

func increment() {
    counter++ // Race condition!
}

// ❌ Large interfaces
type Everything interface {
    Method1()
    Method2()
    Method3()
    Method4()
    Method5()
    // Too many methods!
}

// ❌ Not using context for cancellation
func LongRunningTask() {
    for {
        // No way to cancel this
        doWork()
    }
}
```
</anti_patterns>

</examples>

<ecosystem>

### 🧪 Testing Philosophy

<testing>
- **Table-driven tests**: Standard Go testing pattern
- **Testify**: Use github.com/stretchr/testify for assertions
- **Mock interfaces**: Use interfaces for testing with mocks
- **Benchmark tests**: Use testing.B for performance tests
- **Integration tests**: Use build tags to separate unit and integration tests
</testing>

### 📝 Documentation

<documentation>
- **Package documentation**: Comment package declaration
- **Function documentation**: Comment exported functions
- **Example tests**: Use Example functions for documentation
- **Go doc**: Generate documentation with go doc
</documentation>

### 🔧 Tools

<tools>
- **go fmt**: Format code automatically
- **go vet**: Static analysis for bugs
- **golint**: Style checker
- **go mod**: Dependency management
- **go test**: Testing framework
- **pprof**: Performance profiling
</tools>

</ecosystem>

### 💡 Go Proverbs
- **"Don't communicate by sharing memory, share memory by communicating"**
- **"Concurrency is not parallelism"**
- **"Channels orchestrate; mutexes serialize"**
- **"The bigger the interface, the weaker the abstraction"**
- **"Make the zero value useful"**
- **"interface{} says nothing"**
- **"Gofmt's style is no one's favorite, yet gofmt is everyone's favorite"**
- **"A little copying is better than a little dependency"**
- **"Syscall must always be guarded with build tags"**
- **"Clear is better than clever"**
- **"Reflection is never clear"**
- **"Errors are values"**
- **"Don't just check errors, handle them gracefully"**

### 🔷 Advanced Patterns
- **Functional options**: For configurable constructors
- **Pipeline pattern**: Chain operations with channels
- **Fan-in/Fan-out**: Distribute work across multiple goroutines
- **Circuit breaker**: Handle service failures gracefully
- **Context propagation**: Pass request-scoped values and cancellation

**Remember**: Go values simplicity, readability, and explicit error handling. Write code that is easy to understand and maintain, leveraging Go's strengths in concurrency and simplicity.

</language_guidelines>
