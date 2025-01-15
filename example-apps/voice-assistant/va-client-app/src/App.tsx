import React, { useState } from 'react';
import { Box, CssBaseline, Typography } from '@mui/material';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';

const App: React.FC = () => {
  const [messages, setMessages] = useState<
    { sender: string; content: string }[]
  >([]);

  const handleSendMessage = (message: string) => {
    setMessages([...messages, { sender: 'user', content: message }]);
    // Add logic to send to backend
  };

  const handleAudioSend = (audio: Blob) => {
    // Add logic to send audio to backend
    console.log(audio);
  };

  return (
    <>
      <CssBaseline />
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
          padding: '16px',
          backgroundColor: '#ffffff',
        }}
      >
        <Typography variant="h4" gutterBottom>
          Chatbot
        </Typography>
        <ChatWindow messages={messages} />
        <MessageInput
          onSend={handleSendMessage}
          onAudioSend={handleAudioSend}
        />
      </Box>
    </>
  );
};

export default App;
