import * as vscode from 'vscode';
import { ChatViewProvider } from './chatViewProvider';

export function activate(context: vscode.ExtensionContext) {
    console.log('Context-AI extension is now active!');

    // Create and register the chat view provider
    const chatViewProvider = new ChatViewProvider(context.extensionUri);
    
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            ChatViewProvider.viewType,
            chatViewProvider
        )
    );

    // Register the open chat command to focus the view
    const openChatDisposable = vscode.commands.registerCommand('context-ai.openChat', () => {
        // Focus the chat view directly
        vscode.commands.executeCommand('contextAiChat.focus');
        chatViewProvider.focus();
    });

    // Add commands to subscriptions
    context.subscriptions.push(openChatDisposable);

    // Show welcome message on first activation
    const hasShownWelcome = context.globalState.get('context-ai.hasShownWelcome', false);
    if (!hasShownWelcome) {
        vscode.window.showInformationMessage(
            'Context-AI extension activated! Use Ctrl+Shift+C to open chat.',
            'Open Chat Now'
        ).then(selection => {
            if (selection === 'Open Chat Now') {
                vscode.commands.executeCommand('context-ai.openChat');
            }
        });
        context.globalState.update('context-ai.hasShownWelcome', true);
    }
}

export function deactivate() {
    console.log('Context-AI extension deactivated');
}
