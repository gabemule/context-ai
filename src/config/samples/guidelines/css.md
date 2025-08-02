<language_guidelines>

# 🎨 CSS Coding Guidelines

<header>
<language_name>CSS</language_name>
<paradigm>Declarative styling with cascading principles</paradigm>
<philosophy>Modular, maintainable, and performant styling</philosophy>
</header>

When providing CSS code suggestions, follow these principles:

<core_principles>

### 📐 Architecture Principles

<solid_principles>
- **Single Responsibility**: Each CSS rule should have one clear purpose
- **Open/Closed**: Use classes that can be extended without modification
- **Liskov Substitution**: Modifier classes should work with any base class
- **Interface Segregation**: Create specific utility classes rather than monolithic ones
- **Dependency Inversion**: Depend on semantic class names, not implementation details
</solid_principles>

<dry_principle>
- **Don't Repeat Yourself**: Use CSS custom properties, mixins, and utility classes
- **Component-based CSS**: Create reusable component styles
- **Utility classes**: Build common patterns into utility classes
- **CSS custom properties**: Use variables for repeated values
</dry_principle>

<clean_code>
- **Meaningful class names**: Use descriptive, semantic class names
- **Consistent formatting**: Follow consistent indentation and spacing
- **Logical grouping**: Group related properties together
- **Clear specificity**: Avoid overly specific selectors
</clean_code>

<yagni>
- **Minimal CSS**: Don't add styles until needed
- **Progressive enhancement**: Start with basic styles, enhance as needed
- **Avoid premature optimization**: Focus on maintainability first
</yagni>

</core_principles>

<language_specific>

### 🛠️ CSS-Specific Best Practices

<best_practices>
- **BEM methodology**: Use Block__Element--Modifier for classes AND Sass variables
- **CSS custom properties**: Only for dynamic values (themes, colors, fonts) within components
- **Sass variables**: For static values and component-specific calculations
- **Mobile-first**: Design for mobile devices first, then enhance
- **Flexbox/Grid**: Use modern layout methods over floats and positioning
- **Performance**: Minimize repaints, use efficient selectors
- **Accessibility**: Ensure sufficient contrast, focus indicators
</best_practices>

<idioms>
- **"CSS vars for dynamic, Sass for static"**: Use appropriate variable type
- **"Component-scoped CSS vars"**: Define CSS vars within components, reference globals
- **"BEM everywhere"**: Apply BEM to classes, Sass variables, and mixins
- **"Mobile first"**: Start with mobile styles, enhance for desktop
- **"Component thinking"**: Design reusable, modular components
</idioms>

<performance>
- **Efficient selectors**: Avoid complex and deeply nested selectors
- **Critical CSS**: Inline critical above-the-fold styles
- **Minimize reflows**: Use transforms and opacity for animations
- **Bundle optimization**: Remove unused CSS, minify for production
- **CSS containment**: Use contain property for layout optimization
</performance>

</language_specific>

### 🎨 Naming Conventions
- **BEM for CSS classes**: block__element--modifier (card__title--large)
- **BEM for Sass variables**: $block__element--modifier ($button__text--large)
- **CSS custom properties**: --component-property (--button-bg, --card-spacing)
- **Utility classes**: Prefixed and descriptive (u-text-center, u-margin-large)
- **State classes**: is- or has- prefix (is-active, has-error)
- **JavaScript hooks**: js- prefix for JavaScript-only classes

### 🎯 CSS Custom Properties Strategy
- **Global tokens**: Define in :root for theme values only
- **Component scope**: Define CSS vars within component classes
- **Dynamic values only**: Colors, fonts, spacing that change with themes
- **Reference globals**: Component vars reference global tokens

### 🔍 Specificity Management
- **Low specificity**: Use classes instead of IDs and deeply nested selectors
- **Logical order**: Organize CSS from generic to specific
- **Avoid !important**: Use proper cascading instead of forcing styles
- **Component isolation**: Use methodologies like BEM to avoid conflicts

