// Book Advisor Chat Application

const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const chatForm = document.getElementById('chat-form');
const examplesModal = document.getElementById('examples-modal');
const examplesList = document.getElementById('examples-list');

// Load chat history on page load
window.addEventListener('load', () => {
    loadChatHistory();
    messageInput.focus();
});

// Handle form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input and disable form
    messageInput.value = '';
    messageInput.disabled = true;
    document.querySelector('.send-btn').disabled = true;
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send message to server
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        if (response.ok) {
            // Add bot response
            addMessage(data.answer, 'bot');
        } else {
            // Show error message
            addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();
        addMessage('Sorry, I couldn\'t connect to the server. Please try again.', 'bot');
    } finally {
        // Re-enable form
        messageInput.disabled = false;
        document.querySelector('.send-btn').disabled = false;
        messageInput.focus();
    }
});

// Add message to chat
function addMessage(content, sender) {
    // Remove welcome message if it exists
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const icon = document.createElement('div');
    icon.className = 'message-icon';
    icon.textContent = sender === 'user' ? '👤' : '📚';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Process content for formatting
    if (sender === 'bot') {
        contentDiv.innerHTML = formatBotMessage(content);
    } else {
        contentDiv.textContent = content;
    }
    
    messageDiv.appendChild(icon);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format bot message with markdown-like styling
function formatBotMessage(content) {
    // Convert markdown-like formatting to HTML
    let formatted = content
        // Headers
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        // Bullet points
        .replace(/^• (.+)$/gm, '<li>$1</li>')
        // Line breaks
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    
    // Wrap in paragraphs
    formatted = '<p>' + formatted + '</p>';
    
    // Wrap consecutive li elements in ul
    formatted = formatted.replace(/(<li>.*?<\/li>(\s*<br>\s*)?)+/g, (match) => {
        return '<ul>' + match.replace(/<br>/g, '') + '</ul>';
    });
    
    return formatted;
}

// Show typing indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot typing';
    typingDiv.id = 'typing-indicator';
    
    const icon = document.createElement('div');
    icon.className = 'message-icon';
    icon.textContent = '📚';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content typing-indicator';
    contentDiv.innerHTML = '<span></span><span></span><span></span>';
    
    typingDiv.appendChild(icon);
    typingDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Load chat history
async function loadChatHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        
        if (data.history && data.history.length > 0) {
            // Remove welcome message
            const welcomeMessage = document.querySelector('.welcome-message');
            if (welcomeMessage) {
                welcomeMessage.remove();
            }
            
            // Add historical messages
            data.history.forEach(entry => {
                addMessage(entry.question, 'user');
                addMessage(entry.answer, 'bot');
            });
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Clear chat
async function clearChat() {
    if (!confirm('Are you sure you want to clear the chat history?')) {
        return;
    }
    
    try {
        await fetch('/api/clear', { method: 'POST' });
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <h2>Welcome! Ask me anything.</h2>
                <p>I can provide advice based on insights from:</p>
                <ul>
                    <li><strong>Steve Jobs</strong> - Leadership, innovation, and life decisions</li>
                    <li><strong>Daniel Kahneman</strong> - Decision-making and thinking strategies</li>
                    <li><strong>The Innovators</strong> - Lessons from history's greatest innovators</li>
                    <li><strong>Sapiens</strong> - Understanding human nature and society</li>
                </ul>
            </div>
        `;
    } catch (error) {
        console.error('Error clearing chat:', error);
    }
}

// Show example questions
async function askExample() {
    try {
        const response = await fetch('/api/examples');
        const data = await response.json();
        
        examplesList.innerHTML = '';
        data.examples.forEach(example => {
            const div = document.createElement('div');
            div.className = 'example-question';
            div.textContent = example;
            div.onclick = () => {
                messageInput.value = example;
                closeModal();
                messageInput.focus();
            };
            examplesList.appendChild(div);
        });
        
        examplesModal.style.display = 'block';
    } catch (error) {
        console.error('Error loading examples:', error);
    }
}

// Close modal
function closeModal() {
    examplesModal.style.display = 'none';
}

// Close modal when clicking outside
window.onclick = (event) => {
    if (event.target === examplesModal) {
        closeModal();
    }
};

// Handle Enter key in input
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});