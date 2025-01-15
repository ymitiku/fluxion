import React from 'react';
import { Box, Typography } from '@mui/material';
import MessageBubble from "./MessageBubble";

interface ChatWindowProps {
  messages: { sender: string; content: string }[];
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages }) => {
  return (
    <Box
      sx={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px',
      }}
    >
      {messages.map((msg, idx) => (
        <MessageBubble key={idx} sender={msg.sender} content={msg.content} />
      ))}
    </Box>
  );
};

export default ChatWindow;