### ⚡ Performance Guidelines
- **Critical CSS**: Inline essential styles for above-the-fold content
- **Lazy loading**: Load non-critical CSS asynchronously
- **Efficient animations**: Use transform and opacity for 60fps animations
- **Bundle size**: Remove unused CSS, use tree-shaking
- **Resource hints**: Preload fonts and critical CSS files

### 🎯 Layout Best Practices
- **Flexbox**: For one-dimensional layouts
- **CSS Grid**: For two-dimensional layouts
- **Logical properties**: Use margin-inline, padding-block for internationalization
- **Container queries**: Responsive components based on container size
- **Aspect ratio**: Use aspect-ratio property for consistent proportions

<examples>

### 🌟 Examples of Good Practices

<good_practices>
```scss
// ✅ Global CSS Custom Properties (only dynamic theme values)
:root {
  --global-color-primary: #007bff;
  --global-color-secondary: #6c757d;
  --global-color-success: #28a745;
  --global-font-family: system-ui, -apple-system, sans-serif;
  --global-font-size-base: 1rem;
}

// ✅ Sass variables for static values (BEM naming)
$spacing__base: 1rem;
$spacing__small: $spacing__base * 0.5;
$spacing__large: $spacing__base * 2;
$border-radius__default: 0.375rem;
$shadow__light: 0 2px 4px rgba(0, 0, 0, 0.1);

// ✅ Component with CSS vars referencing globals
.card {
  // Component-scoped CSS vars (dynamic values only)
  --card-bg: white;
  --card-text: #333;
  --card-border: #e9ecef;
  --card-spacing: var(--global-font-size-base);
  
  // Static styles using Sass variables
  background: var(--card-bg);
  border-radius: $border-radius__default;
  box-shadow: $shadow__light;
  padding: $spacing__base;
}

.card__header {
  border-bottom: 1px solid var(--card-border);
  margin-bottom: $spacing__base;
  padding-bottom: $spacing__small;
}

.card__title {
  --card-title-color: var(--global-color-primary);
  
  color: var(--card-title-color);
  font-family: var(--global-font-family);
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.card__content {
  color: var(--card-text);
  line-height: 1.6;
}

.card--featured {
  --card-border: var(--global-color-primary);
  border: 2px solid var(--card-border);
}

.card--compact {
  padding: $spacing__small;
}

/* ✅ Mobile-first responsive design */
.grid {
  display: grid;
  gap: var(--spacing-base);
  grid-template-columns: 1fr;
}

@media (min-width: 48em) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 64em) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* ✅ Utility classes */
.u-text-center { text-align: center; }
.u-margin-none { margin: 0; }
.u-padding-small { padding: var(--spacing-small); }
.u-hidden { display: none; }
.u-sr-only {
  clip: rect(0, 0, 0, 0);
  clip-path: inset(50%);
  height: 1px;
  overflow: hidden;
  position: absolute;
  white-space: nowrap;
  width: 1px;
}

// ✅ Button component with CSS vars + Sass variables
.button {
  // Component-scoped CSS vars (dynamic theme values)
  --button-bg: var(--global-color-primary);
  --button-border: var(--global-color-primary);
  --button-text: white;
  --button-font: var(--global-font-family);
  
  // Static styles using Sass variables
  background: var(--button-bg);
  border: 1px solid var(--button-border);
  border-radius: $border-radius__default;
  color: var(--button-text);
  cursor: pointer;
  display: inline-flex;
  font-family: var(--button-font);
  font-size: var(--global-font-size-base);
  font-weight: 500;
  gap: $spacing__small;
  padding: $spacing__small * 1.5 $spacing__base * 1.5;
  text-decoration: none;
  transition: all 0.2s ease;
  align-items: center;
  justify-content: center;
}

.button:hover,
.button:focus {
  --button-bg: #0056b3;
  --button-border: #0056b3;
  transform: translateY(-1px);
}

.button:focus {
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
  outline: none;
}

.button--secondary {
  --button-bg: transparent;
  --button-text: var(--global-color-primary);
}

.button--large {
  font-size: calc(var(--global-font-size-base) * 1.125);
  padding: $spacing__base $spacing__large;
}

.button--block {
  width: 100%;
}

/* ✅ Efficient animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(1rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.3s ease-out;
}

/* ✅ Container queries (modern CSS) */
.sidebar {
  container-type: inline-size;
}

@container (min-width: 300px) {
  .sidebar .card {
    display: flex;
    flex-direction: row;
  }
}
```
</good_practices>

