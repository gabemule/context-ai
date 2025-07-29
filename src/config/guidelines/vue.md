<language_guidelines>

# 🟢 Vue.js Coding Guidelines

<header>
<language_name>Vue.js</language_name>
<paradigm>Component-based reactive framework</paradigm>
<philosophy>Progressive framework with composition and reactivity</philosophy>
</header>

When providing Vue.js code suggestions, follow these principles:

<core_principles>

### 📐 Architecture Principles

<solid_principles>
- **Single Responsibility**: Each component should have one clear purpose
- **Open/Closed**: Use composables and props for extensibility
- **Liskov Substitution**: Component interfaces should be consistent
- **Interface Segregation**: Create focused, specific props interfaces
- **Dependency Inversion**: Depend on abstractions through composables
</solid_principles>

<dry_principle>
- **Don't Repeat Yourself**: Use composables for shared logic
- **Composition API**: Prefer composition over mixins
- **Reusable components**: Build modular, reusable UI components
- **Shared utilities**: Extract common functions to utilities
</dry_principle>

<clean_code>
- **Component clarity**: Single-file components with clear structure
- **Meaningful names**: Descriptive component and variable names
- **Small components**: Keep components focused and small
- **Clear data flow**: Explicit props down, events up pattern
</clean_code>

<yagni>
- **Start simple**: Don't add complexity until needed
- **Progressive enhancement**: Build basic functionality first
- **Avoid over-abstraction**: Don't create composables prematurely
</yagni>

</core_principles>

<language_specific>

### 🛠️ Vue-Specific Best Practices

<best_practices>
- **Composition API**: Prefer Composition API over Options API
- **TypeScript integration**: Use TypeScript for better developer experience
- **Composables**: Extract reusable reactive logic into composables
- **Single-file components**: Use .vue files with <template>, <script>, <style>
- **Reactive patterns**: Understand ref, reactive, computed, watch
- **Performance**: Use v-memo, defineAsyncComponent for optimization
</best_practices>

<idioms>
- **"Composition over inheritance"**: Use composables instead of mixins
- **"Props down, events up"**: Clear parent-child communication
- **"Reactive by design"**: Leverage Vue's reactivity system
- **"Single-file components"**: Keep template, script, style together
- **"Declarative templates"**: Use template syntax over imperative DOM manipulation
</idioms>

<performance>
- **Lazy loading**: Use defineAsyncComponent for code splitting
- **Computed caching**: Use computed for expensive operations
- **Memory optimization**: Properly clean up watchers and subscriptions
- **Bundle optimization**: Tree-shake unused components and libraries
- **Virtual scrolling**: For large lists and data sets
</performance>

</language_specific>

### 🎨 Naming Conventions
- **Components**: PascalCase (UserProfile, ProductCard)
- **Props**: camelCase (userName, isActive)
- **Events**: kebab-case (user-updated, item-selected)
- **Composables**: camelCase with "use" prefix (useUserData, useLocalStorage)
- **Files**: kebab-case for components (user-profile.vue)

### 🔍 Component Structure
- **Script setup**: Use <script setup> for cleaner syntax
- **Template first**: Template at top, followed by script and style
- **Props definition**: Use defineProps with TypeScript interfaces
- **Emits definition**: Use defineEmits for type-safe events
- **Composables**: Extract complex logic to composables

### ⚡ Reactivity Guidelines
- **ref vs reactive**: Use ref for primitives, reactive for objects
- **Computed properties**: For derived state that depends on reactive data
- **Watchers**: For side effects based on reactive data changes
- **Lifecycle hooks**: Use appropriate hooks for component lifecycle
- **Memory management**: Clean up subscriptions in onUnmounted

### 🎯 State Management
- **Pinia**: Use Pinia for global state management
- **Local state**: Keep state local when possible
- **Composables**: For shared reactive logic between components
- **Props/events**: For parent-child communication
- **Provide/inject**: For dependency injection across component tree

<examples>

### 🌟 Examples of Good Practices

