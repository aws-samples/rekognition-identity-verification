import React from 'react';
import Dialog from '@mui/material/Dialog';
import SignIn from '../Pages/SignIn';

const ModalDialog = ({ open, handleClose }) => {
  return (
    <Dialog open={open} onClose={handleClose}>
      <SignIn></SignIn>
    </Dialog>
  );
};

export default ModalDialog;