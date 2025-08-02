<language_guidelines>

# ⚡ C/C++ Coding Guidelines

<header>
<language_name>C/C++</language_name>
<paradigm>Systems programming with manual memory management</paradigm>
<philosophy>Zero overhead principle, direct hardware control, and deterministic performance</philosophy>
</header>

When providing C/C++ code suggestions, follow these principles:

<core_principles>

### 📐 Architecture Principles

<solid_principles>
- **Single Responsibility**: Each function/class should have one clear purpose
- **Open/Closed**: Use inheritance and templates for extensibility
- **Liskov Substitution**: Derived classes should be substitutable for base classes
- **Interface Segregation**: Keep interfaces minimal and focused
- **Dependency Inversion**: Depend on abstractions (interfaces/templates)
</solid_principles>

<dry_principle>
- **Don't Repeat Yourself**: Use functions, templates, and macros judiciously
- **Template metaprogramming**: Generate code at compile time
- **Header organization**: Separate interface from implementation
- **Code reuse**: Create reusable libraries and components
</dry_principle>

<clean_code>
- **RAII (Resource Acquisition Is Initialization)**: Tie resource lifetime to object lifetime
- **Clear ownership**: Make ownership and lifetime explicit
- **Const correctness**: Use const wherever possible
- **Type safety**: Leverage the type system for correctness
</clean_code>

<yagni>
- **Avoid premature optimization**: Write clear code first, optimize later
- **Simple abstractions**: Don't over-engineer until complexity is needed
- **Minimal dependencies**: Only include what you actually use
</yagni>

</core_principles>

<language_specific>

### 🛠️ C/C++-Specific Best Practices

<best_practices>
- **Modern C++ features**: Use C++17/20 features (auto, range-based for, smart pointers)
- **RAII**: Automatic resource management through object lifetime
- **Smart pointers**: Use unique_ptr, shared_ptr instead of raw pointers
- **STL containers**: Prefer STL containers over C-style arrays
- **Move semantics**: Implement move constructors/assignment for efficiency
- **Exception safety**: Write exception-safe code with strong guarantees
</best_practices>

<idioms>
- **"Zero overhead principle"**: Don't pay for what you don't use
- **"RAII"**: Resource Acquisition Is Initialization
- **"Rule of Three/Five/Zero"**: Constructor, destructor, copy/move operations
- **"Prefer stack to heap"**: Stack allocation is faster and safer
- **"Make interfaces easy to use correctly and hard to use incorrectly"**
</idioms>

<performance>
- **Memory locality**: Structure data for cache efficiency
- **Minimize allocations**: Reuse objects, use object pools
- **Profile-guided optimization**: Measure before optimizing
- **Compiler optimizations**: Enable appropriate optimization flags
- **SIMD**: Use vectorization for data-parallel operations
</performance>

</language_specific>

### 🎨 Naming Conventions
- **Variables/Functions**: snake_case or camelCase (be consistent)
- **Classes/Types**: PascalCase
- **Constants**: SCREAMING_SNAKE_CASE
- **Macros**: SCREAMING_SNAKE_CASE
- **Namespaces**: lowercase
- **Private members**: Often prefixed with m_ or trailing _

### 🔍 Error Handling
- **Return codes**: Traditional C-style error handling
- **Exceptions**: C++ exceptions for exceptional conditions
- **Optional types**: std::optional for potentially missing values
- **Error categories**: Use std::error_code for system errors
- **RAII**: Ensure cleanup happens even during exceptions

### ⚡ Memory Management
- **Stack allocation**: Prefer automatic storage duration
- **Smart pointers**: unique_ptr for exclusive ownership, shared_ptr for shared
- **RAII**: Tie resource lifetime to object lifetime
- **Custom allocators**: For performance-critical applications
- **Memory pools**: Reduce allocation overhead

### 🧵 Concurrency Guidelines
- **std::thread**: Modern C++ threading
- **std::mutex**: Synchronization primitives
- **std::atomic**: Lock-free programming
- **Thread-local storage**: thread_local keyword
- **Lock-free data structures**: For high-performance scenarios

<examples>

### 🌟 Examples of Good Practices

