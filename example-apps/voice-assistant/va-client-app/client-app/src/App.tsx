import React, { useState } from 'react';
import { Box, CssBaseline, Typography, IconButton } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';
import axios from "axios"; // Import Axios for API requests
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';

const App: React.FC = () => {
  const [messages, setMessages] = useState<
    { sender: string; content: string, audioUrl: string | null }[]
  >([]);

  const [darkMode, setDarkMode] = useState(false);

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      ...(darkMode
        ? {
            background: { default: '#121212', paper: '#1e1e1e' }, // Dark gray background
            text: { primary: '#ffffff', secondary: '#bbbbbb' },   // White text
          }
        : {
            background: { default: '#ffffff', paper: '#f5f5f5' }, // Light gray background
            text: { primary: '#000000', secondary: '#333333' },   // Black text
          }),
    },
  });
  

  const toggleDarkMode = () => {
    setDarkMode((prevMode) => !prevMode);
  };
 

  const handleSendMessage = async (message: string) => {
    // Update the UI with the user's message
    setMessages([...messages, { sender: "user", content: message, audioUrl: null }]);
    try {
      // Send the message to the backend
      const response = await axios.post("http://127.0.0.1:5000/send-message", {
          history: messages,
          message: message,
      });

      // Extract and display the response from the backend
      const botResponse = response.data.response;
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "bot", content: botResponse, audioUrl: null },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "bot", content: "An error occurred. Please try again.", audioUrl: null },
      ]);
    }
  };

  const handleAudioSend = async (audio: Blob, audioUrl: string | null) => {
    try {
      // Create FormData to send the audio file and conversation history
      const formData = new FormData();
      formData.append("audio", audio, "audio.webm"); // Append the audio file
      formData.append(
        "history",
        JSON.stringify(
          messages.map((msg) => ({
            sender: msg.sender,
            content: msg.content,
          }))
        )
      );

      // Make POST request to send-audio endpoint
      const response = await axios.post("http://127.0.0.1:5000/send-audio", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      // Extract response and transcribed audio text
      const { response: botResponse, audio_text: transcribedText } = response.data;

      // Update the messages state with the transcription and bot response
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "user", content: transcribedText, audioUrl: audioUrl }, // Add transcribed audio as a user message
        { sender: "bot", content: botResponse, audioUrl: null },     // Add the bot's response
      ]);
    } catch (error) {
      console.error("Error sending audio:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "bot", content: "An error occurred while processing the audio. Please try again.", audioUrl: null },
      ]);
    }
  };


  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
          padding: '16px',
          bgcolor: 'background.default',
          color: 'text.primary',
        }}
      >
        <Typography variant="h4" gutterBottom>
          Fluxion Voice Assistant
        </Typography>    
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
            marginBottom: 2,
          }}
        >
          <IconButton onClick={toggleDarkMode} color="inherit">
            {darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
        </Box>

        <ChatWindow messages={messages} />
        <MessageInput
          onSend={handleSendMessage}
          onAudioSend={handleAudioSend}
        />
      </Box>
    </ThemeProvider>
  );
};

export default App;
