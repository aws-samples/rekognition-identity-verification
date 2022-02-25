import React, { useState } from 'react'
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
    fName: "Amit",
    lName: "Gupta",
    id: "",
    age: "1970-01-01",
};
//User profile page
export default function Profile() {
    const [properties, setProperties] = useState(initialUserState)
    const [error, setError] = useState()
    const [registerSuccess, setregisterSuccess] = useState()
    const [progress, setprogress] = useState(false)
    const [imgSrc, setImgSrc] = React.useState(null);
    const [idCard, setidCard] = useState(null);
    const [cardState, setCardSubmit] = useState(false);

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

    const cardSubmit = () => {

        setCardSubmit(true);
    }

    const handleSubmit = (event) => {
        setError(null)
        if (properties.fName === '' || properties.lName === '' || imgSrc === null || properties.age === '' || properties.id === '' || idCard === null) {
            setError(" Error! Please provide the User Id")
        } else {
            setprogress(true)
            var base64Image = imgSrc.replace(/^data:image\/[a-z]+;base64,/, "");
            var base64ImageId = idCard.replace(/^data:image\/[a-z]+;base64,/, "");
            const requestData = {
                body: { "Properties": properties, "UserId": properties.id, "Image": base64Image, "IdCard": base64ImageId }, // replace this with attributes you need
                headers: { "Content-Type": "application/json" }, // OPTIONAL
            };
            API.post("identityverification", "register-idcard", requestData).then(response => {
                let responseData = response
                if (responseData.status === "SUCCEEDED") {
                    let responseSuccessData = JSON.parse(responseData.output)
                    setregisterSuccess({ "userName": responseSuccessData.UserId, "imageId": responseSuccessData.ImageId, "label": "       Successfully Registered User", "fName": properties.fName, "lName": properties.lName, "age": properties.age })

                } else {
                    console.log(responseData.error)
                    setError(responseData.status + " : Identification information doesn't match")
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
        console.log(properties)
    };

    return (
        <>
            <Title pagetitle="Register new user with ID card" />
            {cardState ?
                <Grid container spacing={2}
                    direction="row"
                    justifyContent="center"
                    alignItems="stretch"
                >
                    {imgSrc ?
                        <>
                            <Grid item xs={5} md={5}>
                                <Item elevation={0}>
                                    <img width="100%" height="100%"
                                        src={imgSrc}
                                    />
                                    <StyledButton onClick={recapture} variant="contained" >
                                        RECAPTURE
                                    </StyledButton>
                                </Item>
                            </Grid>
                            <Grid container justifyContent="center" alignItems="center">
                                <Grid item xs={4} alignItems="stretch" justifyContent="center">
                                    <Item>
                                        <Stack
                                            sx={{
                                                display: "flex",
                                                flexDirection: "column",
                                                alignItems: "center",
                                                // justifyContent: "center",
                                                //  height: "250px",
                                                //  width: "60%",
                                            }}
                                        >
                                            {error && (
                                                <Typography color="red" variant="subtitle2" gutterBottom component="div">
                                                    {error}
                                                </Typography>
                                            )}

                                            <TextField textAlign="center" id="id" label="User Id" variant="standard" onChange={handleChange} />
                                            {/* <TextField id="fName" label="First Name" variant="standard" onChange={handleChange} />
                                <TextField id="lName" label="Last Name" variant="standard" onChange={handleChange} />
                                <TextField id="age" value={properties.age} variant="standard" onChange={handleChange} /> */}
                                            <div  >
                                                <StyledButton variant="contained" onClick={handleSubmit} >
                                                    REGISTER
                                                </StyledButton>
                                                {progress &&
                                                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: "-50px", marginLeft: "95px" }}>
                                                        <CircularProgress size={20} color="inherit" style={{ color: 'white' }} />
                                                    </Box>
                                                }
                                            </div>
                                        </Stack>
                                    </Item>
                                </Grid>
                            </Grid>
                        </>
                        :
                        <Grid item xs={5} md={5}>
                            <Item elevation={0}
                            >
                                <WebCam UpdateWebCamImage={capture} label="CAPTURE PHOTO" ></WebCam>
                            </Item>
                        </Grid>
                    }
                </Grid>
                :
                <Grid container spacing={2}
                    direction="row"
                    justifyContent="center"
                    alignItems="stretch"
                >
                    <Grid item xs={6} md={5}>
                        {idCard ?
                            <Item elevation={0}>
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
                                <StyledButton onClick={cardSubmit} variant="contained">
                                    Submit
                                </StyledButton>
                            </Item>
                            : <Item
                                elevation={0}>
                                <FileUpload
                                    accept=".jpg,.png,.jpeg"
                                    label=""
                                    updateFilesCb={updateUploadedFile}
                                />
                            </Item>
                        }
                    </Grid>
                </Grid>
            }
            {registerSuccess && < Navigate
                to='/success'
                state={registerSuccess
                }
            >
            </Navigate >}
        </>
    );
}