<good_practices>
```vue
<!-- ✅ Modern Vue 3 component with Composition API -->
<template>
  <div class="user-profile">
    <div class="user-profile__header">
      <img 
        :src="user.avatar" 
        :alt="`${user.name} avatar`"
        class="user-profile__avatar"
        loading="lazy"
      >
      <div class="user-profile__info">
        <h2 class="user-profile__name">{{ user.name }}</h2>
        <p class="user-profile__email">{{ user.email }}</p>
        <span 
          class="user-profile__status"
          :class="`user-profile__status--${user.status}`"
        >
          {{ user.status }}
        </span>
      </div>
    </div>
    
    <div class="user-profile__actions">
      <button 
        @click="handleEdit"
        class="button button--primary"
        :disabled="isLoading"
      >
        Edit Profile
      </button>
      <button 
        @click="handleDelete"
        class="button button--danger"
        :disabled="isLoading"
      >
        Delete User
      </button>
    </div>
    
    <div v-if="isLoading" class="user-profile__loading">
      Loading...
    </div>
  </div>
</template>

<script setup lang="ts">
// ✅ TypeScript interfaces
interface User {
  id: string
  name: string
  email: string
  avatar: string
  status: 'active' | 'inactive' | 'pending'
}

interface UserProfileProps {
  userId: string
  editable?: boolean
}

interface UserProfileEmits {
  'user-updated': [user: User]
  'user-deleted': [userId: string]
}

// ✅ Props and emits with types
const props = withDefaults(defineProps<UserProfileProps>(), {
  editable: true
})

const emit = defineEmits<UserProfileEmits>()

// ✅ Composables for reusable logic
const { user, isLoading, updateUser, deleteUser } = useUser(props.userId)
const { showConfirmDialog } = useDialog()

// ✅ Computed properties for derived state
const canEdit = computed(() => props.editable && !isLoading.value)

// ✅ Methods with clear purpose
const handleEdit = async () => {
  if (!canEdit.value) return
  
  try {
    const updatedUser = await updateUser({
      name: 'New Name' // This would come from a form
    })
    emit('user-updated', updatedUser)
  } catch (error) {
    console.error('Failed to update user:', error)
  }
}

const handleDelete = async () => {
  const confirmed = await showConfirmDialog({
    title: 'Delete User',
    message: `Are you sure you want to delete ${user.value?.name}?`
  })
  
  if (confirmed) {
    try {
      await deleteUser()
      emit('user-deleted', props.userId)
    } catch (error) {
      console.error('Failed to delete user:', error)
    }
  }
}
</script>

<style scoped lang="scss">
// ✅ Scoped styles with BEM naming
.user-profile {
  --user-profile-bg: white;
  --user-profile-border: #e5e7eb;
  --user-profile-spacing: 1rem;
  
  background: var(--user-profile-bg);
  border: 1px solid var(--user-profile-border);
  border-radius: $border-radius__default;
  padding: var(--user-profile-spacing);
}

.user-profile__header {
  display: flex;
  gap: $spacing__base;
  margin-bottom: $spacing__large;
}

.user-profile__avatar {
  border-radius: 50%;
  height: 64px;
  width: 64px;
}

.user-profile__info {
  flex: 1;
}

.user-profile__name {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 $spacing__small 0;
}

.user-profile__status {
  display: inline-block;
  padding: $spacing__small;
  border-radius: $border-radius__default;
  font-size: 0.875rem;
  
  &--active {
    background: #d1fae5;
    color: #065f46;
  }
  
  &--inactive {
    background: #fee2e2;
    color: #991b1b;
  }
  
  &--pending {
    background: #fef3c7;
    color: #92400e;
  }
}

.user-profile__actions {
  display: flex;
  gap: $spacing__base;
}
</style>
```

