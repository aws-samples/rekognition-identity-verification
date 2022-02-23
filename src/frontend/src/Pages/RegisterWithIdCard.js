import React, { useState, useEffect } from 'react'
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import Card from '@mui/material/Card';
import Box from '@mui/material/Box';
import CardMedia from '@mui/material/CardMedia';
import { styled } from "@mui/material/styles";
import { API } from "aws-amplify";
import CircularProgress from '@mui/material/CircularProgress';
import Stack from "@mui/material/Stack";
import FileUpload from '../Components/FileUpload';
import WebCam from '../Components/WebCam';
import {
    Navigate
} from "react-router-dom";
import Title from '../Components/PageTitle';
import StyledButton from '../Components/ButtonTheme';

const Item = styled(Paper)(({ theme }) => ({
    ...theme.typography.body2,
    textAlign: 'center',
    color: theme.palette.text.secondary,
}));
const initialUserState = {
    fName: "",
    lName: "",
    id: "",
    age: "",
};

//New user registration with ID card
export default function RegisterWithIdCard() {
    const [properties, setProperties] = useState(initialUserState)
    const [error, setError] = useState()
    const [registerSuccess, setregisterSuccess] = useState()
    const [progress, setprogress] = useState(false)
    const [imgSrc, setImgSrc] = React.useState(null);
    const [idCard, setidCard] = useState(null);
  
    const updateUploadedFile = (file) => {
        setidCard(file)
    }
    const capture = (image) => {
        localStorage.setItem("pic", image);
        setImgSrc(image);
    }
    const recapture = () => {
        localStorage.removeItem("pic")
        setImgSrc(null);
    }
    const update = () => {

        setidCard(null);
    }
    // const cardSubmit = () => {

    //     setCardSubmit(true);
    // }

    useEffect(() => {
        properties.fName = "Happy"
        properties.lName = "Traveler"
        properties.age = "1981-01-01"
    }, [idCard])

    const handleSubmit = (event) => {
        setError(null)
        if (properties.fName === '' || properties.lName === '' || imgSrc === null || properties.age === '' || properties.id === '' || idCard === null) {
            setError(" Error! Please fill in all fields; *and* please ensure that you've supplied a selfie image and id card image.")
        } else {
            setprogress(true)
            var base64Image = imgSrc.replace(/^data:image\/[a-z]+;base64,/, "");
            var base64ImageId = idCard.replace(/^data:image\/[a-z]+;base64,/, "");
            const requestData = {
                body: { "Properties": properties, "UserId": properties.id, "Image": base64Image, "IdCard": base64ImageId }, // replace this with attributes you need
                headers: { "Content-Type": "application/json" }, // OPTIONAL
            };
            console.log(requestData);
            API.post("identityverification", "/register-idcard", requestData).then(response => {
                let responseData = response
                if (responseData.status === "SUCCEEDED") {
                    let responseSuccessData = JSON.parse(responseData.output)
                    setregisterSuccess({ "userName": responseSuccessData.UserId, "imageId": responseSuccessData.ImageId, "label": "       Successfully Registered User", "fName": properties.fName, "lName": properties.lName, "age": properties.age })

                } else {
                    console.log(responseData.error)
                    setError("Faces don't match")
                    //setError(responseData.status + " : Identification information doesn't match")
                }
                setprogress(false)
            })
                .catch(error => {
                    console.log(error.response);
                });


        }
        event.preventDefault();
    };
    const handleChange = (event) => {
        const id = [event.target.id]
        properties[id] = event.target.value
        setProperties(properties)
    };

    return (
        <>
            <Title pagetitle="Register new user with ID card" />
            <Grid container spacing={12}
                // direction="row"
                justifyContent="center"
                alignItems="stretch"

            >
                <Grid item xs={5} md={5}>
                    {imgSrc ?
                        <Item elevation={5}
                            style={{ borderRadius: "8px !important" }}>
                            <img width="100%" height="100%" src={imgSrc} />
                            <StyledButton onClick={recapture} variant="contained" >
                                RECAPTURE
                            </StyledButton>
                        </Item>
                        :
                        <Item elevation={5}>
                            <WebCam UpdateWebCamImage={capture} label="CAPTURE PHOTO" ></WebCam>
                        </Item>
                    }
                </Grid>
                <Grid item xs={5} md={5}>
                    {idCard ?
                        <Item elevation={5}>
                            <Card >
                                <CardMedia
                                    component="img"
                                    image={idCard}
                                    alt="green iguana"
                                />
                            </Card>
                            <StyledButton onClick={update} variant="contained">
                                UPDATE
                            </StyledButton>
                        </Item>
                        : <Item elevation={3}>
                            <FileUpload
                                accept=".jpg,.png,.jpeg"
                                label=""
                                updateFilesCb={updateUploadedFile}
                            />
                        </Item>
                    }
                </Grid>
                <Grid item xs={8}>
                    <Item elevation={5}>
                        <Grid container
                            justifyContent="center"
                            alignItems="stretch">
                            <Grid item xs={7}>
                                <Stack
                                    sx={{
                                        display: "flex",
                                        flexDirection: "column",
                                        // alignItems: "center",
                                        justifyContent: "center",
                                        //  height: "250px",
                                        // width: "60%",
                                    }}
                                >
                                    {error && (
                                        <Typography color="red" variant="subtitle2" gutterBottom component="div">
                                            {error}
                                        </Typography>
                                    )}
                                    <TextField id="id" label="User Id" variant="standard" onChange={handleChange} />
                                    <TextField id="fName" value={properties.fName} label="First Name" variant="standard" onChange={handleChange} />
                                    <TextField id="lName" value={properties.lName} label="Last Name" variant="standard" onChange={handleChange} />
                                    <TextField id="age" value={properties.age} label="Date of birth (YYYY-MM-DD)" variant="standard" onChange={handleChange} />
                                    <Box textAlign='center' >
                                        <StyledButton variant="contained" onClick={handleSubmit} style={{ maxWidth: '30%', maxHeight: '30%', minWidth: '30%', minHeight: '30%' }}>
                                            REGISTER
                                        </StyledButton>
                                        {progress &&
                                            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: "-50px", marginLeft: "95px" }}>
                                                <CircularProgress size={20} color="inherit" style={{ color: 'white' }} />
                                            </Box>
                                        }
                                    </Box>
                                </Stack>
                            </Grid>
                        </Grid>
                    </Item>
                </Grid>
            </Grid>
            {/* </Container> */}
            {registerSuccess && < Navigate
                to='/success'
                state={registerSuccess
                }
            >
            </Navigate >}
        </>
    );
}