<good_practices>
```cpp
// ✅ Modern C++ class with RAII and rule of five
class FileHandler {
private:
    std::unique_ptr<FILE, decltype(&fclose)> file_;
    std::string filename_;
    
public:
    // Constructor with RAII
    explicit FileHandler(const std::string& filename, const char* mode = "r")
        : file_(fopen(filename.c_str(), mode), &fclose)
        , filename_(filename) {
        if (!file_) {
            throw std::runtime_error("Failed to open file: " + filename);
        }
    }
    
    // Move constructor
    FileHandler(FileHandler&& other) noexcept
        : file_(std::move(other.file_))
        , filename_(std::move(other.filename_)) {
    }
    
    // Move assignment
    FileHandler& operator=(FileHandler&& other) noexcept {
        if (this != &other) {
            file_ = std::move(other.file_);
            filename_ = std::move(other.filename_);
        }
        return *this;
    }
    
    // Delete copy operations (unique ownership)
    FileHandler(const FileHandler&) = delete;
    FileHandler& operator=(const FileHandler&) = delete;
    
    // Destructor automatically called by unique_ptr
    ~FileHandler() = default;
    
    // Safe file operations
    bool write_line(const std::string& line) {
        if (!file_) return false;
        return fputs(line.c_str(), file_.get()) != EOF;
    }
    
    std::optional<std::string> read_line() {
        if (!file_) return std::nullopt;
        
        char buffer[1024];
        if (fgets(buffer, sizeof(buffer), file_.get())) {
            return std::string(buffer);
        }
        return std::nullopt;
    }
    
    const std::string& filename() const noexcept { return filename_; }
    bool is_open() const noexcept { return static_cast<bool>(file_); }
};

// ✅ Template class with perfect forwarding and SFINAE
template<typename T>
class CircularBuffer {
private:
    std::vector<T> buffer_;
    std::size_t head_ = 0;
    std::size_t tail_ = 0;
    std::size_t size_ = 0;
    
public:
    explicit CircularBuffer(std::size_t capacity) 
        : buffer_(capacity) {}
    
    // Perfect forwarding for efficient insertion
    template<typename U>
    void push(U&& value) {
        static_assert(std::is_convertible_v<U, T>, "Type must be convertible to T");
        
        buffer_[tail_] = std::forward<U>(value);
        tail_ = (tail_ + 1) % buffer_.size();
        
        if (size_ < buffer_.size()) {
            ++size_;
        } else {
            head_ = (head_ + 1) % buffer_.size();
        }
    }
    
    std::optional<T> pop() {
        if (empty()) {
            return std::nullopt;
        }
        
        T result = std::move(buffer_[head_]);
        head_ = (head_ + 1) % buffer_.size();
        --size_;
        
        return result;
    }
    
    [[nodiscard]] bool empty() const noexcept { return size_ == 0; }
    [[nodiscard]] bool full() const noexcept { return size_ == buffer_.size(); }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] std::size_t capacity() const noexcept { return buffer_.size(); }
};

// ✅ Smart pointer usage and factory functions
class NetworkConnection {
private:
    int socket_fd_;
    std::string host_;
    int port_;
    
    // Private constructor for factory pattern
    NetworkConnection(int fd, std::string host, int port)
        : socket_fd_(fd), host_(std::move(host)), port_(port) {}
    
public:
    ~NetworkConnection() {
        if (socket_fd_ >= 0) {
            close(socket_fd_);
        }
    }
    
    // Factory method
    static std::unique_ptr<NetworkConnection> create(const std::string& host, int port) {
        int fd = socket(AF_INET, SOCK_STREAM, 0);
        if (fd < 0) {
            return nullptr;
        }
        
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        
        if (inet_pton(AF_INET, host.c_str(), &addr.sin_addr) <= 0) {
            close(fd);
            return nullptr;
        }
        
        if (connect(fd, (sockaddr*)&addr, sizeof(addr)) < 0) {
            close(fd);
            return nullptr;
        }
        
        // Use private constructor
        return std::unique_ptr<NetworkConnection>(
            new NetworkConnection(fd, host, port)
        );
    }
    
    ssize_t send_data(const std::vector<uint8_t>& data) {
        if (socket_fd_ < 0) return -1;
        return send(socket_fd_, data.data(), data.size(), 0);
    }
    
    std::optional<std::vector<uint8_t>> receive_data(size_t max_size = 4096) {
        if (socket_fd_ < 0) return std::nullopt;
        
        std::vector<uint8_t> buffer(max_size);
        ssize_t bytes_received = recv(socket_fd_, buffer.data(), buffer.size(), 0);
        
        if (bytes_received <= 0) {
            return std::nullopt;
        }
        
        buffer.resize(bytes_received);
        return buffer;
    }
    
    // Non-copyable but movable
    NetworkConnection(const NetworkConnection&) = delete;
    NetworkConnection& operator=(const NetworkConnection&) = delete;
    NetworkConnection(NetworkConnection&&) = default;
    NetworkConnection& operator=(NetworkConnection&&) = default;
};

// ✅ Exception-safe class with strong exception guarantee
class SafeVector {
private:
    std::unique_ptr<int[]> data_;
    std::size_t size_;
    std::size_t capacity_;
    
    void reallocate(std::size_t new_capacity) {
        auto new_data = std::make_unique<int[]>(new_capacity);
        
        // Copy old data (this can throw)
        for (std::size_t i = 0; i < size_; ++i) {
            new_data[i] = data_[i];
        }
        
        // Only update state after successful allocation and copy
        data_ = std::move(new_data);
        capacity_ = new_capacity;
    }
    
public:
    SafeVector() : data_(nullptr), size_(0), capacity_(0) {}
    
    explicit SafeVector(std::size_t initial_capacity) 
        : data_(std::make_unique<int[]>(initial_capacity))
        , size_(0)
        , capacity_(initial_capacity) {}
    
    void push_back(int value) {
        if (size_ == capacity_) {
            reallocate(capacity_ == 0 ? 1 : capacity_ * 2);
        }
        
        data_[size_++] = value;
    }
    
    int& at(std::size_t index) {
        if (index >= size_) {
            throw std::out_of_range("Index out of range");
        }
        return data_[index];
    }
    
    const int& at(std::size_t index) const {
        if (index >= size_) {
            throw std::out_of_range("Index out of range");
        }
        return data_[index];
    }
    
    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] std::size_t capacity() const noexcept { return capacity_; }
    [[nodiscard]] bool empty() const noexcept { return size_ == 0; }
};

// ✅ Thread-safe singleton with std::once_flag
class Logger {
private:
    static std::unique_ptr<Logger> instance_;
    static std::once_flag once_flag_;
    
    std::mutex mutex_;
    std::ofstream log_file_;
    
    Logger() : log_file_("application.log", std::ios::app) {}
    
public:
    static Logger& get_instance() {
        std::call_once(once_flag_, []() {
            instance_ = std::unique_ptr<Logger>(new Logger());
        });
        return *instance_;
    }
    
    void log(const std::string& level, const std::string& message) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        
        log_file_ << "[" << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S")
                  << "] [" << level << "] " << message << std::endl;
        log_file_.flush();
    }
    
    void info(const std::string& message) { log("INFO", message); }
    void warning(const std::string& message) { log("WARNING", message); }
    void error(const std::string& message) { log("ERROR", message); }
    
    // Non-copyable, non-movable
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;
    Logger(Logger&&) = delete;
    Logger& operator=(Logger&&) = delete;
};

// Static member definitions
std::unique_ptr<Logger> Logger::instance_;
std::once_flag Logger::once_flag_;

// ✅ Modern C++ algorithm usage
#include <algorithm>
#include <numeric>
#include <execution>

class DataProcessor {
public:
    // Functional-style data processing
    static std::vector<int> process_data(const std::vector<int>& input) {
        std::vector<int> result;
        result.reserve(input.size());
        
        // Use STL algorithms instead of manual loops
        std::copy_if(input.begin(), input.end(), std::back_inserter(result),
                     [](int x) { return x % 2 == 0; });
        
        std::transform(result.begin(), result.end(), result.begin(),
                       [](int x) { return x * x; });
        
        std::sort(result.begin(), result.end());
        
        return result;
    }
    
    // Parallel processing with C++17 execution policies
    static double calculate_average(const std::vector<double>& data) {
        if (data.empty()) return 0.0;
        
        double sum = std::reduce(std::execution::par_unseq,
                                data.begin(), data.end(), 0.0);
        
        return sum / data.size();
    }
    
    // Range-based processing with C++20 ranges (if available)
    template<typename Range>
    static auto transform_and_filter(Range&& range) 
        -> std::vector<typename std::decay_t<Range>::value_type> {
        
        std::vector<typename std::decay_t<Range>::value_type> result;
        
        for (const auto& item : range) {
            if (item > 0) {
                result.push_back(item * 2);
            }
        }
        
        return result;
    }
};
```
</good_practices>

