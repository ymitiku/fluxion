import React, { useRef, useState } from 'react';
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
  const [audioBlobUrl, setAudioBlobUrl] = useState<string>("");
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const audioElementRef = useRef<HTMLAudioElement>(null);
  const [isRecording, setIsRecording] = useState(false);

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
      setAudioBlobUrl("");
    }
  };

  const handleAudioDiscard = () => {
    setAudioBlob(null);
    setAudioBlobUrl("")
    const audioElement = audioElementRef.current;
    if (audioElement) {
      audioElement.pause();
      audioElement.currentTime = 0;
      audioElement.setAttribute('src', '');
    }
    setIsRecording(false);
  };

  const handleStartRecording = (startRecording: () => void) => {
    startRecording();
  };

  const handleStopRecording = (stopRecording: () => void) => {
    stopRecording();
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
      {isRecording && 
        <ReactMediaRecorder
          audio
          onStop={(blobUrl, blob) => {
            setAudioBlobUrl(blobUrl);
            setAudioBlob(blob);

          }}
          
          render={({ startRecording, stopRecording }) => (
            <div>
              <IconButton
                onMouseDown={() => handleStartRecording(startRecording)}
                onMouseUp={() => handleStopRecording(stopRecording)}
                color="primary"
              >
                <MicIcon />
                {isRecording && <audio src={audioBlobUrl} controls ref={audioElementRef} />}
              </IconButton>
              
            </div>
          )}  
        />
      }
      {!isRecording && <MicIcon onClick={() => setIsRecording(true)} />}
      {isRecording && (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            marginLeft: '8px',
          }}
        >
          
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
