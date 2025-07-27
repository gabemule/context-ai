import * as vscode from 'vscode';
import { ChatPanel } from './chatPanel';

export function activate(context: vscode.ExtensionContext) {
    console.log('Context-AI extension is now active!');

    // Register the open chat command
    const openChatDisposable = vscode.commands.registerCommand('context-ai.openChat', () => {
        ChatPanel.createOrShow(context.extensionUri);
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
