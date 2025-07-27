(function() {
    const vscode = acquireVsCodeApi();
    
    // DOM elements
    const messagesContainer = document.getElementById('messages');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const clearBtn = document.getElementById('clearBtn');
    const sendText = sendBtn.querySelector('.send-text');
    const loadingText = sendBtn.querySelector('.loading');
    
    let isLoading = false;
    let currentLoadingMessage = null;
    let isStreaming = false;
    let currentStreamingMessage = null;
    let isInitializing = true;
    let initializationStatus = null;
    let chatInfoShown = false;
    let rawStreamContent = '';

    // Initialize
    init();

    function init() {
        // Show empty state initially
        showEmptyState();
        
        // Event listeners
        sendBtn.addEventListener('click', sendMessage);
        clearBtn.addEventListener('click', clearChat);
        messageInput.addEventListener('keydown', handleKeyDown);
        
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
        
        // Process markdown-like formatting
        contentDiv.innerHTML = formatMessage(text);

        messageDiv.appendChild(headerDiv);
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        return messageDiv;
    }

    function formatMessage(text) {
        // Basic markdown formatting for better display
        let formatted = text
            // Headers
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Code blocks
            .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
            // Inline code
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            // Lists
            .replace(/^\* (.*$)/gm, '<li>$1</li>')
            .replace(/^- (.*$)/gm, '<li>$1</li>')
            // Line breaks
            .replace(/\n/g, '<br>');

        // Wrap consecutive list items in ul tags
        formatted = formatted.replace(/(<li>.*<\/li>)(\s*<br>\s*<li>.*<\/li>)*/g, (match) => {
            return '<ul>' + match.replace(/<br>\s*/g, '') + '</ul>';
        });

        return formatted;
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
        console.log('🧹 removeLoadingMessage called, currentLoadingMessage:', currentLoadingMessage);
        
        if (currentLoadingMessage) {
            console.log('🧹 Removing loading message');
            currentLoadingMessage.remove();
            currentLoadingMessage = null;
            console.log('🧹 Loading message removed successfully');
        } else {
            console.log('🧹 No currentLoadingMessage to remove');
        }
    }

    function setLoading(loading) {
        isLoading = loading;
        
        if (loading && !isInitializing) { // ✅ SÓ mostrar se não estiver inicializando
            sendBtn.disabled = true;
            sendText.style.display = 'none';
            loadingText.style.display = 'inline';
            showHeaderLoading(); // ✅ USAR header loading
        } else if (!loading) {
            sendBtn.disabled = false;
            sendText.style.display = 'inline';
            loadingText.style.display = 'none';
            hideHeaderLoading(); // ✅ ESCONDER header loading
        }
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
                clearChat();
                break;
                
            case 'addQuestion':
                addMessage(message.text, 'user');
                hideEmptyState();
                break;
                
            case 'streamStart':
                // Start streaming - MANTER loading ativo
                console.log('🎯 streamStart - starting streaming (keeping header loading)');
                startStreaming();
                break;
                
            case 'streamChunk':
                // Add chunk to streaming message
                appendStreamChunk(message.text);
                break;
                
            case 'streamComplete':
                // Complete streaming and remove loading
                console.log('🎯 streamComplete - removing header loading');
                setLoading(false);
                completeStreaming();
                break;
                
            case 'chatReady':
                // Chat is ready - remove initialization status and enable input
                console.log('🎯 chatReady received:', message);
                console.log('🎯 chatInfo:', message.chatInfo);
                console.log('🎯 chatInfoShown:', chatInfoShown);
                
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
                console.log('🎯 Using info:', infoToShow);
                
                if (!chatInfoShown) {
                    console.log('🎯 Calling showChatInfo...');
                    showChatInfo(infoToShow);
                    chatInfoShown = true;
                    console.log('🎯 showChatInfo completed');
                } else {
                    console.log('🎯 chatInfoShown already true, skipping');
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
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
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
        
        // Apply markdown formatting that preserves line breaks
        const formattedContent = formatMarkdownPreservingBreaks(rawStreamContent);
        
        // Update content with formatted markdown
        contentDiv.innerHTML = formattedContent;
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function formatMarkdownPreservingBreaks(text) {
        // ✅ NORMALIZAR quebras de linha antes da formatação
        let normalized = text
            // Remove quebras triplas ou mais, mantém máximo 2
            .replace(/\n{3,}/g, '\n\n')
            // Remove quebras extras entre bullets
            .replace(/([•\-\*].*?)\n{2,}(?=[•\-\*])/g, '$1\n')
            // Remove quebras extras entre listas numeradas
            .replace(/(\d+\..*?)\n{2,}(?=\d+\.)/g, '$1\n')
            // Remove quebra extra antes de emojis de seção
            .replace(/\n{2,}(?=[🎯🔧🔑🛡️🔄])/g, '\n')
            .trim();

        // Apply markdown formatting while preserving line breaks
        let formatted = normalized
            // Headers (preserve line breaks)
            .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
            .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
            .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
            
            // Code blocks (preserve content inside)
            .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
            
            // Bold/Italic
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            
            // Inline code
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            
            // Lists (preserve line structure)
            .replace(/^\* (.*$)/gm, '<li>$1</li>')
            .replace(/^- (.*$)/gm, '<li>$1</li>');

        // Wrap consecutive list items in ul tags
        formatted = formatted.replace(/(<li>.*<\/li>\n?)+/g, (match) => {
            return '<ul>' + match + '</ul>';
        });

        // Since we're using CSS white-space: pre-wrap, we keep \n as \n
        // The CSS will handle rendering line breaks properly
        return formatted;
    }

    function completeStreaming() {
        isStreaming = false;
        
        if (currentStreamingMessage) {
            // Apply final formatting on completion
            const contentDiv = currentStreamingMessage.querySelector('.message-content');
            if (rawStreamContent) {
                contentDiv.innerHTML = formatMarkdownPreservingBreaks(rawStreamContent);
            }
            
            // Remove streaming class
            currentStreamingMessage.classList.remove('streaming');
            currentStreamingMessage = null;
        }
        
        // Reset raw content
        rawStreamContent = '';
    }

    function showChatInfo(rawChatInfo) {
        console.log('🎯 showChatInfo START with:', rawChatInfo);
        
        // Clean up the raw chat info - remove box drawing characters and format nicely
        const cleanedInfo = rawChatInfo
            .replace(/[╭╮╰╯─│]/g, '') // Remove box drawing characters
            .replace(/^\s*🤖.*?Session.*?\n/gm, '') // Remove header line
            .replace(/^\s*$/gm, '') // Remove empty lines
            .trim();

        console.log('🎯 cleanedInfo:', cleanedInfo);

        // Extract key information
        const lines = cleanedInfo.split('\n').filter(line => line.trim());
        console.log('🎯 lines:', lines);
        
        let embeddings = '';
        let description = '';
        let commands = [];
        
        let currentSection = '';
        
        for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('Using embeddings:')) {
                embeddings = trimmed.replace('Using embeddings:', '').trim();
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

        console.log('🎯 parsed data - embeddings:', embeddings, 'description:', description, 'commands:', commands);

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
        
        console.log('🎯 generated html:', html);
        
        infoDiv.innerHTML = html;
        console.log('🎯 appending to messagesContainer, current children:', messagesContainer.children.length);
        messagesContainer.appendChild(infoDiv);
        console.log('🎯 after append, children:', messagesContainer.children.length);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        console.log('🎯 showChatInfo COMPLETE');
    }

    // Auto-resize textarea
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 150) + 'px';
    });
})();