```ts
// ✅ Composable for user management
// composables/useUser.ts
export function useUser(userId: string) {
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  const fetchUser = async () => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.get(`/users/${userId}`)
      user.value = response.data
    } catch (err) {
      error.value = 'Failed to fetch user'
      console.error('User fetch error:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  const updateUser = async (updates: Partial<User>) => {
    isLoading.value = true
    
    try {
      const response = await api.patch(`/users/${userId}`, updates)
      user.value = response.data
      return response.data
    } catch (err) {
      error.value = 'Failed to update user'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const deleteUser = async () => {
    isLoading.value = true
    
    try {
      await api.delete(`/users/${userId}`)
      user.value = null
    } catch (err) {
      error.value = 'Failed to delete user'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // Fetch user on mount
  onMounted(fetchUser)
  
  return {
    user: readonly(user),
    isLoading: readonly(isLoading),
    error: readonly(error),
    updateUser,
    deleteUser,
    refetch: fetchUser
  }
}
```
</good_practices>

<anti_patterns>
### 🚫 Anti-patterns to Avoid

```vue
<!-- ❌ Options API with poor structure -->
<template>
  <div>
    <span @click="doSomething">{{ message }}</span>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: 'Hello' // No type safety
    }
  },
  methods: {
    doSomething() {
      // Logic mixed with component
    }
  }
}
</script>

<!-- ✅ Better: Composition API with types -->
<template>
  <div>
    <button @click="handleClick">{{ message }}</button>
  </div>
</template>

<script setup lang="ts">
const message = ref<string>('Hello')
const { handleClick } = useClickHandler()
</script>

<!-- ❌ Direct DOM manipulation -->
<script setup>
const updateElement = () => {
  document.getElementById('myElement').textContent = 'New text'
}
</script>

<!-- ✅ Better: Reactive data -->
<script setup>
const elementText = ref('Old text')
const updateElement = () => {
  elementText.value = 'New text'
}
</script>
```
</anti_patterns>

</examples>

<ecosystem>

### 🧪 Testing Philosophy

<testing>
- **Vue Test Utils**: Official testing utilities for Vue components
- **Vitest**: Fast unit testing framework
- **Component testing**: Test component behavior and interactions
- **Composables testing**: Test composable logic in isolation
- **E2E testing**: Use Playwright or Cypress for integration tests
</testing>

### 📝 Documentation

<documentation>
- **Component docs**: Document props, events, and slots
- **Composables docs**: Document reactive logic and usage
- **Storybook**: Visual component documentation and testing
- **TypeScript**: Types serve as inline documentation
</documentation>

### 🔧 Tools

<tools>
- **Vite**: Fast build tool and dev server
- **Vue Devtools**: Browser extension for debugging
- **Pinia**: State management library
- **VueUse**: Collection of essential Vue composables
- **Nuxt**: Full-stack Vue framework
</tools>

</ecosystem>

### 💡 Vue Philosophy
- **"Progressive framework"**: Adopt incrementally as needed
- **"Reactive by design"**: Embrace Vue's reactivity system
- **"Component-based"**: Build UIs from reusable components
- **"Developer experience"**: Focus on developer happiness and productivity
- **"Performance by default"**: Optimized reactivity and rendering
- **"Ecosystem friendly"**: Plays well with other tools and libraries

### 🔷 Advanced Patterns
- **Teleport**: Render content in different DOM locations
- **Suspense**: Handle async components and loading states
- **Custom directives**: Create reusable DOM manipulation logic
- **Plugins**: Extend Vue with global functionality
- **Render functions**: Programmatic component creation
- **Server-side rendering**: With Nuxt or custom SSR setup

### 🚀 Performance Tips
- **Code splitting**: Use defineAsyncComponent for lazy loading
- **Virtual scrolling**: For large data sets
- **Memoization**: Use computed properties for expensive calculations
- **Tree shaking**: Remove unused code from bundles
- **Bundle analysis**: Monitor and optimize bundle size
- **Preloading**: Use link prefetch for critical resources

### 🎨 UI Best Practices
- **Accessibility**: Use semantic HTML and ARIA attributes
- **Responsive design**: Mobile-first approach with CSS Grid/Flexbox
- **Loading states**: Provide feedback during async operations
- **Error boundaries**: Handle and display errors gracefully
- **Animation**: Use Vue transitions for smooth UI changes
- **Internationalization**: Use Vue I18n for multi-language support

**Remember**: Vue.js excels at building reactive, component-based user interfaces. Embrace the Composition API, use TypeScript for better development experience, extract reusable logic into composables, and keep components focused and small.

</language_guidelines>
