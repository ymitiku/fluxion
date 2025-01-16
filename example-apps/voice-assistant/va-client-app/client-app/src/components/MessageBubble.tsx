import React from 'react';
import { Box, Typography } from '@mui/material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { dracula } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ReactMarkdown from 'react-markdown';

interface MessageBubbleProps {
  sender: string;
  content: string;
  audioUrl: string | null; // Optional audio URL for voice messages
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ sender, content, audioUrl }) => {
  const isUser = sender === 'user';

  const parseMessage = (message: string) => {
    const codeRegex = /```(\w+)?\n([\s\S]*?)```/g; // Matches code blocks
    const parts = [];
    let lastIndex = 0;

    let match;
    while ((match = codeRegex.exec(message)) !== null) {
      // Push non-code content before the match
      if (lastIndex < match.index) {
        parts.push({ type: 'text', content: message.slice(lastIndex, match.index) });
      }

      // Push the code block
      const language = match[1] || 'plaintext'; // Default to plaintext if no language is specified
      parts.push({ type: 'code', content: match[2], language });

      lastIndex = codeRegex.lastIndex;
    }

    // Push remaining non-code content
    if (lastIndex < message.length) {
      parts.push({ type: 'text', content: message.slice(lastIndex) });
    }

    return parts;
  };

  const renderCodeBlock = (code: string, language: string) => {
    return (
      <SyntaxHighlighter
        language={language}
        style={dracula}
        customStyle={{
          margin: 0,
          padding: '8px',
          borderRadius: '4px',
          backgroundColor: '#2d2d2d',
          fontSize: '0.9rem',
          whiteSpace: 'pre-wrap',
        }}
      >
        {code}
      </SyntaxHighlighter>
    );
  }

  const renderTextMarkdown = (text: string) => {
    return <ReactMarkdown>{text}</ReactMarkdown>;
  }


  const renderMarkdownParts = (parsedMessage: { type: string; content: string; language?: string }[]) => {
    return parsedMessage.map((part, _) => {
      if (part.type === 'text') {
        return renderTextMarkdown(part.content);
      } else if (part.type === 'code') {
        return renderCodeBlock(part.content, part.language? part.language : 'plaintext');
      }
    })
  }

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '8px',
      }}
    >
      <Box
        sx={{
          padding: '8px 16px',
          backgroundColor: isUser ? '#1976d2' : '#e0e0e0',
          color: isUser ? '#fff' : '#000',
          borderRadius: '16px',
          maxWidth: '60%',
        }}
      >
        {isUser ?<Typography variant="body1">{content}</Typography> : renderMarkdownParts(parseMessage(content))}
        
        {/* Render the audio player if audioUrl is provided */}
        {audioUrl && (
          <Box
            sx={{
              marginTop: '8px',
              display: 'flex',
              justifyContent: sender === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            <audio controls style={{ width: '100%' }}>
              <source src={audioUrl} type="audio/webm" />
              Your browser does not support the audio element.
            </audio>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default MessageBubble;
