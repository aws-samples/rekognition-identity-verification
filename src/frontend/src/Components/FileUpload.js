import React, { useRef, useState } from "react";
import styled from "styled-components";
import IconButton from '@mui/material/IconButton';
import FileUploadIcon from '@mui/icons-material/FileUpload';

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
    const handleUploadBtnClick = () => {
        fileInputField.current.click();
    };

    const callUpdateFilesCb = (file) => {
        const reader = new FileReader();
        reader.onloadend = function () {
            updateFilesCb(reader.result);
        }
        reader.readAsDataURL(file);

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
            <FileUploadContainer>
                <DragDropText>Drag and drop your ID card</DragDropText>
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