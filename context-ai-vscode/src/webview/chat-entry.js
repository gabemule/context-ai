// ✅ Import libs that Vite will bundle
import markdownit from 'markdown-it';
import hljs from 'highlight.js';

// Make libs available globally for the main chat script
window.markdownit = markdownit;
window.hljs = hljs;
window.libsReady = true; // Flag to indicate libs are loaded

// console.log('🎯 BUNDLE: Libraries loaded and made available globally');
// console.log('🎯 BUNDLE: markdownit type:', typeof window.markdownit);
// console.log('🎯 BUNDLE: hljs type:', typeof window.hljs);

// Wait for DOM to be ready, then import chat.js
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('🎯 BUNDLE: DOM ready, importing chat.js');
        import('../../media/chat.js');
    });
} else {
    console.log('🎯 BUNDLE: DOM already ready, importing chat.js');
    import('../../media/chat.js');
}
