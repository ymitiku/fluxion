import React from 'react';
import { Box, Typography } from '@mui/material';

interface MessageBubbleProps {
  sender: string;
  content: string;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ sender, content }) => {
  const isUser = sender === 'user';

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
        <Typography variant="body1">{content}</Typography>
      </Box>
    </Box>
  );
};

export default MessageBubble;