<anti_patterns>
### 🚫 Anti-patterns to Avoid

```css
/* ❌ Overly specific selectors */
div.container ul.nav li.nav-item a.nav-link { color: blue; }

/* ✅ Better: use classes */
.nav-link { color: blue; }

/* ❌ IDs for styling */
#header { background: blue; }

/* ✅ Better: use classes */
.header { background: blue; }

/* ❌ Magic numbers and hardcoded values */
.card {
  margin: 15px;
  padding: 23px;
  border-radius: 8px;
}

/* ✅ Better: use variables */
.card {
  margin: var(--spacing-base);
  padding: var(--spacing-large);
  border-radius: var(--border-radius);
}

/* ❌ Non-semantic class names */
.red-text { color: red; }
.big-box { font-size: 24px; }

/* ✅ Better: semantic names */
.error-message { color: red; }
.heading-primary { font-size: 1.5rem; }
```
</anti_patterns>

</examples>

<ecosystem>

### 🧪 Testing Philosophy

<testing>
- **CSS validation**: Use W3C CSS Validator
- **Cross-browser testing**: Test in multiple browsers
- **Responsive testing**: Test across different screen sizes
- **Performance testing**: Measure CSS impact on page load
- **Accessibility testing**: Ensure sufficient contrast and focus states
</testing>

### 📝 Documentation

<documentation>
- **Style guide**: Document component styles and usage
- **Design tokens**: Document colors, spacing, typography
- **Component library**: Visual examples of styled components
- **Browser support**: Document supported browsers and fallbacks
</documentation>

### 🔧 Tools

<tools>
- **Preprocessors**: Sass, Less for enhanced CSS authoring
- **PostCSS**: Plugin-based CSS processing
- **Linters**: stylelint for code quality
- **Build tools**: Webpack, Vite for optimization
- **Frameworks**: Tailwind CSS, Bootstrap for rapid development
</tools>

</ecosystem>

### 💡 CSS Philosophy
- **"Cascade is a feature"**: Embrace the cascade, don't fight it
- **"Specificity is debt"**: Keep specificity low and manageable
- **"Mobile first"**: Design for constraints, enhance for capabilities
- **"Performance matters"**: Every style impacts rendering performance
- **"Accessibility is essential"**: Design for all users from the start
- **"Maintainability over cleverness"**: Write CSS that others can understand

### 🔷 Advanced Patterns
- **CSS-in-JS**: Runtime CSS generation for dynamic styling
- **CSS Modules**: Scoped CSS for component-based development
- **Atomic CSS**: Utility-first CSS approach
- **CSS containment**: Optimize rendering performance
- **CSS Houdini**: Extend CSS with custom properties and paint worklets
- **Container queries**: Element-based responsive design

### 🚀 Performance Tips
- **Critical CSS**: Inline essential styles for faster rendering
- **CSS containment**: Use contain property to isolate rendering
- **Transform animations**: Use transform and opacity for smooth animations
- **Efficient selectors**: Avoid complex selectors that slow rendering
- **Bundle optimization**: Remove unused CSS, use tree-shaking
- **Resource loading**: Preload fonts, use font-display: swap

### 🎨 Design System Integration
- **Consistent tokens**: Use design tokens for colors, spacing, typography
- **Component variants**: Create systematic component variations
- **Responsive scales**: Use consistent breakpoints and scaling
- **Accessibility standards**: Meet WCAG guidelines for contrast and interaction
- **Brand consistency**: Maintain visual consistency across applications

**Remember**: CSS is about creating maintainable, performant, and accessible styles. Focus on semantic class names, keep specificity low, embrace modern layout methods, and always consider the user experience across different devices and abilities.

</language_guidelines>
