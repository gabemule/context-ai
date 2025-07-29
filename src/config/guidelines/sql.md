<language_guidelines>

# 🗄️ SQL Coding Guidelines

<header>
<language_name>SQL</language_name>
<paradigm>Declarative database query language</paradigm>
<philosophy>Data integrity, performance, and maintainability</philosophy>
</header>

When providing SQL code suggestions, follow these principles:

<core_principles>

### 📐 Architecture Principles

<solid_principles>
- **Single Responsibility**: Each query/procedure should have one clear purpose
- **Interface Segregation**: Create focused, specific views and procedures
</solid_principles>

<dry_principle>
- **Don't Repeat Yourself**: Use CTEs, views, and functions for reusable logic
- **Common patterns**: Extract repeated query patterns into views
- **Parameterized queries**: Use parameters instead of string concatenation
- **Modular design**: Break complex queries into manageable parts
</dry_principle>

<clean_code>
- **Readable formatting**: Consistent indentation and keyword casing
- **Meaningful names**: Descriptive table, column, and alias names
- **Clear logic**: Well-structured WHERE clauses and JOINs
- **Documentation**: Comment complex queries and business logic
</clean_code>

</core_principles>

<language_specific>

### 🛠️ SQL-Specific Best Practices

<best_practices>
- **Consistent formatting**: Use standard SQL formatting conventions
- **Performance optimization**: Understand query execution plans
- **Data integrity**: Use constraints, foreign keys, and transactions
- **Parameterized queries**: Prevent SQL injection attacks
- **Indexing strategy**: Create indexes based on query patterns
- **Normalization**: Follow database normalization principles
</best_practices>

<idioms>
- **"Set-based thinking"**: Work with sets of data, not row-by-row
- **"Query what you need"**: Select only required columns and rows
- **"Join efficiently"**: Use appropriate join types and conditions
- **"Index for queries"**: Create indexes to support common query patterns
- **"Constrain data"**: Use database constraints for data integrity
</idioms>

<performance>
- **Query optimization**: Analyze execution plans and optimize bottlenecks
- **Proper indexing**: Create indexes on frequently queried columns
- **Efficient joins**: Use inner joins when possible, optimize join order
- **Limit result sets**: Use LIMIT/TOP and WHERE clauses effectively
- **Batch operations**: Use bulk operations for large data modifications
</performance>

</language_specific>

### 🎨 Naming Conventions
- **Tables**: PascalCase or snake_case (Users, user_profiles)
- **Columns**: snake_case (user_id, created_at, first_name)
- **Indexes**: Descriptive with prefix (idx_users_email, uk_users_username)  
- **Procedures**: Verb-noun pattern (sp_GetUserById, GetActiveUsers)
- **Functions**: Descriptive names (fn_CalculateAge, IsValidEmail)

### 🔍 Query Structure
- **Keywords**: UPPERCASE for SQL keywords (SELECT, FROM, WHERE)
- **Identifiers**: Consistent casing for table and column names
- **Aliases**: Short, meaningful aliases (u for users, p for products)
- **Indentation**: Consistent indentation for readability
- **Line breaks**: Strategic line breaks for complex queries

### ⚡ Performance Guidelines
- **Selective queries**: Use WHERE clauses to limit result sets
- **Proper joins**: Choose correct join types (INNER, LEFT, RIGHT)
- **Index usage**: Understand how indexes affect query performance
- **Avoid functions**: Don't use functions in WHERE clauses on large tables
- **Batch processing**: Process large datasets in smaller chunks

### 🎯 Data Integrity
- **Constraints**: Use PRIMARY KEY, FOREIGN KEY, CHECK constraints
- **Transactions**: Use transactions for data consistency
- **Validation**: Implement data validation at database level
- **Normalization**: Follow appropriate normal forms
- **Backup strategy**: Regular backups and recovery procedures

<examples>

### 🌟 Examples of Good Practices

