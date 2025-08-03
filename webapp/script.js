class IgnatiusChatApp {
    constructor() {
        this.apiBaseUrl = window.IgnatiusConfig?.apiBaseUrl || 'http://localhost:5001/api/v1';
        this.currentConversationId = null;
        this.isConnected = false;
        this.isLoading = false;
        
        this.initializeElements();
        this.bindEvents();
        this.checkApiConnection();
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.statusText = document.getElementById('statusText');
        this.connectionIndicator = document.getElementById('connectionIndicator');
        this.conversationInfo = document.getElementById('conversationInfo');
        this.conversationId = document.getElementById('conversationId');
        this.conversationTopic = document.getElementById('conversationTopic');
        this.newConversationBtn = document.getElementById('newConversationBtn');
    }

    bindEvents() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        this.newConversationBtn.addEventListener('click', () => this.startNewConversation());
        
        // Auto-resize input
        this.messageInput.addEventListener('input', () => {
            this.updateSendButtonState();
        });
    }

    async checkApiConnection() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/conversations`, {
                method: 'OPTIONS',
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Request-Method': 'POST'
                }
            });
            
            this.setConnectionStatus(true, 'Connected to API');
        } catch (error) {
            console.error('API connection failed:', error);
            this.setConnectionStatus(false, 'API connection failed. Please ensure the service is running.');
        }
    }

    setConnectionStatus(connected, message) {
        this.isConnected = connected;
        this.statusText.textContent = message;
        this.connectionIndicator.classList.toggle('connected', connected);
        this.connectionIndicator.classList.toggle('disconnected', !connected);
        
        this.messageInput.disabled = !connected || this.isLoading;
        this.sendButton.disabled = !connected || this.isLoading;
        
        this.updateSendButtonState();
    }

    updateSendButtonState() {
        const hasMessage = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !this.isConnected || this.isLoading || !hasMessage;
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading || !this.isConnected) return;

        this.setLoadingState(true);
        this.messageInput.value = '';
        this.updateSendButtonState();

        // Add user message to chat
        this.addMessageToChat('user', message);

        try {
            const response = await fetch(`${this.apiBaseUrl}/conversations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    conversation_id: this.currentConversationId,
                    message: message
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            const data = await response.json();
            this.handleConversationResponse(data);

        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessageToChat('system', `Error: ${error.message}`);
        } finally {
            this.setLoadingState(false);
        }
    }

    handleConversationResponse(data) {
        // Update conversation info
        this.currentConversationId = data.conversation_id;
        this.conversationId.textContent = data.conversation_id;
        this.conversationTopic.textContent = data.topic || '-';
        this.conversationInfo.style.display = 'block';

        // Find the latest bot message (last message that's not from user)
        const messages = data.messages || [];
        const latestBotMessage = messages.slice().reverse().find(msg => msg.role === 'bot');
        
        if (latestBotMessage) {
            this.addMessageToChat('bot', latestBotMessage.text);
        }
    }

    addMessageToChat(role, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const textP = document.createElement('p');
        textP.textContent = text;
        
        contentDiv.appendChild(textP);
        messageDiv.appendChild(contentDiv);
        
        // Add timestamp for non-welcome messages
        if (role !== 'system') {
            const timestamp = document.createElement('div');
            timestamp.className = 'message-timestamp';
            timestamp.textContent = new Date().toLocaleTimeString();
            messageDiv.appendChild(timestamp);
        }
        
        this.chatMessages.appendChild(messageDiv);
        
        // Ensure scroll happens after element is rendered
        setTimeout(() => {
            this.scrollToBottom();
        }, 50);
    }

    setLoadingState(loading) {
        this.isLoading = loading;
        this.statusText.textContent = loading ? 'Thinking...' : 'Ready';
        this.messageInput.disabled = loading || !this.isConnected;
        this.sendButton.disabled = loading || !this.isConnected;
        this.sendButton.textContent = loading ? 'Sending...' : 'Send';
        
        if (loading) {
            this.addLoadingIndicator();
        } else {
            this.removeLoadingIndicator();
        }
        
        this.updateSendButtonState();
    }

    addLoadingIndicator() {
        if (document.getElementById('loadingIndicator')) return;
        
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loadingIndicator';
        loadingDiv.className = 'message bot-message loading';
        loadingDiv.innerHTML = `
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(loadingDiv);
        
        // Force scroll to bottom with a small delay to ensure the element is rendered
        setTimeout(() => {
            this.scrollToBottom();
        }, 50);
    }

    removeLoadingIndicator() {
        const indicator = document.getElementById('loadingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    startNewConversation() {
        this.currentConversationId = null;
        this.conversationInfo.style.display = 'none';
        
        // Clear chat messages except welcome
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        this.chatMessages.innerHTML = '';
        if (welcomeMessage) {
            this.chatMessages.appendChild(welcomeMessage);
        }
        
        this.messageInput.focus();
    }

    scrollToBottom() {
        // Use smooth scrolling and ensure it goes to the very bottom
        this.chatMessages.scrollTo({
            top: this.chatMessages.scrollHeight,
            behavior: 'smooth'
        });
        
        // Fallback for browsers that don't support smooth scrolling
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new IgnatiusChatApp();
});