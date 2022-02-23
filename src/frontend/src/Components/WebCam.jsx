import * as React from 'react';
import Webcam from "react-webcam";
import Paper from '@mui/material/Paper';
import StyledButton from './ButtonTheme';

const videoConstraints = {
  width: 1300,
  height: 720,
  facingMode: "user"

};
// Webcam react component to capture the user image.
const WebcamCapture = ({ UpdateWebCamImage, label }) => {
  const webcamRef = React.useRef(null);
  const [imgSrc, setImgSrc] = React.useState(null);
  const callUpdateWebCamImage = (image) => {
    UpdateWebCamImage(image);
  };
  const capture = React.useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImgSrc(imageSrc);
    callUpdateWebCamImage(imageSrc)
  }, [webcamRef, setImgSrc]);

  return (
    <Paper style={{ padding: 8 }}>
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        height={'100%'}
        width={'100%'}
        videoConstraints={videoConstraints}
      />
      <StyledButton onClick={capture} variant="contained">
        {label}
      </StyledButton>
    </Paper>
  );
};

export default WebcamCapture;