<anti_patterns>
### 🚫 Anti-patterns to Avoid

```cpp
// ❌ Raw pointer ownership (memory leak risk)
class BadClass {
    int* data;
public:
    BadClass(int size) : data(new int[size]) {} // Who owns this?
    ~BadClass() { /* Oops, forgot to delete[] */ }
};

// ✅ Better: use smart pointers or containers
class GoodClass {
    std::vector<int> data; // Automatic cleanup
public:
    GoodClass(int size) : data(size) {}
    // Destructor automatically generated
};

// ❌ Not following Rule of Three/Five
class BadResource {
    FILE* file;
public:
    BadResource(const char* name) : file(fopen(name, "r")) {}
    ~BadResource() { if (file) fclose(file); }
    // Missing copy constructor and assignment operator!
};

// ✅ Better: implement all or delete them
class GoodResource {
    std::unique_ptr<FILE, decltype(&fclose)> file;
public:
    GoodResource(const char* name) 
        : file(fopen(name, "r"), &fclose) {}
    
    // Delete copy operations for unique ownership
    GoodResource(const GoodResource&) = delete;
    GoodResource& operator=(const GoodResource&) = delete;
    
    // Move operations
    GoodResource(GoodResource&&) = default;
    GoodResource& operator=(GoodResource&&) = default;
};

// ❌ C-style casts
void* ptr = malloc(100);
int* bad_cast = (int*)ptr; // Dangerous!

// ✅ Better: use C++ casts
void* ptr = malloc(100);
int* good_cast = static_cast<int*>(ptr); // Explicit and safe

// ❌ Not using const
class BadAPI {
public:
    int get_value() { return value; } // Should be const!
    void print() { std::cout << value; } // Should be const!
private:
    int value = 42;
};

// ✅ Better: const correctness
class GoodAPI {
public:
    int get_value() const { return value; }
    void print() const { std::cout << value; }
private:
    int value = 42;
};

// ❌ Manual memory management when not needed
std::vector<int*> bad_vector;
for (int i = 0; i < 10; ++i) {
    bad_vector.push_back(new int(i)); // Memory leak waiting to happen
}

// ✅ Better: let containers manage memory
std::vector<int> good_vector;
for (int i = 0; i < 10; ++i) {
    good_vector.push_back(i); // Automatic cleanup
}
```
</anti_patterns>

