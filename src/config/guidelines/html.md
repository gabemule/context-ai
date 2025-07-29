<language_guidelines>

# 🌐 HTML Coding Guidelines

<header>
<language_name>HTML</language_name>
<paradigm>Semantic markup for structured content</paradigm>
<philosophy>Semantic, accessible, and performance-optimized web content</philosophy>
</header>

When providing HTML code suggestions, follow these principles:

<core_principles>

### 📐 Architecture Principles

<solid_principles>
- **Single Responsibility**: Each element should have one clear semantic purpose
- **Open/Closed**: Use semantic elements that can be extended with CSS/JS
- **Liskov Substitution**: Semantic elements should be interchangeable in context
- **Interface Segregation**: Use specific semantic elements rather than generic divs
- **Dependency Inversion**: Depend on semantic meaning, not visual presentation
</solid_principles>

<dry_principle>
- **Don't Repeat Yourself**: Use components, templates, and includes
- **Semantic reusability**: Create reusable semantic patterns
- **Template systems**: Use templating engines for dynamic content
- **Component-based architecture**: Build reusable UI components
</dry_principle>

<clean_code>
- **Semantic HTML**: Use elements for their intended meaning
- **Clear structure**: Logical document outline and hierarchy
- **Readable markup**: Proper indentation and meaningful attributes
- **Accessibility first**: Built-in accessibility from the start
</clean_code>

<yagni>
- **Progressive enhancement**: Start with basic HTML, enhance with CSS/JS
- **Minimal markup**: Don't add elements until they serve a purpose
- **Simple structure**: Avoid unnecessary nesting and complexity
</yagni>

</core_principles>

<language_specific>

### 🛠️ HTML-Specific Best Practices

<best_practices>
- **Semantic HTML5**: Use appropriate semantic elements (article, section, nav, etc.)
- **Accessibility**: ARIA attributes, alt text, proper heading hierarchy
- **Performance**: Minimize DOM size, optimize images, preload critical resources
- **SEO**: Proper meta tags, structured data, semantic markup
- **Progressive enhancement**: Work without CSS/JavaScript
- **Web standards**: Valid HTML5, modern best practices
</best_practices>

<idioms>
- **"Content first"**: Structure content semantically before styling
- **"Progressive enhancement"**: Basic functionality without CSS/JS
- **"Accessibility by design"**: Built-in accessibility, not retrofitted
- **"Mobile first"**: Design for mobile devices first
- **"Performance budget"**: Every element should justify its existence
</idioms>

<performance>
- **Critical rendering path**: Optimize above-the-fold content
- **Resource hints**: Use preload, prefetch, preconnect
- **Image optimization**: Proper formats, sizes, and lazy loading
- **Minimal DOM**: Reduce number of elements and nesting
- **Efficient selectors**: Structure for efficient CSS targeting
</performance>

</language_specific>

### 🎨 Naming Conventions
- **IDs**: kebab-case, unique per page (main-navigation, hero-section)
- **Classes**: kebab-case, reusable (button-primary, card-content)
- **Data attributes**: data-kebab-case (data-toggle-state)
- **BEM methodology**: block__element--modifier
- **Semantic naming**: Describe meaning, not appearance

### 🔍 Accessibility Guidelines
- **Semantic structure**: Use proper heading hierarchy (h1-h6)
- **ARIA labels**: Provide labels for complex interactions
- **Alt text**: Descriptive alternative text for images
- **Focus management**: Proper tab order and focus indicators
- **Screen reader support**: Test with screen readers

### ⚡ Performance Optimization
- **Critical CSS**: Inline critical CSS for above-the-fold content
- **Resource loading**: Preload important resources, lazy load others
- **Image optimization**: Use appropriate formats and sizes
- **Minimize requests**: Combine resources when beneficial
- **Caching strategy**: Proper cache headers and versioning

### 🏗️ Document Structure
- **DOCTYPE**: Always use HTML5 DOCTYPE
- **Language**: Specify document language
- **Meta tags**: Viewport, charset, description
- **Heading hierarchy**: Logical h1-h6 structure
- **Landmark roles**: nav, main, aside, footer

<ecosystem>

### 🧪 Testing Philosophy

<testing>
- **HTML validation**: Use W3C Markup Validator
- **Accessibility testing**: Screen readers, axe-core, Lighthouse
- **Performance testing**: PageSpeed Insights, WebPageTest
- **Cross-browser testing**: Test in multiple browsers and devices
- **Responsive testing**: Test across different screen sizes
</testing>

### 📝 Documentation

<documentation>
- **Style guides**: Document HTML patterns and components
- **Accessibility guide**: Document ARIA usage and patterns
- **Component library**: Document reusable HTML components
- **Performance guide**: Document optimization techniques
</documentation>

### 🔧 Tools

<tools>
- **HTML validators**: W3C Markup Validator, html-validate
- **Accessibility tools**: axe-core, WAVE, Lighthouse
- **Performance tools**: PageSpeed Insights, WebPageTest
- **Build tools**: Webpack, Vite, Parcel for optimization
- **Linters**: htmlhint, tidy for code quality
</tools>

</ecosystem>

### 💡 HTML Philosophy
- **"Content is king"**: Structure content meaningfully
- **"Semantic web"**: Use elements for their intended purpose
- **"Progressive enhancement"**: Start with working HTML
- **"Accessibility first"**: Design for all users from the start
- **"Performance matters"**: Every byte counts
- **"Standards compliance"**: Follow web standards and best practices

### 🔷 Advanced Patterns
- **Web Components**: Custom elements and shadow DOM
- **Microformats**: Structured data for better SEO
- **AMP/PWA**: Accelerated Mobile Pages and Progressive Web Apps
- **Schema.org**: Rich snippets and structured data
- **OpenGraph**: Social media optimization
- **JSON-LD**: Linked data for enhanced SEO

### 🚀 Performance Tips
- **Critical rendering path**: Optimize above-the-fold content
- **Resource hints**: preload, prefetch, preconnect
- **Image optimization**: WebP, AVIF, proper sizing
- **Lazy loading**: Load images and content as needed
- **Minification**: Remove unnecessary whitespace and comments
- **CDN**: Use Content Delivery Networks for static assets

### ♿ Accessibility Best Practices
- **Semantic HTML**: Use appropriate elements
- **ARIA labels**: Enhance semantics when needed
- **Keyboard navigation**: Ensure all features work with keyboard
- **Screen reader testing**: Test with actual screen readers
- **Color contrast**: Ensure sufficient contrast ratios
- **Focus management**: Proper focus indicators and tab order

**Remember**: HTML is the foundation of the web. Focus on semantic meaning, accessibility, and performance. Good HTML makes your content accessible to everyone, helps with SEO, and provides a solid foundation for CSS and JavaScript enhancements.

</language_guidelines>
