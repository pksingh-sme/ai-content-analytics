import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const ChatContainer = styled.div`
  max-width: 900px;
  margin: 0 auto;
  height: 80vh;
  display: flex;
  flex-direction: column;
`;

const ChatHeader = styled.div`
  padding: 1rem;
  background-color: #2c3e50;
  color: white;
  border-radius: 8px 8px 0 0;
`;

const ChatMessages = styled.div`
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  background-color: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-top: none;
`;

const MessageContainer = styled.div<{ isUser: boolean }>`
  display: flex;
  margin-bottom: 1.5rem;
  justify-content: ${props => props.isUser ? 'flex-end' : 'flex-start'};
`;

const MessageBubble = styled.div<{ isUser: boolean }>`
  max-width: 80%;
  padding: 1rem;
  border-radius: 18px;
  background-color: ${props => props.isUser ? '#3498db' : '#e9ecef'};
  color: ${props => props.isUser ? 'white' : '#212529'};
  margin: 0 1rem;
`;

const MessageContent = styled.div`
  line-height: 1.5;
  
  p {
    margin: 0.5rem 0;
  }
  
  pre, code {
    background-color: rgba(0,0,0,0.05);
    padding: 0.5rem;
    border-radius: 4px;
    overflow-x: auto;
  }
`;

const ChatInput = styled.div`
  display: flex;
  padding: 1rem;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-top: none;
  border-radius: 0 0 8px 8px;
`;

const MessageInput = styled.input`
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
`;

const SendButton = styled.button`
  margin-left: 0.5rem;
  padding: 0.75rem 1.5rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;

  &:hover {
    background-color: #2980b9;
  }

  &:disabled {
    background-color: #bdc3c7;
    cursor: not-allowed;
  }
`;

const TypingIndicator = styled.div`
  padding: 0.5rem 1rem;
  color: #7f8c8d;
  font-style: italic;
`;

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  sources?: any[];
}

const ChatSection: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m your AI assistant. Ask me anything about your uploaded content.',
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Call backend API
      const response = await axios.post('http://localhost:8000/api/v1/query', {
        query: inputValue,
        top_k: 5,
        include_sources: true
      });

      // Add AI response
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.data.response,
        isUser: false,
        timestamp: new Date(),
        sources: response.data.sources
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <ChatContainer>
      <ChatHeader>
        <h2>AI-Powered Chat</h2>
        <p>Ask questions about your uploaded content</p>
      </ChatHeader>
      
      <ChatMessages>
        {messages.map((message) => (
          <MessageContainer key={message.id} isUser={message.isUser}>
            <MessageBubble isUser={message.isUser}>
              <MessageContent>
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </MessageContent>
            </MessageBubble>
          </MessageContainer>
        ))}
        
        {isLoading && (
          <MessageContainer isUser={false}>
            <MessageBubble isUser={false}>
              <TypingIndicator>AI is thinking...</TypingIndicator>
            </MessageBubble>
          </MessageContainer>
        )}
        
        <div ref={messagesEndRef} />
      </ChatMessages>
      
      <ChatInput>
        <MessageInput
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about your content..."
          disabled={isLoading}
        />
        <SendButton onClick={handleSendMessage} disabled={isLoading || !inputValue.trim()}>
          Send
        </SendButton>
      </ChatInput>
    </ChatContainer>
  );
};

export default ChatSection;