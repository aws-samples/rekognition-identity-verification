import { useState } from 'react';
import ModalDialog from '../Components/PromptSignIn';

const Login = () => {
  // declare a new state variable for modal open
  const [open, setOpen] = useState(true);

  // function to handle modal open
  // const handleOpen = () => {
  //   setOpen(true);
  // };

  // function to handle modal close
  const handleClose = () => {
    setOpen(true);
  };

  return (
      <ModalDialog open={open} handleClose={handleClose} />
  );
};

export default Login;