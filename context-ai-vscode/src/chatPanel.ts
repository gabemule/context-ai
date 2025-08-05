import * as vscode from 'vscode';
import { spawn } from 'child_process';
import * as path from 'path';

export class ChatPanel {
    public static currentPanel: ChatPanel | undefined;
    public static readonly viewType = 'contextAIChat';

    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];

    public static createOrShow(extensionUri: vscode.Uri): ChatPanel {
        const column = vscode.window.activeTextEditor
            ? vscode.ViewColumn.Beside
            : undefined;

        // If we already have a panel, show it
        if (ChatPanel.currentPanel) {
            ChatPanel.currentPanel._panel.reveal(column);
            return ChatPanel.currentPanel;
        }

        // Otherwise, create a new panel
        const panel = vscode.window.createWebviewPanel(
            ChatPanel.viewType,
            'Context-AI Chat',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'media'),
                    vscode.Uri.joinPath(extensionUri, 'out'),
                    vscode.Uri.joinPath(extensionUri, 'node_modules')
                ]
            }
        );

        ChatPanel.currentPanel = new ChatPanel(panel, extensionUri);
        return ChatPanel.currentPanel;
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        // Set the webview's initial html content
        this._update();

        // Listen for when the panel is disposed
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.command) {
                    case 'sendMessage':
                        await this._handleSendMessage(message.text);
                        break;
                    case 'clearChat':
                        this._panel.webview.postMessage({
                            command: 'clearMessages'
                        });
                        break;
                }
            },
            null,
            this._disposables
        );

        // Pre-initialize chat process when panel opens for better UX
        this._initializeChatProcess().catch((error) => {
            console.log('⚠️ Pre-initialization failed, will retry on first question:', error.message);
        });
    }

    public sendQuestion(question: string) {
        this._panel.webview.postMessage({
            command: 'addQuestion',
            text: question
        });
        this._handleSendMessage(question);
    }

    private async _handleSendMessage(text: string) {
        try {
            console.log('🚀 _handleSendMessage START:', text);
            
            // Show loading state
            this._panel.webview.postMessage({
                command: 'showLoading',
                isLoading: true
            });

            // Execute context-ai CLI
            await this._executeContextAI(text);

            console.log('✅ _executeContextAI completed, sending streamComplete');
            
            this._panel.webview.postMessage({
                command: 'streamComplete'
            });

            console.log('🏁 _handleSendMessage SUCCESS completed');

        } catch (error) {
            console.log('❌ _handleSendMessage ERROR:', error);
            
            // Handle errors - only send receiveMessage for errors
            this._panel.webview.postMessage({
                command: 'receiveMessage',
                text: `❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
                isLoading: false,
                isError: true
            });
        }
    }

    private _chatProcess: any = null;
    private _isInitializing = false;
    private _isProcessing = false;
    private _chatInitialized = false;

    private _executeContextAI(question: string): Promise<string> {
        return new Promise(async (resolve, reject) => {
            try {
                // Prevent duplicate processing
                if (this._isProcessing) {
                    reject(new Error('Another question is already being processed'));
                    return;
                }

                this._isProcessing = true;

                // Initialize chat process if needed
                if (!this._chatProcess && !this._isInitializing) {
                    await this._initializeChatProcess();
                }

                if (!this._chatProcess) {
                    this._isProcessing = false;
                    reject(new Error('Failed to initialize Context-AI chat process'));
                    return;
                }

                // Send question to chat process
                this._sendQuestionToChat(question, 
                    (result: string) => {
                        this._isProcessing = false;
                        resolve(result);
                    }, 
                    (error: Error) => {
                        this._isProcessing = false;
                        reject(error);
                    }
                );

            } catch (error) {
                this._isProcessing = false;
                reject(error);
            }
        });
    }

    private async _initializeChatProcess(): Promise<void> {
        this._isInitializing = true;

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        const cwd = workspaceFolder ? workspaceFolder.uri.fsPath : process.cwd();

        console.log('🚀 Initializing Context-AI chat process...');
        console.log('📁 Working directory:', cwd);
        console.log('🏠 HOME directory:', process.env.HOME);

        // Try different possible commands for chat
        const possibleCommands = [
            'context-ai',
            `${process.env.HOME}/.local/bin/context-ai`,
            '/opt/homebrew/bin/context-ai',
            '/usr/local/bin/context-ai',
            'python3 -m src.cli',
            'python -m src.cli',
            'poetry run context-ai'
        ];

        console.log('🔧 Will try these commands:', possibleCommands);

        for (const command of possibleCommands) {
            try {
                let cmd: string;
                let cmdArgs: string[];

                if (command.startsWith('python3 -m src.cli')) {
                    cmd = 'python3';
                    cmdArgs = ['-m', 'src.cli', 'chat'];
                } else if (command.startsWith('python -m src.cli')) {
                    cmd = 'python';
                    cmdArgs = ['-m', 'src.cli', 'chat'];
                } else if (command.includes('poetry')) {
                    cmd = 'poetry';
                    cmdArgs = ['run', 'context-ai', 'chat'];
                } else {
                    cmd = command;
                    cmdArgs = ['chat'];
                }

                console.log(`🔄 Trying command: ${cmd} ${cmdArgs.join(' ')}`);
                console.log(`📂 CWD: ${cwd}`);
                console.log(`🔧 Shell: false, stdio: pipe`);

                this._chatProcess = spawn(cmd, cmdArgs, {
                    cwd: cwd,
                    shell: false,
                    stdio: ['pipe', 'pipe', 'pipe'],
                    env: {
                        ...process.env,
                        CONTEXT_AI_VSCODE: 'true'  // Enable VSCode integration mode
                    }
                });

                console.log(`🚀 Process PID: ${this._chatProcess.pid}`);

                if (!this._chatProcess.pid) {
                    console.log(`❌ Process failed to start (PID undefined)`);
                    throw new Error('Process failed to start - PID undefined');
                }

                this._chatProcess.on('error', (error: Error) => {
                    console.log(`❌ Process spawn error: ${error.message}`);
                    throw error;
                });

                // Set up initialization listener to capture chat ready info
                await this._waitForChatInitialization();

                // Process started successfully
                console.log('🎉 Chat process initialized successfully!');
                this._isInitializing = false;
                this._chatInitialized = true;
                return;

            } catch (error) {
                console.log(`❌ Command failed: ${error instanceof Error ? error.message : error}`);
                // Try next command
                continue;
            }
        }

        this._isInitializing = false;
        throw new Error(`Could not start Context-AI chat. Tried commands: ${possibleCommands.join(', ')}`);
    }

    private async _waitForChatInitialization(): Promise<void> {
        return new Promise((resolve, reject) => {
            let initTimeout: NodeJS.Timeout;
            let accumulatedInitOutput = ''; // Accumulate chunks for panel processing

            const initDataHandler = (data: Buffer) => {
                const chunk = data.toString();
                console.log(`📥 Init chunk (${chunk.length} chars):`, JSON.stringify(chunk));
                
                // Accumulate output for panel processing
                accumulatedInitOutput += chunk;
                
                // Process panels during initialization
                this.processCompletePanels(accumulatedInitOutput);

                // Detectar quando chat está pronto para receber mensagens
                if (chunk.includes('#= Context-AI Loaded =#')) {
                    console.log('🎯 Chat ready - initialization complete (Context-AI Loaded marker found)');

                    // Remove initialization listener
                    this._chatProcess.stdout.off('data', initDataHandler);
                    this._chatProcess.stderr.off('data', initErrorHandler);

                    // Clear timeout
                    clearTimeout(initTimeout);

                    // Panel processing already handled by processCompletePanels above
                    resolve();
                    return;
                }
            };

            const initErrorHandler = (data: Buffer) => {
                const error = data.toString();
                console.log(`🚨 Init stderr:`, JSON.stringify(error));
                if (error.includes('error') || error.includes('Error')) {
                    this._chatProcess.stdout.off('data', initDataHandler);
                    this._chatProcess.stderr.off('data', initErrorHandler);
                    clearTimeout(initTimeout);
                    reject(new Error(`Context-AI initialization error: ${error}`));
                }
            };

            // Set up listeners
            this._chatProcess.stdout.on('data', initDataHandler);
            this._chatProcess.stderr.on('data', initErrorHandler);

            // Timeout after 30 seconds
            initTimeout = setTimeout(() => {
                console.log('⏰ Initialization timeout after 30s');
                this._chatProcess.stdout.off('data', initDataHandler);
                this._chatProcess.stderr.off('data', initErrorHandler);
                reject(new Error('Initialization timeout after 30 seconds'));
            }, 30000);
        });
    }

    private _sendQuestionToChat(question: string, resolve: Function, reject: Function): void {
        if (!this._chatProcess) {
            reject(new Error('Chat process not initialized'));
            return;
        }

        console.log(`📨 Sending question to chat: "${question}"`);

        let output = '';
        let isCollecting = false;
        let responseStarted = false;
        let requestCompleted = false;

        const cleanupAndResolve = (result: string) => {
            if (requestCompleted) return;
            requestCompleted = true;
            
            console.log('🧹 Cleaning up listeners and resolving');
            this._chatProcess.stdout.off('data', dataHandler);
            this._chatProcess.stderr.off('data', errorHandler);
            
            // Send completion signal
            this._panel.webview.postMessage({
                command: 'streamComplete'
            });
            
            resolve(result);
        };

        const cleanupAndReject = (error: Error) => {
            if (requestCompleted) return;
            requestCompleted = true;
            
            console.log('🧹 Cleaning up listeners and rejecting');
            this._chatProcess.stdout.off('data', dataHandler);
            this._chatProcess.stderr.off('data', errorHandler);
            reject(error);
        };

        let accumulatedOutput = ''; // Accumulate chunks for token stats detection
        
        const dataHandler = (data: Buffer) => {
            if (requestCompleted) return; // Ignore if already completed
            
            const chunk = data.toString();
            console.log(`📥 Received stdout chunk (${chunk.length} chars):`, JSON.stringify(chunk));
            
            // Accumulate all output for token stats detection
            accumulatedOutput += chunk;
            
            // Check for complete Rich panels (generic detection)
            const shouldStopCollecting = this.processCompletePanels(accumulatedOutput);
            if (shouldStopCollecting && isCollecting) {
                console.log('🎯 Stopping chunk streaming due to Answer panel detection');
                isCollecting = false;
            }
            
            // ONLY handle initialization if chat hasn't been initialized yet
            if (!this._chatInitialized) {
                // Detect initialization completion with safe marker
                if (chunk.includes('#= Context-AI Loaded =#')) {
                    this._chatInitialized = true;
                    console.log('🎯 Chat initialized - waiting for dynamic panel content (Context-AI Loaded marker)');
                    // Don't send chatReady here - let processCompletePanels handle it with dynamic content
                    return;
                }
                
                // Skip all initialization chunks
                console.log('📋 Skipping initialization chunk');
                return;
            }

            // RESPONSE HANDLING (only after initialization)
            
            // Only stop when we see Context-AI End marker (this comes after panel ends and stats are sent)
            if (chunk.includes('#= Context-AI End =#')) {
                console.log('🏁 Response complete (found Context-AI End marker - panel closed, stats sent)');
                cleanupAndResolve(output.trim());
                return;
            }

            // Start collecting when we see streaming start marker
            if (chunk.includes('#= Context-AI Streaming START =#')) {
                if (!isCollecting) {
                    console.log('🎯 Started streaming response (Context-AI Streaming START marker)');
                    isCollecting = true;
                    responseStarted = true;
                    
                    // Send stream start message
                    this._panel.webview.postMessage({
                        command: 'streamStart'
                    });
                }
                return;
            }

            // Stop collecting when we see streaming end marker
            if (chunk.includes('#= Context-AI Streaming END =#')) {
                console.log('🎯 Streaming ended (Context-AI Streaming END marker)');
                isCollecting = false;
                return;
            }

            // Stream chunks in real-time if we're collecting
            if (isCollecting && responseStarted) {
                output += chunk;
                console.log(`📝 Streaming chunk - total output: ${output.length} chars`);
                
                // Send chunk to UI for real-time display
                this._panel.webview.postMessage({
                    command: 'streamChunk',
                    text: chunk
                });
            }
        };

        const errorHandler = (data: Buffer) => {
            if (requestCompleted) return;
            
            const error = data.toString();
            console.log(`🚨 Received stderr:`, JSON.stringify(error));
            if (error.includes('error') || error.includes('Error')) {
                cleanupAndReject(new Error(`Context-AI error: ${error}`));
            }
        };

        // Set up listeners
        this._chatProcess.stdout.on('data', dataHandler);
        this._chatProcess.stderr.on('data', errorHandler);

        // Send question
        console.log('✍️ Writing question to stdin...');
        this._chatProcess.stdin.write(`${question}\n`);

        // Timeout after 90 seconds (reduced timeout)
        const timeoutId = setTimeout(() => {
            console.log('⏰ Request timeout after 90s');
            cleanupAndReject(new Error('Request timeout after 90 seconds'));
        }, 90000);

        // Clear timeout when request completes
        const originalResolve = resolve;
        const originalReject = reject;
        
        resolve = (result: any) => {
            clearTimeout(timeoutId);
            originalResolve(result);
        };
        
        reject = (error: any) => {
            clearTimeout(timeoutId);
            originalReject(error);
        };
    }

    private processCompletePanels(accumulatedOutput: string): boolean {
        let shouldStopCollecting = false;
        
        // Detectar todos os panels conhecidos automaticamente
        this.detectPanel(accumulatedOutput, 'Token Usage', (panelContent: string) => {
            const stats = this.extractStatsFromTokenPanel(panelContent);
            if (stats) {
                console.log('📊 Successfully extracted token stats from panel:', stats);
                
                // Send stats to webview
                this._panel.webview.postMessage({
                    command: 'updateTokenStats',
                    stats: stats
                });
            }
        });
        
        this.detectPanel(accumulatedOutput, 'Context-AI Chat Session with History', (panelContent: string) => {
            const chatInfo = this.extractChatInfoFromPanel(panelContent);
            if (chatInfo) {
                console.log('🎯 Found dynamic Chat Session panel, sending chatReady');
                
                // Send dynamic chat info instead of mock
                this._panel.webview.postMessage({
                    command: 'chatReady',
                    chatInfo: chatInfo
                });
            } else {
                console.log('⚠️ Chat info extraction failed, sending fallback chatReady');
                
                // Send fallback to ensure loading is removed
                this._panel.webview.postMessage({
                    command: 'chatReady',
                    chatInfo: 'Ask questions about your codebase. Chat history will be maintained for context.\n\nSpecial commands:\n/embeddings - Show active embeddings\n/history - Show chat statistics\n/clear - Reset conversation history\n/verbose - Toggle detailed logging\n/mode - Change prompt mode\nexit - Quit chat session'
                });
            }
        });
        
        
        return shouldStopCollecting;
    }

    private detectPanel(
        accumulatedOutput: string, 
        panelTitle: string, 
        onPanelFound: (panelContent: string) => void
    ): void {
        if (accumulatedOutput.includes(panelTitle) &&
            accumulatedOutput.includes('╭───') &&
            accumulatedOutput.includes('───╮') &&
            accumulatedOutput.includes('╰───') &&
            accumulatedOutput.includes('───╯')) {
            
            console.log(`🎯 Found complete ${panelTitle} panel`);
            onPanelFound(accumulatedOutput);
        }
    }

    private extractStatsFromTokenPanel(panelText: string): any {
        try {
            // Extract data from Rich panel text
            // Look for patterns like:
            // "Total: 100,411 tokens (50.2%)"
            // "Input: 98,420 • Output: 1,991"
            // "Breakdown: 91K code + 1K history"
            
            const totalMatch = panelText.match(/Total:\s*([\d,]+)\s*tokens\s*\(([\d.]+)%\)/);
            const inputOutputMatch = panelText.match(/Input:\s*([\d,]+)\s*•\s*Output:\s*([\d,]+)/);
            const breakdownMatch = panelText.match(/Breakdown:\s*(.+?)(?:\n|$)/);
            
            if (totalMatch && inputOutputMatch) {
                const totalTokens = parseInt(totalMatch[1].replace(/,/g, ''));
                const percentage = parseFloat(totalMatch[2]);
                const inputTokens = parseInt(inputOutputMatch[1].replace(/,/g, ''));
                const outputTokens = parseInt(inputOutputMatch[2].replace(/,/g, ''));
                const breakdown = breakdownMatch ? breakdownMatch[1].trim() : '';
                
                return {
                    total_tokens: totalTokens,
                    percentage: percentage,
                    input_tokens: inputTokens,
                    output_tokens: outputTokens,
                    breakdown: breakdown
                };
            }
        } catch (error) {
            console.error('❌ Failed to extract stats from Token Usage panel:', error);
        }
        
        return null;
    }

    private extractChatInfoFromPanel(panelText: string): string | null {
        try {
            // Extract content from Rich panel, removing borders and formatting
            // Look for the panel content between the borders
            
            // Simpler approach: find content between ╭─── and ╰───
            const panelStart = panelText.indexOf('╭───');
            const panelEnd = panelText.indexOf('╰───');
            
            if (panelStart !== -1 && panelEnd !== -1 && panelEnd > panelStart) {
                let content = panelText.substring(panelStart, panelEnd + 10); // Include closing border
                
                // Extract just the text lines, removing borders
                const lines = content.split('\n');
                const contentLines = [];
                
                for (const line of lines) {
                    // Remove lines that are just borders
                    if (line.includes('╭───') || line.includes('╰───') || line.includes('─')) {
                        continue;
                    }
                    
                    // Clean line: remove │ and leading/trailing spaces
                    const cleanLine = line.replace(/^[\s]*│[\s]*/, '').replace(/[\s]*│[\s]*$/, '').trim();
                    
                    // Only add non-empty lines
                    if (cleanLine) {
                        contentLines.push(cleanLine);
                    }
                }
                
                const finalContent = contentLines.join('\n').trim();
                
                if (finalContent && finalContent.length > 10) {
                    console.log('📝 Extracted chat info from panel:', finalContent.substring(0, 100) + '...');
                    return finalContent;
                }
            }
            
            console.log('⚠️ Could not extract chat info from panel, using fallback');
            return null;
            
        } catch (error) {
            console.error('❌ Failed to extract chat info from panel:', error);
            return null;
        }
    }

    public dispose() {
        ChatPanel.currentPanel = undefined;

        // Clean up chat process
        if (this._chatProcess) {
            this._chatProcess.kill();
            this._chatProcess = null;
        }

        // Clean up our resources
        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private _update() {
        const webview = this._panel.webview;
        this._panel.webview.html = this._getHtmlForWebview(webview);
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        // Local paths for CSS and JS  
        const bundledScriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'out', 'media', 'chat.bundle.js'));
        const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'out', 'media', 'chat.css'));

        // Use a nonce to only allow specific scripts to be run
        const nonce = getNonce();
        
        console.log('🔧 DEBUG: Creating webview HTML');
        console.log('🔧 bundledScriptUri:', bundledScriptUri.toString());
        console.log('🔧 styleUri:', styleUri.toString());
        console.log('🔧 nonce:', nonce);

        return `<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self' 'unsafe-inline' 'unsafe-eval' vscode-resource:; script-src-elem 'self' 'unsafe-inline' vscode-resource:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https: vscode-resource:; font-src 'self' https: vscode-resource:;">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="${styleUri}" rel="stylesheet">
                
                <!-- ✅ HIGHLIGHT.JS DEFAULT THEME CSS -->
                <link href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.11.1/build/styles/monokai.min.css" rel="stylesheet">
                
                <title>Context-AI Chat</title>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="header-row">
                            <h1>🤖 Context-AI Chat</h1>
                            <button id="clearBtn" class="clear-btn">Clear Chat</button>
                        </div>
                        <div id="tokenStats" class="token-stats hidden"></div>
                    </div>
                    
                    <div id="messages" class="messages"></div>
                    
                    <div class="input-container">
                        <textarea 
                            id="messageInput" 
                            placeholder="Ask Context-AI about your codebase..." 
                            rows="3"
                        ></textarea>
                        <button id="sendBtn" class="send-btn">
                            <span class="send-text">Send</span>
                            <span class="loading hidden">Sending...</span>
                        </button>
                    </div>
                    
                    <div class="examples">
                        <p>💡 <strong>Try asking:</strong></p>
                        <div class="example-questions">
                            <button class="example-btn" data-question="How auth works?">
                                🔐 How auth works?
                            </button>
                            <button class="example-btn" data-question="Explain the project architecture">
                                🏗️ Explain the architecture
                            </button>
                            <button class="example-btn" data-question="Detail the libraries and its exports">
                                📚 Detail libraries
                            </button>
                        </div>
                    </div>
                </div>

                <!-- ✅ BUNDLED SCRIPT -->
                <script src="${bundledScriptUri}"></script>
            </body>
            </html>`;
    }
}

function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
