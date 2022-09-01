import React, { useRef, useState } from "react";
import styled from "styled-components";
import IconButton from '@mui/material/IconButton';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import Typography from '@mui/material/Typography';

export const FileUploadContainer = styled.section`
  position: relative;
  margin: 25px 0 15px;
  border: 2px dotted lightgray;
  padding: 35px 20px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: white;
`;

export const FormField = styled.input`
  font-size: 18px;
  display: block;
  width: 100%;
  border: none;
  text-transform: none;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;

  &:focus {
    outline: none;
  }
`;

export const DragDropText = styled.p`
  font-weight: bold;
  letter-spacing: 2.2px;
  margin-top: 0;
  text-align: center;
`;

const DEFAULT_MAX_FILE_SIZE_IN_BYTES = 500000;

const FileUpload = ({
    label,
    updateFilesCb,
    maxFileSizeInBytes = DEFAULT_MAX_FILE_SIZE_IN_BYTES,
    ...otherProps
}) => {
    const fileInputField = useRef(null);
    const [files, setFiles] = useState();
    const [error, setError] = useState();
    const handleUploadBtnClick = () => {
        fileInputField.current.click();
    };

    const callUpdateFilesCb = (file) => {
        setError(null)
        if(file.size > 150000) {
            setError(" Error! Please upload image size of less than 150 kb.")
        }else {
        const reader = new FileReader();
        reader.onloadend = function () {
            updateFilesCb(reader.result);
        }
        reader.readAsDataURL(file);
    }

    };

    const handleNewFileUpload = (e) => {
        if (e.target.files[0]) {
            const files = e.target.files[0]
            setFiles(files);
            callUpdateFilesCb(files);
        }
    };

    return (
        <>
          {error && (
          <Typography color="red" variant="subtitle2" gutterBottom component="div">
            {error}
          </Typography>
        )}
            <FileUploadContainer>
                <DragDropText>Drag and drop your ID card
                <Typography variant="caption" display="block" gutterBottom>
                Please upload image size of less than 150 kb
      </Typography>
                    <p></p>
                </DragDropText>
                <IconButton onClick={handleUploadBtnClick}>
                    <FileUploadIcon sx={{ fontSize: 80 }} />
                </IconButton>
                <FormField
                    type="file"
                    ref={fileInputField}
                    onChange={handleNewFileUpload}
                    title=""
                    value=""
                    {...otherProps}
                />
            </FileUploadContainer>
        </>
    );
};

export default FileUpload;