import React, { useState } from 'react';
import { Box, TextField, IconButton, Button } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import MicIcon from '@mui/icons-material/Mic';
import DeleteIcon from '@mui/icons-material/Delete';
import { ReactMediaRecorder } from 'react-media-recorder';

interface MessageInputProps {
  onSend: (message: string) => void;
  onAudioSend: (audio: Blob) => void;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSend, onAudioSend }) => {
  const [message, setMessage] = useState('');
  const [audioBlobUrl, setAudioBlobUrl] = useState<string | null>(null);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);

  const handleSend = () => {
    if (message.trim()) {
      onSend(message);
      setMessage('');
    }
  };

  const handleAudioSave = () => {
    if (audioBlob) {
      onAudioSend(audioBlob);
      setAudioBlob(null);
      setAudioBlobUrl(null);
    }
  };

  const handleAudioDiscard = () => {
    setAudioBlob(null);
    setAudioBlobUrl(null);
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', padding: '8px' }}>
      <TextField
        fullWidth
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type a message..."
        variant="outlined"
        sx={{ marginRight: '8px' }}
      />
      <ReactMediaRecorder
        audio
        onStop={(blobUrl, blob) => {
          setAudioBlobUrl(blobUrl);
          setAudioBlob(blob);
        }}
        render={({ startRecording, stopRecording }) => (
          <>
            <IconButton
              onMouseDown={startRecording}
              onMouseUp={stopRecording}
              color="primary"
            >
              <MicIcon />
            </IconButton>
          </>
        )}
      />
      {audioBlobUrl && (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            marginLeft: '8px',
          }}
        >
          <audio src={audioBlobUrl} controls style={{ marginRight: '8px' }} />
          <Button
            onClick={handleAudioSave}
            variant="contained"
            color="primary"
            size="small"
            sx={{ marginRight: '4px' }}
          >
            Send
          </Button>
          <IconButton onClick={handleAudioDiscard} color="secondary">
            <DeleteIcon />
          </IconButton>
        </Box>
      )}
      <IconButton onClick={handleSend} color="primary">
        <SendIcon />
      </IconButton>
    </Box>
  );
};

export default MessageInput;
