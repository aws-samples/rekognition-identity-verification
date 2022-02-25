import React, { useState, useEffect } from 'react'
import Typography from '@mui/material/Typography';
import { styled } from "@mui/material/styles";
import WebCam from '../Components/WebCam';
import Paper from '@mui/material/Paper';
import Container from '@mui/material/Container';
import { API } from "aws-amplify";
import TextField from '@mui/material/TextField';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import {
    Navigate
} from "react-router-dom";
import StyledButton from '../Components/ButtonTheme';
import Title from '../Components/PageTitle'

const Item = styled(Paper)(({ theme }) => ({
    ...theme.typography.body2,
    padding: theme.spacing(1),
    textAlign: 'center',
    color: theme.palette.text.secondary,
}));
//User SignIn page
const SignIn = () => {
    const [error, setError] = useState()
    const [id, setId] = useState(null)
    const [progress, setprogress] = useState(null)
    const [imgSrc, setImgSrc] = useState(null);
    const [registerSuccess, setregisterSuccess] = useState()
    const handleChange = (event) => {
        setError(null)
        setId(event.target.value)

    }
    useEffect(() => {
        setError(null)
        if (imgSrc) {
            if (id == null) {
                setError("Please enter user id");
            } else {
                setprogress(true)
                var base64Image = imgSrc.replace(/^data:image\/[a-z]+;base64,/, "");
                const requestData = {
                    body: { "UserId": id, "Image": base64Image }, // replace this with attributes you need
                    headers: { "Content-Type": "application/json" }, // OPTIONAL
                };
                API.post("identityverification", "auth", requestData).then(response => {
                    let responseData = response;
                    if (responseData.status === "SUCCEEDED") {
                        let responseSuccessData = JSON.parse(responseData.output)
                        console.log(responseSuccessData)
                        setregisterSuccess({ "label": "Welcome " + responseSuccessData.UserId + ". Login Successful" })
                    } else {
                        setError("Login failed. Incorrect user-id")
                    }
                    setprogress(false)
                })
                    .catch(error => {
                        console.log(error.response);
                    });
            }

        }
    }, [imgSrc])

    const makeAuthCall = () => {
        console.log(imgSrc)
    }

    const capture = (idcard) => {
        setImgSrc(idcard);
        makeAuthCall()

    }

    return (
        <>
            <Container maxWidth="sm">
                <Grid
                    container
                    direction="column"
                    justifyContent="center"
                    alignItems="center"
                >
                    <Title pagetitle="Sign in to your account" error={error} />
                    <Item elevation={0}>
                        <TextField id="id" label="User Id" variant="outlined" onChange={handleChange} />
                    </Item>
                    <Item elevation={0}>
                        <WebCam UpdateWebCamImage={capture} label="LOGIN"></WebCam>
                        {progress &&
                            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: "-50px" }}>
                                <CircularProgress size={20} color="inherit" style={{ color: 'white' }} />
                            </Box>
                        }
                    </Item>
                </Grid>
            </Container>
            {registerSuccess && < Navigate
                to='/success'
                state={registerSuccess
                }
            >
            </Navigate >}
            <Item>
                <Typography variant="body1" gutterBottom >
                    Click below to register for an account
                </Typography>
                <StyledButton href="/register" variant="contained">
                    REGISTER
                </StyledButton>
            </Item>

        </>
    );
}
export default SignIn;