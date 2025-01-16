import React, { useRef, useState } from 'react';
import { Box, TextField, IconButton, Button, Typography } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import MicIcon from '@mui/icons-material/Mic';
import DeleteIcon from '@mui/icons-material/Delete';
import { ReactMediaRecorder } from 'react-media-recorder';
import { keyframes } from '@emotion/react';
import Tooltip from '@mui/material/Tooltip';


interface MessageInputProps {
  onSend: (message: string) => void;
  onAudioSend: (audio: Blob, audioUrl: string | null) => void;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSend, onAudioSend }) => {
  const [message, setMessage] = useState('');
  const [audioBlobUrl, setAudioBlobUrl] = useState<string>("");
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const audioElementRef = useRef<HTMLAudioElement>(null);
  const [isShowRecorder, setIsShowRecorder] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const maxDuration = 10;
  let timerRef: number | null = null;
  
  const pulse = keyframes`
    0% { transform: scale(1);}
    50% { transform: scale(1.2); }
    100% { transform: scale(1);}
  `;

  const handleSend = () => {
    if (message.trim()) {
      onSend(message);
      setMessage('');
    }
  };

  const handleAudioSave = () => {
    if (audioBlob) {
      onAudioSend(audioBlob, audioBlobUrl);
      resetAudioState();
    }
  };

  const handleAudioDiscard = () => {
    resetAudioState();
  };

  const resetAudioState = () => {
    setAudioBlob(null);
    setAudioBlobUrl('');
    setIsShowRecorder(false);
    const audioElement = audioElementRef.current;
    if (audioElement) {
      audioElement.pause();
      audioElement.currentTime = 0;
      audioElement.setAttribute('src', '');
    }
  };


  const handleStartRecording = (startRecording: () => void, stopRecording: () => void) => {
    setErrorMessage(""); // Clear error message
    startRecording();
    setIsRecording(true);

    timerRef = setTimeout(() => {
      handleStopRecording(stopRecording);
    }, maxDuration * 1000);
  };

  const validateAudioLength = () => {
    const audioElement = audioElementRef.current;
    if (audioElement) {
      audioElement.addEventListener('loadedmetadata', () => {
        if (audioElement.duration < 1) {
          setErrorMessage('Recording is too short. Please record at least 1 second.');
          setAudioBlob(null);
          setAudioBlobUrl('');
          resetAudioState();
        }
      });
    }
  };

  const handleStopRecording = (stopRecording: () => void) => {
    if (timerRef) clearTimeout(timerRef);
    stopRecording();
    setIsRecording(false);
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
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            handleSend();
          }
        }
      }
      />
      {isShowRecorder && (
        <>
        <ReactMediaRecorder
          audio
          onStop={(blobUrl, blob) => {
            setAudioBlobUrl(blobUrl);
            setAudioBlob(blob);
            validateAudioLength();

          }}
          
          render={({ startRecording, stopRecording }) => (
            <div>
              <Tooltip title="Hold mic to record">
                <IconButton
                  onMouseDown={() => handleStartRecording(startRecording, stopRecording)}
                  onMouseUp={() => handleStopRecording(stopRecording)}
                  color="primary"
                >
                  <MicIcon
                  sx={{
                    color: isRecording? 'red' : 'gray',
                    animation: isRecording ? `${pulse} 1s infinite` : 'none',
                  }}
                />
                  {isShowRecorder && <audio src={audioBlobUrl} controls ref={audioElementRef} />}
                </IconButton>
              </Tooltip>
                
            </div>
          )}  
        />
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
        </>)
      }
      {!isShowRecorder && 
        <Tooltip title="Record audio message">
          <IconButton
          sx={{
            backgroundColor:  'gray',
            '&:hover': {
              backgroundColor: 'darkgray',
            },
          }}
          onClick={() =>setIsShowRecorder(true)}
        >
          <MicIcon sx={{ color: 'white' }}/>
        </IconButton>
        </Tooltip>
      }
      <IconButton onClick={handleSend} color="primary">
        <SendIcon />
      </IconButton>
      {errorMessage && (
        <Typography color="error" sx={{ marginLeft: '16px' }}>
          {errorMessage}
        </Typography>
      )}
    </Box>
  );
};

export default MessageInput;
