<language_guidelines>

# 🦀 Rust Coding Guidelines

<header>
<language_name>Rust</language_name>
<paradigm>Systems programming with memory safety</paradigm>
<philosophy>Zero-cost abstractions, memory safety, and fearless concurrency</philosophy>
</header>

When providing Rust code suggestions, follow these principles:

<core_principles>

### 📐 Architecture Principles

<solid_principles>
- **Single Responsibility**: Each function/module should have one clear purpose
- **Open/Closed**: Use traits for extensibility without modification
- **Liskov Substitution**: Trait implementations should be interchangeable
- **Interface Segregation**: Keep traits small and focused
- **Dependency Inversion**: Depend on traits, not concrete types
</solid_principles>

<dry_principle>
- **Don't Repeat Yourself**: Use macros, generics, and modules for reusability
- **Generic programming**: Write code that works with multiple types
- **Macro system**: Generate repetitive code with macros
- **Module organization**: Group related functionality in modules
</dry_principle>

<clean_code>
- **Explicit over implicit**: Make intentions clear in code
- **Type safety**: Leverage Rust's type system for correctness
- **Error handling**: Use Result<T, E> for fallible operations
- **Ownership clarity**: Make ownership and borrowing explicit
</clean_code>

<yagni>
- **Start with concrete types**: Add generics when needed
- **Avoid premature optimization**: Profile before optimizing
- **Simple error types**: Start with basic errors, add detail as needed
</yagni>

</core_principles>

<language_specific>

### 🛠️ Rust-Specific Best Practices

<best_practices>
- **Ownership system**: Understand borrowing, moving, and lifetimes
- **Zero-cost abstractions**: Write high-level code with low-level performance
- **Pattern matching**: Use match and if-let for control flow
- **Error handling**: Prefer Result<T, E> over panicking
- **Iterator chains**: Use iterators for data transformation
- **Trait system**: Define shared behavior with traits
</best_practices>

<idioms>
- **"Zero-cost abstractions"**: High-level constructs with no runtime overhead
- **"Fearless concurrency"**: Memory safety prevents data races
- **"Move by default"**: Values are moved unless explicitly borrowed
- **"Fail fast"**: Use panic! for unrecoverable errors, Result for recoverable ones
- **"Iterator over indexing"**: Prefer iterator methods over manual indexing
</idioms>

<performance>
- **Stack allocation**: Prefer stack over heap when possible
- **Borrowing over cloning**: Use references to avoid unnecessary copies
- **Iterator chains**: Often faster than manual loops due to optimization
- **SIMD**: Use explicit SIMD or let compiler auto-vectorize
- **Profile-guided optimization**: Use cargo flamegraph and perf
</performance>

</language_specific>

### 🎨 Naming Conventions
- **Modules/functions/variables**: snake_case
- **Types/Traits/Enums**: PascalCase
- **Constants/Statics**: SCREAMING_SNAKE_CASE
- **Lifetime parameters**: 'a, 'b, 'c (short and descriptive)
- **Type parameters**: T, U, V (single letters) or descriptive names

### 🔍 Error Handling
- **Result<T, E>**: For recoverable errors
- **Option<T>**: For nullable values
- **? operator**: For early returns in fallible functions
- **Custom error types**: Implement std::error::Error trait
- **Error propagation**: Use ? operator or combinators

### ⚡ Memory Management
- **Ownership**: Each value has a single owner
- **Borrowing**: Immutable and mutable references
- **Lifetimes**: Ensure references are valid
- **RAII**: Resources cleaned up automatically
- **Smart pointers**: Box<T>, Rc<T>, Arc<T> for heap allocation

### 🧵 Concurrency Guidelines
- **Send + Sync**: Traits for thread safety
- **Arc<Mutex<T>>**: Shared mutable state
- **Channels**: Message passing between threads
- **Async/await**: For asynchronous programming
- **Rayon**: Data parallelism with work-stealing

<examples>

### 🌟 Examples of Good Practices