<good_practices>
```sql
-- ✅ Well-formatted SELECT query
SELECT 
    u.user_id,
    u.username,
    u.email,
    p.first_name,
    p.last_name,
    p.created_at
FROM users u
INNER JOIN profiles p ON u.user_id = p.user_id
WHERE u.is_active = 1
    AND p.created_at >= '2024-01-01'
ORDER BY p.created_at DESC;

-- ✅ Common Table Expression (CTE)
WITH active_users AS (
    SELECT user_id, username, email
    FROM users
    WHERE is_active = 1
),
user_stats AS (
    SELECT 
        user_id,
        COUNT(*) as order_count,
        SUM(total_amount) as total_spent
    FROM orders
    WHERE order_date >= DATEADD(month, -12, GETDATE())
    GROUP BY user_id
)
SELECT 
    au.username,
    au.email,
    COALESCE(us.order_count, 0) as orders_last_year,
    COALESCE(us.total_spent, 0) as spent_last_year
FROM active_users au
LEFT JOIN user_stats us ON au.user_id = us.user_id
ORDER BY us.total_spent DESC;

-- ✅ Parameterized stored procedure
CREATE PROCEDURE sp_GetUserOrders
    @UserId INT,
    @StartDate DATE = NULL,
    @EndDate DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @DefaultStartDate DATE = DATEADD(month, -6, GETDATE());
    DECLARE @DefaultEndDate DATE = GETDATE();
    
    SELECT 
        o.order_id,
        o.order_date,
        o.total_amount,
        o.status,
        COUNT(oi.item_id) as item_count
    FROM orders o
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.user_id = @UserId
        AND o.order_date >= COALESCE(@StartDate, @DefaultStartDate)
        AND o.order_date <= COALESCE(@EndDate, @DefaultEndDate)
    GROUP BY o.order_id, o.order_date, o.total_amount, o.status
    ORDER BY o.order_date DESC;
END;

-- ✅ Efficient UPDATE with JOIN
UPDATE inventory 
SET quantity = inventory.quantity - oi.quantity
FROM inventory i
INNER JOIN order_items oi ON i.product_id = oi.product_id
INNER JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'confirmed'
    AND o.processed_date IS NULL;

-- ✅ Table creation with constraints
CREATE TABLE orders (
    order_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    order_date DATETIME2 NOT NULL DEFAULT GETDATE(),
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    
    CONSTRAINT FK_orders_users 
        FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT CK_orders_total_amount 
        CHECK (total_amount >= 0),
    CONSTRAINT CK_orders_status 
        CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled'))
);

-- ✅ Index creation
CREATE NONCLUSTERED INDEX idx_orders_user_date 
ON orders (user_id, order_date DESC)
INCLUDE (total_amount, status);
```
</good_practices>

<anti_patterns>
### 🚫 Anti-patterns to Avoid

```sql
-- ❌ SELECT * and poor formatting
select * from users where active=1;

-- ✅ Better: Specify columns and format properly
SELECT user_id, username, email
FROM users
WHERE is_active = 1;

-- ❌ String concatenation (SQL injection risk)
DECLARE @sql NVARCHAR(1000) = 'SELECT * FROM users WHERE username = ''' + @username + '''';

-- ✅ Better: Parameterized query
SELECT user_id, username, email
FROM users
WHERE username = @username;

-- ❌ Functions in WHERE clause
SELECT * FROM orders 
WHERE YEAR(order_date) = 2024;

-- ✅ Better: Range comparison
SELECT * FROM orders
WHERE order_date >= '2024-01-01' 
    AND order_date < '2025-01-01';
```
</anti_patterns>

</examples>

<ecosystem>

### 🧪 Testing Philosophy

<testing>
- **Unit tests**: Test stored procedures and functions individually
- **Data validation**: Test constraints and business rules
- **Performance tests**: Test query performance with realistic data volumes
- **Integration tests**: Test database interactions with applications
- **Regression tests**: Ensure changes don't break existing functionality
</testing>

### 📝 Documentation

<documentation>
- **Schema documentation**: Document table purposes and relationships
- **Query comments**: Explain complex business logic in queries
- **Procedure documentation**: Document parameters and return values
- **Data dictionary**: Maintain comprehensive column descriptions
</documentation>

### 🔧 Tools

<tools>
- **Query analyzers**: SQL Server Management Studio, MySQL Workbench
- **Performance tools**: Execution plan analyzers, query profilers
- **Version control**: Database schema versioning tools
- **Migration tools**: Database migration and deployment tools
- **Testing frameworks**: Database unit testing frameworks
</tools>

</ecosystem>

### 💡 SQL Philosophy
- **"Data is the foundation"**: Ensure data integrity and consistency
- **"Performance matters"**: Write efficient queries for large datasets
- **"Security first"**: Prevent SQL injection and unauthorized access
- **"Maintainability"**: Write readable, well-documented queries
- **"Set-based operations"**: Think in terms of data sets, not individual rows

### 🔷 Advanced Patterns
- **Window functions**: For analytical queries and ranking
- **Recursive CTEs**: For hierarchical data queries
- **Pivot/Unpivot**: For data transformation and reporting
- **Dynamic SQL**: For flexible query generation (use carefully)
- **Bulk operations**: For efficient large-scale data operations

### 🚀 Performance Tips
- **Indexing strategy**: Create indexes based on query patterns
- **Query optimization**: Use execution plans to identify bottlenecks
- **Partitioning**: For very large tables and improved performance
- **Statistics**: Keep database statistics up to date
- **Connection pooling**: Efficiently manage database connections
- **Caching**: Cache frequently accessed data when appropriate

**Remember**: SQL is about working with data efficiently and safely. Focus on data integrity, query performance, and security. Write readable queries, use proper constraints, and always use parameterized queries to prevent SQL injection.

</language_guidelines>
