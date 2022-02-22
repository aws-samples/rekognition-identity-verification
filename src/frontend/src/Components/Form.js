import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import StyledButton from '../Components/ButtonTheme';
import Stack from "@mui/material/Stack";
import { API } from "aws-amplify";
import Typography from '@mui/material/Typography';
import { Navigate } from "react-router-dom";
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';


const Form = ({ imgSrc }) => {
    
//   const classes = useStyles();
  // create state variables for each input
  const [id, setId] = useState('');
  const [fName, setFirstName] = useState('');
  const [lName, setLastName] = useState('');
  const [age, setAge] = useState('');
  const [error, setError] = useState();
  const [progress, setprogress] = useState(false);
  const [registerSuccess, setregisterSuccess] = useState();
//   console.log(fName, lName, id, age);

  const handleSubmit = e => {
    console.log(e)
    console.log(fName, lName, id, age);
    setError(null)
        if (fName === '' || lName === '' || age === '' || imgSrc === null || id === '')
            setError(" Error! Please fill in all fields; *and* please ensure that you've supplied a selfie image.")
        else {
            setprogress(true)
            var base64Image = imgSrc.replace(/^data:image\/[a-z]+;base64,/, "");
            const requestData = {
                body: { "Properties": {fName, lName, age, id} , "UserId": id, "Image": base64Image }, // replace this with attributes you need
                headers: { "Content-Type": "application/json" }, // OPTIONAL
            };
            API.post("identityverification", "/register", requestData).then(response => {
                let responseData = response;
                if (responseData.status === "SUCCEEDED") {
                    let responseSuccessData = JSON.parse(responseData.output)
                    setregisterSuccess({ "userName": responseSuccessData.UserId, "imageId": responseSuccessData.ImageId, "label": "       Successfully Registered User", "fName": fName, "lName": lName, "age": age})
                } else {
                    setError(responseData.status + " : " + responseData.error)
                }
                setprogress(false)
                
            })
                .catch(error => {
                    console.log(error.response);
                });
     

        }

    e.preventDefault();
    // console.log(fName, lName, id, age);
  };

  return (

    <form onSubmit={handleSubmit}>
    <Stack sx={{ p: 2 } }>
       {error && (
            <Typography color="red" variant="subtitle2" gutterBottom component="div">
                {error}
            </Typography>
        )}
      <TextField
        id="id"
        label="Login"
        variant="filled"
        type="id"
        required
        value={id}
        onChange={e => setId(e.target.value)}
      />
      <TextField
        id="fName"
        label="First Name"
        variant="filled"
        required
        value={fName}
        onChange={e => setFirstName(e.target.value)}
      />
      <TextField
        id="lName"
        label="Last Name"
        variant="filled"
        required
        value={lName}
        onChange={e => setLastName(e.target.value)}
      />
      <TextField
        id="age"
        label="Date of birth (YYYY-MM-DD)"
        variant="filled"
        // type="date"
        required
        value={age}
        onChange={e => setAge(e.target.value)}
      />
      <div>
        <StyledButton variant="contained" href="/login">
          Cancel
        </StyledButton>
        <StyledButton type="submit" variant="contained" color="primary">
          Signup
        </StyledButton>
        {registerSuccess && < Navigate to='/success' state={registerSuccess}>
            </Navigate >}
        {progress &&   
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: "-50px", marginLeft: "95px" }}>
                <CircularProgress size={20} color="inherit" style={{ color: 'white' }} />
            </Box>
        }
      </div>
      </Stack>
    </form>
  );
};

export default Form;