<good_practices>
```rust
// ✅ Clear trait definition with associated types
trait Repository {
    type Item;
    type Error;
    
    fn find_by_id(&self, id: u64) -> Result<Option<Self::Item>, Self::Error>;
    fn save(&mut self, item: Self::Item) -> Result<(), Self::Error>;
}

// ✅ Struct with owned data and clear ownership
#[derive(Debug, Clone)]
pub struct User {
    pub id: u64,
    pub name: String,
    pub email: String,
}

// ✅ Builder pattern with consuming methods
pub struct UserBuilder {
    id: Option<u64>,
    name: Option<String>,
    email: Option<String>,
}

impl UserBuilder {
    pub fn new() -> Self {
        Self {
            id: None,
            name: None,
            email: None,
        }
    }
    
    pub fn id(mut self, id: u64) -> Self {
        self.id = Some(id);
        self
    }
    
    pub fn name(mut self, name: impl Into<String>) -> Self {
        self.name = Some(name.into());
        self
    }
    
    pub fn email(mut self, email: impl Into<String>) -> Self {
        self.email = Some(email.into());
        self
    }
    
    pub fn build(self) -> Result<User, BuildError> {
        Ok(User {
            id: self.id.ok_or(BuildError::MissingField("id"))?,
            name: self.name.ok_or(BuildError::MissingField("name"))?,
            email: self.email.ok_or(BuildError::MissingField("email"))?,
        })
    }
}

// ✅ Custom error type with good practices
#[derive(Debug, thiserror::Error)]
pub enum BuildError {
    #[error("Missing required field: {0}")]
    MissingField(&'static str),
    #[error("Invalid email format: {0}")]
    InvalidEmail(String),
}

// ✅ Generic function with trait bounds
fn process_items<T, F, R>(items: Vec<T>, processor: F) -> Vec<R>
where
    F: Fn(T) -> R,
{
    items.into_iter().map(processor).collect()
}

// ✅ Proper error handling with ?
async fn fetch_user_data(client: &HttpClient, user_id: u64) -> Result<UserData, AppError> {
    let response = client
        .get(&format!("/users/{}", user_id))
        .send()
        .await?;
    
    if !response.status().is_success() {
        return Err(AppError::HttpError(response.status()));
    }
    
    let user_data: UserData = response.json().await?;
    Ok(user_data)
}

// ✅ Iterator chains for data processing
fn analyze_sales_data(sales: Vec<Sale>) -> SalesReport {
    let total_revenue: f64 = sales
        .iter()
        .filter(|sale| sale.status == Status::Completed)
        .map(|sale| sale.amount)
        .sum();
    
    let top_products: Vec<_> = sales
        .iter()
        .fold(HashMap::new(), |mut acc, sale| {
            *acc.entry(&sale.product_id).or_insert(0) += 1;
            acc
        })
        .into_iter()
        .sorted_by(|a, b| b.1.cmp(&a.1))
        .take(10)
        .collect();
    
    SalesReport {
        total_revenue,
        top_products,
        total_sales: sales.len(),
    }
}

// ✅ Pattern matching with exhaustive cases
fn handle_request(request: Request) -> Response {
    match request {
        Request::Get { path, .. } => handle_get(path),
        Request::Post { path, body, .. } => handle_post(path, body),
        Request::Put { path, body, .. } => handle_put(path, body),
        Request::Delete { path, .. } => handle_delete(path),
        Request::Options { .. } => Response::ok().header("Allow", "GET,POST,PUT,DELETE"),
        _ => Response::method_not_allowed(),
    }
}

// ✅ Safe concurrency with Arc and Mutex
use std::sync::{Arc, Mutex};
use std::thread;

fn concurrent_counter() -> i32 {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];
    
    for _ in 0..10 {
        let counter_clone = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for _ in 0..100 {
                let mut num = counter_clone.lock().unwrap();
                *num += 1;
            }
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    *counter.lock().unwrap()
}

// ✅ Async function with proper error handling
use tokio::fs;
use tokio::io::AsyncWriteExt;

async fn save_data_atomically(
    file_path: &Path,
    data: &[u8],
) -> Result<(), std::io::Error> {
    let temp_path = file_path.with_extension("tmp");
    
    // Write to temporary file first
    let mut file = fs::File::create(&temp_path).await?;
    file.write_all(data).await?;
    file.flush().await?;
    drop(file); // Ensure file is closed
    
    // Atomically move to final location
    fs::rename(temp_path, file_path).await?;
    
    Ok(())
}

// ✅ Zero-cost abstraction with const generics
struct Matrix<T, const ROWS: usize, const COLS: usize> {
    data: [[T; COLS]; ROWS],
}

impl<T, const ROWS: usize, const COLS: usize> Matrix<T, ROWS, COLS>
where
    T: Copy + Default + std::ops::Add<Output = T>,
{
    fn new() -> Self {
        Self {
            data: [[T::default(); COLS]; ROWS],
        }
    }
    
    fn add(&self, other: &Self) -> Self {
        let mut result = Self::new();
        for i in 0..ROWS {
            for j in 0..COLS {
                result.data[i][j] = self.data[i][j] + other.data[i][j];
            }
        }
        result
    }
}
```
</good_practices>

