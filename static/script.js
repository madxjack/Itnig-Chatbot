function addMessage(sender, message, isUser) {
    const messageClass = isUser ? 'bg-primary text-secondary ml-auto' : 'bg-secondary text-white';
    const iconClass = isUser ? 'fa-user' : 'fa-robot';
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.className = `flex items-start ${isUser ? 'justify-end' : ''}`;
    messageElement.innerHTML = `
        ${!isUser ? `
            <div class="w-8 h-8 rounded-full bg-primary text-secondary flex items-center justify-center mr-3">
                <i class="fas ${iconClass}"></i>
            </div>
        ` : ''}
        <div class="max-w-[70%] ${messageClass} rounded-lg p-3 shadow-md">
            <p class="font-semibold mb-1">${sender}</p>
            <p>${message}</p>
        </div>
        ${isUser ? `
            <div class="w-8 h-8 rounded-full bg-secondary text-white flex items-center justify-center ml-3">
                <i class="fas ${iconClass}"></i>
            </div>
        ` : ''}
    `;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addThinkingMessage() {
    const chatMessages = document.getElementById('chat-messages');
    const thinkingElement = document.createElement('div');
    thinkingElement.id = 'thinking-message';
    thinkingElement.className = 'flex items-center';
    thinkingElement.innerHTML = `
        <div class="w-8 h-8 rounded-full bg-primary text-secondary flex items-center justify-center mr-3">
            <i class="fas fa-robot"></i>
        </div>
        <div class="bg-secondary text-white rounded-lg p-3 shadow-md flex items-center">
            <div class="animate-spin rounded-full h-4 w-4 border-2 border-white mr-3"></div>
            <span>Asking Bernat...</span>
        </div>
    `;
    chatMessages.appendChild(thinkingElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeThinkingMessage() {
    const thinkingMessage = document.getElementById('thinking-message');
    if (thinkingMessage) {
        thinkingMessage.remove();
    }
}

function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    if (message !== '') {
        addMessage('You', message, true);
        userInput.value = '';
        addThinkingMessage();

        fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: message }),
        })
        .then(response => response.json())
        .then(data => {
            removeThinkingMessage();
            addMessage('Itnig Team', data.response, false);
        })
        .catch(error => {
            removeThinkingMessage();
            addMessage('System', 'Error: Could not process query', false);
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

    sendButton.addEventListener('click', sendMessage);
});