</examples>

<ecosystem>

### 🧪 Testing Philosophy

<testing>
- **Google Test**: Modern C++ testing framework
- **Catch2**: Header-only testing framework
- **Unit tests**: Test individual functions and classes
- **Mock frameworks**: Google Mock for mocking dependencies
- **Memory testing**: Valgrind, AddressSanitizer for memory errors
</testing>

### 📝 Documentation

<documentation>
- **Doxygen**: Generate documentation from code comments
- **Header comments**: Document public interfaces thoroughly
- **README.md**: Build instructions, usage examples
- **Architecture docs**: High-level design documentation
</documentation>

### 🔧 Tools

<tools>
- **CMake**: Modern build system
- **Clang-format**: Code formatting
- **Clang-tidy**: Static analysis and linting
- **Valgrind**: Memory debugging and profiling
- **GDB/LLDB**: Debugging
- **Perf**: Performance profiling
</tools>

</ecosystem>

### 💡 C++ Philosophy
- **"Zero overhead principle"**: Don't pay for what you don't use
- **"Leave no room for a lower-level language below C++"**
- **"What you don't use, you don't pay for. What you do use, you couldn't hand code any better"**
- **"Type safety"**: Catch errors at compile time
- **"Resource management"**: RAII and automatic cleanup
- **"Performance"**: Direct hardware access and optimization

### 🔷 Advanced Patterns
- **Template metaprogramming**: Compile-time computation
- **CRTP (Curiously Recurring Template Pattern)**: Static polymorphism
- **Policy-based design**: Flexible component composition
- **Type erasure**: Runtime polymorphism without inheritance
- **Expression templates**: Optimize mathematical expressions
- **SFINAE**: Substitute Failure Is Not An Error

### 🚀 Performance Tips
- **Profile first**: Use profilers to identify bottlenecks
- **Memory locality**: Structure data for cache efficiency
- **Minimize allocations**: Reuse objects and use custom allocators
- **Compiler optimizations**: Enable -O2/-O3 and link-time optimization
- **SIMD instructions**: Vectorize data-parallel operations
- **Constexpr**: Compute at compile time when possible

### 🔒 Safety Guidelines
- **RAII**: Automatic resource management
- **Smart pointers**: Avoid raw pointer ownership
- **Const correctness**: Use const everywhere possible
- **Bounds checking**: Use .at() or range-checked access
- **Initialize variables**: Avoid uninitialized memory
- **Static analysis**: Use tools to catch common errors

### 🧵 Concurrency Best Practices
- **std::thread**: Modern threading primitives
- **RAII locks**: std::lock_guard, std::unique_lock
- **Atomic operations**: std::atomic for lock-free programming
- **Thread-safe initialization**: std::once_flag, std::call_once
- **Avoid data races**: Proper synchronization of shared data

**Remember**: C++ gives you the power to write high-performance, system-level code. With this power comes responsibility - manage resources carefully, embrace RAII, and leverage the type system for safety. Modern C++ features make the language much safer and more expressive while maintaining its performance advantages.

</language_guidelines>