<anti_patterns>
### 🚫 Anti-patterns to Avoid

```rust
// ❌ Unnecessary cloning
fn bad_process_strings(strings: &Vec<String>) -> Vec<String> {
    strings.iter().map(|s| s.clone()).collect() // Unnecessary clones
}

// ✅ Better: work with references
fn good_process_strings(strings: &[String]) -> Vec<&str> {
    strings.iter().map(|s| s.as_str()).collect()
}

// ❌ Using unwrap() in library code
fn bad_parse_config(json: &str) -> Config {
    serde_json::from_str(json).unwrap() // Can panic!
}

// ✅ Better: return Result
fn good_parse_config(json: &str) -> Result<Config, ConfigError> {
    serde_json::from_str(json).map_err(ConfigError::ParseError)
}

// ❌ Inefficient string operations
fn bad_concatenate(strings: Vec<&str>) -> String {
    let mut result = String::new();
    for s in strings {
        result = result + s; // Creates new string each time
    }
    result
}

// ✅ Better: use push_str or collect
fn good_concatenate(strings: Vec<&str>) -> String {
    strings.concat() // or strings.join("")
}

// ❌ Borrowing when you could move
fn bad_take_ownership(data: &Vec<i32>) -> ProcessedData {
    process_data(data.clone()) // Unnecessary clone
}

// ✅ Better: take ownership when appropriate
fn good_take_ownership(data: Vec<i32>) -> ProcessedData {
    process_data(data) // Move the data
}

// ❌ Large enums without Box
enum BadLargeEnum {
    Small(i32),
    Large([u8; 1024]), // Makes entire enum large
}

// ✅ Better: Box large variants
enum GoodLargeEnum {
    Small(i32),
    Large(Box<[u8; 1024]>), // Only allocate when needed
}
```
</anti_patterns>

</examples>

<ecosystem>

### 🧪 Testing Philosophy

<testing>
- **Unit tests**: Test individual functions with #[cfg(test)]
- **Integration tests**: Place in tests/ directory
- **Property testing**: Use proptest for property-based testing
- **Benchmark tests**: Use criterion crate for benchmarking
- **Doc tests**: Test examples in documentation
</testing>

### 📝 Documentation

<documentation>
- **/// comments**: Document public APIs
- **//! comments**: Document modules and crates
- **Examples**: Include usage examples in docs
- **cargo doc**: Generate HTML documentation
- **README.md**: Crate overview and quick start
</documentation>

### 🔧 Tools

<tools>
- **rustfmt**: Code formatting
- **clippy**: Linting and suggestions
- **cargo**: Build system and package manager
- **rustc**: The Rust compiler
- **cargo-audit**: Security vulnerability scanning
- **cargo-outdated**: Check for outdated dependencies
</tools>

</ecosystem>

### 💡 Rust Philosophy
- **"Zero-cost abstractions"**: You don't pay for what you don't use
- **"Memory safety without garbage collection"**: Compile-time memory management
- **"Fearless concurrency"**: Safe parallel programming
- **"If it compiles, it (usually) works"**: Strong type system catches bugs
- **"Fast, reliable, productive—pick three"**: You can have all three
- **"Explicit is better than implicit"**: Make intentions clear
- **"Composition over inheritance"**: Use traits and generics

### 🔷 Advanced Patterns
- **Type-level programming**: Use const generics and phantom types
- **RAII guards**: Automatic resource cleanup
- **Interior mutability**: Cell<T>, RefCell<T>, Mutex<T>
- **Async traits**: Trait objects with async methods
- **Procedural macros**: Custom derive and attribute macros
- **Unsafe code**: When you need to break the rules (carefully)

### 🚀 Performance Tips
- **Profile first**: Use cargo flamegraph and perf
- **Avoid allocations**: Use references and borrowing
- **Iterator chains**: Often faster than manual loops
- **SIMD**: Use std::simd or external crates
- **Const evaluation**: Compute at compile time when possible
- **Inlining**: Use #[inline] for small, hot functions

### 🔒 Safety Guidelines
- **Minimize unsafe**: Use only when absolutely necessary
- **Document safety**: Explain safety invariants in unsafe code
- **Encapsulate unsafe**: Wrap in safe APIs
- **Test thoroughly**: Unsafe code needs extra testing
- **Use sanitizers**: AddressSanitizer, ThreadSanitizer, etc.

**Remember**: Rust's strength lies in its ability to provide zero-cost abstractions while maintaining memory safety. Embrace the ownership system, leverage the type system for correctness, and write code that is both safe and performant.

</language_guidelines>
