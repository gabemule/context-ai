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
                    vscode.Uri.joinPath(extensionUri, 'media')
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
            
            // ✅ GARANTIR que loading para SEMPRE
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
                    stdio: ['pipe', 'pipe', 'pipe']
                });

                console.log(`🚀 Process PID: ${this._chatProcess.pid}`);

                // ✅ DETECTAR falha imediatamente
                if (!this._chatProcess.pid) {
                    console.log(`❌ Process failed to start (PID undefined)`);
                    throw new Error('Process failed to start - PID undefined');
                }

                // ✅ DETECTAR erro de spawn imediatamente
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

            // TODO: Capturar instruções dinâmicamente do Context-AI
            // Por enquanto, usar mock das instruções para garantir UX
            const MOCK_CHAT_INFO = `Ask questions about your codebase. Chat history will be maintained for context.

Special commands:
    /embeddings - Show active embeddings
    /history    - Show chat statistics  
    /clear      - Reset conversation history
    /verbose    - Toggle detailed logging
    /mode       - Change prompt mode (minimal|standard|comprehensive|strict)
    exit        - Quit chat session`;

            const initDataHandler = (data: Buffer) => {
                const chunk = data.toString();
                console.log(`📥 Init chunk (${chunk.length} chars):`, JSON.stringify(chunk));

                // Detectar quando chat está pronto para receber mensagens
                if (chunk.includes('You:')) {
                    console.log('🎯 Chat ready - sending chatReady signal with mock info');

                    // Remove initialization listener
                    this._chatProcess.stdout.off('data', initDataHandler);
                    this._chatProcess.stderr.off('data', initErrorHandler);

                    // Clear timeout
                    clearTimeout(initTimeout);

                    // Send chat ready with mock info (always works)
                    this._panel.webview.postMessage({
                        command: 'chatReady',
                        chatInfo: MOCK_CHAT_INFO
                    });

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

        const dataHandler = (data: Buffer) => {
            if (requestCompleted) return; // Ignore if already completed
            
            const chunk = data.toString();
            console.log(`📥 Received stdout chunk (${chunk.length} chars):`, JSON.stringify(chunk));
            
            // ONLY handle initialization if chat hasn't been initialized yet
            if (!this._chatInitialized) {
                // Detect initialization completion
                if (chunk.includes('You:')) {
                    this._chatInitialized = true;
                    console.log('🎯 Chat initialized - sending chatReady signal');
                    
                    this._panel.webview.postMessage({
                        command: 'chatReady',
                        chatInfo: 'Context-AI chat is ready! You can now ask questions about your codebase.'
                    });
                    return;
                }
                
                // Skip all initialization chunks
                console.log('📋 Skipping initialization chunk');
                return;
            }

            // RESPONSE HANDLING (only after initialization)
            
            // Look for the "You:" prompt OR Rich panel start to know when response is complete
            if (chunk.includes('You:') || 
                chunk.includes('╭─────────────────────────── 🤖 Context-AI\'s Answer')) {
                console.log('🏁 Response complete (found end marker or Rich panel start)');
                cleanupAndResolve(output.trim());
                return;
            }

            // Start collecting after we see streaming indicator
            if (chunk.includes('🌊') || chunk.includes('Streaming Response')) {
                if (!isCollecting) {
                    console.log('🎯 Started streaming response');
                    isCollecting = true;
                    responseStarted = true;
                    
                    // Send stream start message
                    this._panel.webview.postMessage({
                        command: 'streamStart'
                    });
                }
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
        // Local path to main script run in the webview
        const scriptPathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'media', 'chat.js');
        const scriptUri = webview.asWebviewUri(scriptPathOnDisk);

        // Local path to css styles
        const stylePathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'media', 'chat.css');
        const styleUri = webview.asWebviewUri(stylePathOnDisk);

        // Use a nonce to only allow specific scripts to be run
        const nonce = getNonce();

        return `<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource}; script-src 'nonce-${nonce}' https://cdn.jsdelivr.net;">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="${styleUri}" rel="stylesheet">
                <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
                <title>Context-AI Chat</title>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🤖 Context-AI Chat</h1>
                        <button id="clearBtn" class="clear-btn">Clear Chat</button>
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
                            <span class="loading" style="display: none;">Sending...</span>
                        </button>
                    </div>
                    
                    <div class="examples">
                        <p>💡 <strong>Try asking:</strong></p>
                        <div class="example-questions">
                            <button class="example-btn" data-question="How auth works?">
                                🔐 How auth works?
                            </button>
                            <button class="example-btn" data-question="Explain the project architecture and its exports">
                                🏗️ Explain the architecture
                            </button>
                        </div>
                    </div>
                </div>

                <script nonce="${nonce}" src="${scriptUri}"></script>
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
