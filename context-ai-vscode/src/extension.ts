import * as vscode from 'vscode';
import { ChatPanel } from './chatPanel';

export function activate(context: vscode.ExtensionContext) {
    console.log('Context-AI extension is now active!');

    // Register the open chat command
    const openChatDisposable = vscode.commands.registerCommand('context-ai.openChat', () => {
        ChatPanel.createOrShow(context.extensionUri);
    });

    // Register the ask selection command
    const askSelectionDisposable = vscode.commands.registerCommand('context-ai.askSelection', () => {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            const selection = editor.selection;
            const selectedText = editor.document.getText(selection);
            
            if (selectedText.trim()) {
                // Create chat panel and send the selected text as a question
                const panel = ChatPanel.createOrShow(context.extensionUri);
                setTimeout(() => {
                    panel.sendQuestion(`Explain this code:\n\`\`\`\n${selectedText}\n\`\`\``);
                }, 100);
            } else {
                vscode.window.showWarningMessage('Please select some code first.');
            }
        }
    });

    // Add commands to subscriptions
    context.subscriptions.push(openChatDisposable);
    context.subscriptions.push(askSelectionDisposable);

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
