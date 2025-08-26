// ✅ Libs will be bundled by Vite and available globally
import { logger } from '../src/shared/logger.js';

(function() {

    // Use libs that were made available globally by the bundle
    const markdownit = window.markdownit;
    const hljs = window.hljs;
    const vscode = acquireVsCodeApi();
    
    // DOM elements
    const messagesContainer = document.getElementById('messages');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const clearBtn = document.getElementById('clearBtn');
    let sendText = null;
    let loadingText = null;
    
    let isLoading = false;
    let currentLoadingMessage = null;
    let isStreaming = false;
    let currentStreamingMessage = null;
    let isInitializing = true;
    let initializationStatus = null;
    let chatInfoShown = false;
    let rawStreamContent = '';
    let isScrolledUp = false;
    let userManuallyScrolled = false;

    // ✅ REAL markdown-it initialization with bundled libs
    let md = null;
    let libsLoaded = false;
    
    function initializeMarkdown() {
        logger.debug('🚀 Initializing markdown-it with BUNDLED libs from Vite');
        
        try {
            // Configure markdown-it with highlight.js (REAL implementation!)
            md = markdownit({
                html: true,
                linkify: true,
                typographer: true,
                breaks: true,
                highlight: function (str, lang) {
                    const escapedCode = md.utils.escapeHtml(str);
                    
                    if (lang && hljs.getLanguage && hljs.getLanguage(lang)) {
                        try {
                            logger.debug(`🎨 Highlighting ${lang} code with highlight.js`);
                            const highlighted = hljs.highlight(str, { language: lang, ignoreIllegals: true }).value;
                            
                            // 📋 Add copy button to code block
                            return '<pre class="code-block-container">' +
                                   '<button class="code-copy-btn" onclick="copyCodeToClipboard(this)" title="Copy code">' +
                                   '<span class="copy-icon">📋</span>' +
                                   '<span class="copy-text">COPY</span>' +
                                   '</button>' +
                                   '<code class="hljs language-' + lang + '">' + highlighted + '</code>' +
                                   '</pre>';
                        } catch (error) {
                            logger.warn('⚠️ Highlight.js error:', error);
                        }
                    }
                    
                    // 📋 Add copy button even for non-highlighted code
                    return '<pre class="code-block-container">' +
                           '<button class="code-copy-btn" onclick="copyCodeToClipboard(this)" title="Copy code">' +
                           '<span class="copy-icon">📋</span>' +
                           '<span class="copy-text">COPY</span>' +
                           '</button>' +
                           '<code class="hljs">' + escapedCode + '</code>' +
                           '</pre>';
                }
            });
            
            libsLoaded = true;
            logger.debug('✅ BUNDLED markdown-it + highlight.js initialized successfully!');
        } catch (error) {
            logger.error('❌ Failed to initialize bundled libraries:', error);
            
            // Basic fallback
            md = {
                render: function(text) {
                    return text
                        .replace(/\n/g, '<br>')
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/`(.*?)`/g, '<code>$1</code>');
                }
            };
            libsLoaded = true;
        }
    }

    // Initialize
    init();

    function init() {
        // ✅ Initialize BUNDLED markdown-it and highlight.js
        initializeMarkdown();
        
        // Initialize button HTML structure FIRST
        initializeSendButton();
        
        // Show empty state initially
        showEmptyState();
        
        // Event listeners
        sendBtn.addEventListener('click', handleSendButtonClick);
        clearBtn.addEventListener('click', clearChat);
        messageInput.addEventListener('keydown', handleKeyDown);
        
        // Scroll detection
        messagesContainer.addEventListener('scroll', handleScroll);
        
        // Example question buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('example-btn')) {
                const question = e.target.getAttribute('data-question');
                if (question) {
                    messageInput.value = question;
                    sendMessage();
                }
            }
        });

        // Show initialization status and disable input
        showInitializationStatus();
        disableInput();
    }

    function showInitializationStatus() {
        const statusDiv = document.createElement('div');
        statusDiv.className = 'initialization-status';
        statusDiv.innerHTML = `
            <div>Initializing Context-AI<span class="loading-dots"></span></div>
        `;
        messagesContainer.appendChild(statusDiv);
        initializationStatus = statusDiv;
    }

    function removeInitializationStatus() {
        if (initializationStatus && initializationStatus.parentNode) {
            initializationStatus.remove();
            initializationStatus = null;
        }
    }

    function disableInput() {
        messageInput.disabled = true;
        sendBtn.disabled = true;
        messageInput.placeholder = "Initializing Context-AI...";
    }

    function enableInput() {
        isInitializing = false;
        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.placeholder = "Ask Context-AI about your codebase...";
        messageInput.focus();
    }

    function handleKeyDown(e) {
        if (e.key === 'Enter') {
            if (e.ctrlKey || e.metaKey) {
                // Ctrl+Enter or Cmd+Enter = new line (allow default behavior)
                return;
            } else {
                // Plain Enter = send message
                e.preventDefault();
                sendMessage();
            }
        }
    }

    function sendMessage() {
        const message = messageInput.value.trim();
        if (!message || isLoading) return;

        // ✅ PROTEÇÃO CRÍTICA: Bloquear envio se libs não carregaram
        if (!libsLoaded || !md) {
            logger.error('❌ BLOCKED: Cannot send message - libraries not ready');
            logger.warn('❌ Libraries still loading. Please wait a moment and try again.');
            return;
        }

        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        messageInput.value = '';
        
        // Show loading state
        setLoading(true);
        
        // Send message to extension
        vscode.postMessage({
            command: 'sendMessage',
            text: message
        });
        
        // Hide empty state
        hideEmptyState();
    }

    function clearChat() {
        messagesContainer.innerHTML = '';
        showEmptyState();
        vscode.postMessage({ command: 'clearChat' });
    }

    function addMessage(text, type = 'assistant', isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        if (isError) {
            messageDiv.classList.add('error');
        }

        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';
        
        if (type === 'user') {
            headerDiv.textContent = '👤 You';
        } else if (isError) {
            headerDiv.textContent = '❌ Error';
        } else {
            headerDiv.textContent = '🤖 Context-AI';
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Process markdown formatting with REAL markdown-it
        contentDiv.innerHTML = formatMessage(text);

        messageDiv.appendChild(headerDiv);
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        
        // 🔽 Smart scroll - só scroll se estiver no bottom
        smartScroll();
        
        return messageDiv;
    }

    function formatMessage(text) {
        // ✅ PROTEÇÃO CRÍTICA: Verificar se markdown-it carregou
        if (!md) {
            logger.error('❌ CRITICAL: markdown-it not loaded, cannot format message!');
            throw new Error('Markdown-it not ready - bundling failed');
        }
        
        logger.debug('🎯 Using BUNDLED markdown-it formatting');
        return md.render(text);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function addLoadingMessage() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading-message';
        loadingDiv.innerHTML = `
            <div class="message-header">🤖 Context-AI</div>
            <div>Thinking<span class="loading-dots"></span></div>
        `;
        
        messagesContainer.appendChild(loadingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        return loadingDiv;
    }

    function removeLoadingMessage() {
        logger.debug('🧹 removeLoadingMessage called, currentLoadingMessage:', currentLoadingMessage);
        
        if (currentLoadingMessage) {
            logger.debug('🧹 Removing loading message');
            currentLoadingMessage.remove();
            currentLoadingMessage = null;
            logger.debug('🧹 Loading message removed successfully');
        } else {
            logger.debug('🧹 No currentLoadingMessage to remove');
        }
    }

    function setLoading(loading) {
        isLoading = loading;
        
        logger.debug('🔽 setLoading called:', { loading, isInitializing, sendText, loadingText });
        
        if (loading && !isInitializing) { // ✅ SÓ mostrar se não estiver inicializando
            sendBtn.disabled = true;
            if (sendText) sendText.classList.add('hidden');
            if (loadingText) loadingText.classList.remove('hidden');
            showHeaderLoading(); // ✅ USAR header loading
        } else if (!loading) {
            sendBtn.disabled = false;
            if (sendText) sendText.classList.remove('hidden');
            if (loadingText) loadingText.classList.add('hidden');
            hideHeaderLoading(); // ✅ ESCONDER header loading
        }
        
        // ✅ SEMPRE atualizar o botão após mudar o estado de loading
        updateSendButton();
    }

    function showHeaderLoading() {
        const header = document.querySelector('.header');
        if (header) {
            header.classList.add('loading');
        }
    }

    function hideHeaderLoading() {
        const header = document.querySelector('.header');
        if (header) {
            header.classList.remove('loading');
        }
    }

    function showEmptyState() {
        if (messagesContainer.children.length === 0) {
            const emptyDiv = document.createElement('div');
            emptyDiv.className = 'empty-state';
            emptyDiv.innerHTML = `
                <h3>Welcome to Context-AI Chat! 🤖</h3>
                <p>Ask questions about your codebase and get intelligent answers.<br>
                Try the example questions below to get started.</p>
            `;
            messagesContainer.appendChild(emptyDiv);
        }
    }

    function hideEmptyState() {
        const emptyState = messagesContainer.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
        }
    }

    // Handle messages from extension
    window.addEventListener('message', event => {
        const message = event.data;
        
        switch (message.command) {
            case 'receiveMessage':
                setLoading(false);
                addMessage(message.text, 'assistant', message.isError);
                break;
                
            case 'showLoading':
                setLoading(message.isLoading);
                break;
                
                case 'clearMessages':
                    messagesContainer.innerHTML = '';
                    // Hide token stats when clearing
                    const tokenStats = document.getElementById('tokenStats');
                    if (tokenStats) {
                        tokenStats.classList.add('hidden');
                    }
                    break;

                case 'updateTokenStats':
                    updateTokenStats(event.data.stats);
                    break;
                
            case 'addQuestion':
                addMessage(message.text, 'user');
                hideEmptyState();
                break;
                
            case 'streamStart':
                // Start streaming - MANTER loading ativo
                logger.debug('🎯 streamStart - starting streaming (keeping header loading)');
                startStreaming();
                break;
                
            case 'streamChunk':
                // Add chunk to streaming message
                appendStreamChunk(message.text);
                break;
                
            case 'streamComplete':
                // Complete streaming and remove loading
                logger.debug('🎯 streamComplete - removing header loading');
                setLoading(false);
                completeStreaming();
                break;
                
            case 'chatReady':
                // Chat is ready - remove initialization status and enable input
                logger.debug('🎯 chatReady received:', message);
                logger.debug('🎯 chatInfo:', message.chatInfo);
                logger.debug('🎯 chatInfoShown:', chatInfoShown);
                
                removeInitializationStatus();
                
                // ✅ FORÇAR mock SEMPRE para debug
                const MOCK_INFO = `Ask questions about your codebase. Chat history will be maintained for context.

Special commands:
    /embeddings - Show active embeddings
    /history    - Show chat statistics  
    /clear      - Reset conversation history
    /verbose    - Toggle detailed logging
    /mode       - Change prompt mode (minimal|standard|comprehensive|strict)
    exit        - Quit chat session`;
                
                const infoToShow = message.chatInfo || MOCK_INFO;
                logger.debug('🎯 Using info:', infoToShow);
                
                if (!chatInfoShown) {
                    logger.debug('🎯 Calling showChatInfo...');
                    showChatInfo(infoToShow);
                    chatInfoShown = true;
                    logger.debug('🎯 showChatInfo completed');
                } else {
                    logger.debug('🎯 chatInfoShown already true, skipping');
                }
                
                enableInput();
                break;
        }
    });

    function startStreaming() {
        isStreaming = true;
        rawStreamContent = ''; // Reset raw content
        
        // Create streaming message container
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant'; // ✅ SEM classe streaming
        
        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';
        headerDiv.textContent = '🤖 Context-AI';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = '<div class="streaming-indicator">🌊 Streaming response...</div>';
        
        messageDiv.appendChild(headerDiv);
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        
        currentStreamingMessage = messageDiv;
        
        // 🔽 Smart scroll - só scroll se estiver no bottom
        smartScroll();
    }

    function formatStreamingMarkdown(text) {
        // ✅ Use BUNDLED markdown-it for streaming
        logger.debug('🎯 Using BUNDLED markdown-it for streaming formatting');
        
        if (!md) {
            logger.warn('⚠️ Markdown-it not ready for streaming, using fallback');
            return escapeHtml(text).replace(/\n/g, '<br>');
        }
        
        try {
            return md.render(text);
        } catch (error) {
            logger.warn('⚠️ Error in streaming markdown formatting:', error);
            return escapeHtml(text).replace(/\n/g, '<br>');
        }
    }

    function appendStreamChunk(chunk) {
        if (!currentStreamingMessage || !isStreaming) return;
        
        const contentDiv = currentStreamingMessage.querySelector('.message-content');
        
        // Remove streaming indicator if it exists
        const indicator = contentDiv.querySelector('.streaming-indicator');
        if (indicator) {
            indicator.remove();
            contentDiv.innerHTML = ''; // Clear content when starting
            rawStreamContent = ''; // Reset when starting fresh
        }
        
        // Accumulate raw content
        rawStreamContent += chunk;
        
        // ✅ Use BUNDLED markdown-it streaming formatting
        const formattedContent = formatStreamingMarkdown(rawStreamContent);
        
        // Update content with formatted markdown
        contentDiv.innerHTML = formattedContent;
        
        // 🔽 Smart scroll - só scroll se usuário estiver no bottom
        smartScroll();
    }

    function completeStreaming() {
        isStreaming = false;
        
        if (currentStreamingMessage) {
            // Apply final formatting on completion with BUNDLED markdown-it
            const contentDiv = currentStreamingMessage.querySelector('.message-content');
            if (rawStreamContent) {
                contentDiv.innerHTML = formatMessage(rawStreamContent);
            }
            
            // Remove streaming class
            currentStreamingMessage.classList.remove('streaming');
            currentStreamingMessage = null;
        }
        
        // Reset raw content
        rawStreamContent = '';
    }

    function showChatInfo(rawChatInfo) {
        logger.debug('🎯 showChatInfo START with:', rawChatInfo);
        
        // Clean up the raw chat info - remove box drawing characters and format nicely
        const cleanedInfo = rawChatInfo
            .replace(/[╭╮╰╯─│]/g, '') // Remove box drawing characters
            .replace(/^\s*🤖.*?Session.*?\n/gm, '') // Remove header line
            .replace(/^\s*$/gm, '') // Remove empty lines
            .trim();

        logger.debug('🎯 cleanedInfo:', cleanedInfo);

        // Extract key information
        const lines = cleanedInfo.split('\n').filter(line => line.trim());
        logger.debug('🎯 lines:', lines);
        
        let embeddings = '';
        let description = '';
        let commands = [];
        
        let currentSection = '';
        
        for (let i = 0; i < lines.length; i++) {
            const trimmed = lines[i].trim();
            if (trimmed.startsWith('Using embeddings:')) {
                // Capture embeddings line and potential continuation lines
                let embeddingsText = trimmed.replace('Using embeddings:', '').trim();
                
                // Look ahead for continuation lines (lines that don't start with special patterns)
                let j = i + 1;
                while (j < lines.length) {
                    const nextLine = lines[j].trim();
                    // Stop if we hit a new section or empty line
                    if (nextLine.includes('Ask questions about') || 
                        nextLine.includes('Special commands:') || 
                        nextLine.startsWith('/') ||
                        nextLine.includes('exit') ||
                        nextLine === '') {
                        break;
                    }
                    // Add continuation line
                    embeddingsText += ' ' + nextLine;
                    j++;
                }
                
                // Clean up the embeddings text - remove line breaks, normalize spaces, fix commas
                embeddings = embeddingsText
                    .replace(/\n\s*/g, ' ')     // Remove line breaks
                    .replace(/,\s*,/g, ',')     // Remove duplicate commas
                    .replace(/\s+/g, ' ')       // Normalize multiple spaces
                    .trim();
                
                // Skip the processed continuation lines
                i = j - 1;
                
            } else if (trimmed.includes('Ask questions about')) {
                description = trimmed;
            } else if (trimmed.includes('Special commands:')) {
                currentSection = 'commands';
            } else if (currentSection === 'commands' && trimmed.startsWith('/')) {
                commands.push(trimmed);
            } else if (trimmed === 'exit        - Quit chat session') {
                commands.push('exit - Quit chat session');
            }
        }

        logger.debug('🎯 parsed data - embeddings:', embeddings, 'description:', description, 'commands:', commands);

        // Create info card
        const infoDiv = document.createElement('div');
        infoDiv.className = 'chat-info-card';
        
        let html = `
            <div class="chat-info-header">
                <span class="chat-info-icon">📊</span>
                <strong>Context-AI Ready!</strong>
            </div>
        `;
        
        if (embeddings) {
            html += `
                <div class="chat-info-section">
                    <div class="chat-info-label">Active Embeddings:</div>
                    <div class="chat-info-value">${embeddings}</div>
                </div>
            `;
        }
        
        if (description) {
            html += `
                <div class="chat-info-section">
                    <div class="chat-info-description">${description}</div>
                </div>
            `;
        }
        
        if (commands.length > 0) {
            html += `
                <div class="chat-info-section">
                    <div class="chat-info-label">Special Commands:</div>
                    <div class="chat-info-commands">
            `;
            
            commands.forEach(cmd => {
                const [command, description] = cmd.split(' - ');
                html += `<div class="command-item">
                    <code>${command}</code> - ${description || ''}
                </div>`;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        logger.debug('🎯 generated html:', html);
        
        infoDiv.innerHTML = html;
        logger.debug('🎯 appending to messagesContainer, current children:', messagesContainer.children.length);
        messagesContainer.appendChild(infoDiv);
        logger.debug('🎯 after append, children:', messagesContainer.children.length);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        logger.debug('🎯 showChatInfo COMPLETE');
    }

    function updateTokenStats(stats) {
        const tokenStatsDiv = document.getElementById('tokenStats');
        if (!tokenStatsDiv) return;
        
        const { total_tokens, percentage, breakdown, output_tokens } = stats;
        
        // Format numbers nicely with 1 decimal place
        const totalK = (total_tokens / 1000).toFixed(1);
        const outputK = (output_tokens / 1000).toFixed(1);
        
        // Create display text
        let displayText = `📊 ${totalK}K tokens (${percentage}%)`;
        
        // Add breakdown if available
        if (breakdown) {
            displayText += ` • ${breakdown}`;
        }
        
        // Add output tokens if significant
        if (parseFloat(outputK) > 0) {
            displayText += ` • ${outputK}K out`;
        }
        
        tokenStatsDiv.innerHTML = displayText;
        tokenStatsDiv.classList.remove('hidden');
        tokenStatsDiv.classList.add('block');
        
        logger.debug('📊 Updated token stats:', displayText);
    }

    // 🔽 Smart Scroll Functions
    function initializeSendButton() {
        // Estruturar o HTML do botão com texto "Scroll Down"
        sendBtn.innerHTML = `
            <span class="send-text">Send</span>
            <span class="loading hidden">Sending...</span>
            <span class="scroll-text hidden">Scroll Down</span>
        `;
        
        // ✅ Atualizar referências GLOBAIS (sem const)
        sendText = sendBtn.querySelector('.send-text');
        loadingText = sendBtn.querySelector('.loading');
        
        
        updateSendButton();
    }

    function handleSendButtonClick() {
        if (sendBtn.classList.contains('scroll-mode')) {
            // Modo scroll - fazer scroll to bottom
            scrollToBottom();
        } else {
            // Modo normal - enviar mensagem
            sendMessage();
        }
    }

    function handleScroll() {
        const threshold = 100; // pixels do bottom
        const atBottom = isAtBottom(threshold);
        
        // Detectar se usuário scrollou manualmente para cima
        if (!atBottom) {
            userManuallyScrolled = true;
            isScrolledUp = true;
        } else if (atBottom) {
            userManuallyScrolled = false;
            isScrolledUp = false;
        }
        
        updateSendButton();
    }

    function isAtBottom(threshold = 50) {
        const container = messagesContainer;
        return (container.scrollHeight - container.scrollTop - container.clientHeight) <= threshold;
    }

    function updateSendButton() {
        const scrollText = sendBtn.querySelector('.scroll-text');
        const sendTextEl = sendBtn.querySelector('.send-text');
        const loadingEl = sendBtn.querySelector('.loading');
        
        // ✅ CORREÇÃO: Permitir scroll mode durante streaming, só bloquear se inicializando
        if (isScrolledUp && !isInitializing) {
            // Transformar em botão de scroll
            sendBtn.classList.add('scroll-mode');
            
            // ✅ FORÇAR ENABLE e mostrar texto correto
            sendBtn.disabled = false;
            if (scrollText) scrollText.classList.remove('hidden');
            if (sendTextEl) sendTextEl.classList.add('hidden');
            if (loadingEl) loadingEl.classList.add('hidden');
            
        } else {
            // Voltar ao modo normal
            sendBtn.classList.remove('scroll-mode');
            
            // Restaurar estado normal
            if (scrollText) scrollText.classList.add('hidden');
            if (sendTextEl) sendTextEl.classList.remove('hidden');
            
            // Só desabilitar se não estiver inicializando
            if (!isInitializing) {
                sendBtn.disabled = isLoading;
            }
        }
    }

    function scrollToBottom() {
        if (isStreaming) {
            // ⚡ Scroll instantâneo durante streaming para evitar problema de timing
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        } else {
            // 🎨 Smooth scroll quando não há streaming
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight,
                behavior: 'smooth'
            });
        }
        
        // Reset scroll state
        isScrolledUp = false;
        userManuallyScrolled = false;
        updateSendButton();
    }

    // Override original scroll behavior during streaming
    function smartScroll() {
        // Só fazer auto-scroll se usuário estiver no bottom
        if (!userManuallyScrolled && isAtBottom(150)) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    // 📋 Copy Code to Clipboard Function
    window.copyCodeToClipboard = function(button) {
        try {
            // Find the code element within the pre container
            const preContainer = button.closest('.code-block-container');
            const codeElement = preContainer.querySelector('code');
            
            if (!codeElement) {
                logger.error('❌ Code element not found');
                return;
            }
            
            // Get the raw text content (without HTML formatting)
            const codeText = codeElement.textContent || codeElement.innerText;
            
            // Copy to clipboard using the Clipboard API
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(codeText).then(() => {
                    logger.debug('📋 Code copied to clipboard successfully');
                    showCopyFeedback(button);
                }).catch((err) => {
                    logger.error('❌ Failed to copy code:', err);
                    fallbackCopyToClipboard(codeText, button);
                });
            } else {
                // Fallback for older browsers
                fallbackCopyToClipboard(codeText, button);
            }
            
        } catch (error) {
            logger.error('❌ Copy operation failed:', error);
        }
    };
    
    // Fallback copy method for older browsers
    function fallbackCopyToClipboard(text, button) {
        try {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            
            logger.debug('📋 Code copied using fallback method');
            showCopyFeedback(button);
        } catch (error) {
            logger.error('❌ Fallback copy failed:', error);
        }
    }
    
    // Show visual feedback when code is copied
    function showCopyFeedback(button) {
        const copyTextSpan = button.querySelector('.copy-text');
        const copyIconSpan = button.querySelector('.copy-icon');
        
        if (copyTextSpan && copyIconSpan) {
            // Store original content
            const originalText = copyTextSpan.textContent;
            const originalIcon = copyIconSpan.textContent;
            
            // Show success feedback
            copyTextSpan.textContent = 'COPIED!';
            copyIconSpan.textContent = '✅';
            button.style.backgroundColor = '#28a745';
            
            // Reset after 2 seconds
            setTimeout(() => {
                copyTextSpan.textContent = originalText;
                copyIconSpan.textContent = originalIcon;
                button.style.backgroundColor = '';
            }, 2000);
        }
    }

    // Auto-resize textarea - CSP compliant (sem inline styles)
    messageInput.addEventListener('input', function() {
        // Use classes para diferentes tamanhos
        this.classList.remove('height-small', 'height-medium', 'height-large');
        
        if (this.scrollHeight <= 72) {
            this.classList.add('height-small');
        } else if (this.scrollHeight <= 100) {
            this.classList.add('height-medium');
        } else {
            this.classList.add('height-large');
        }
    });
})();
