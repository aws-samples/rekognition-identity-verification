import React, { useState } from 'react'
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import { styled } from "@mui/material/styles";
import WebCam from '../Components/WebCam';
import Container from '@mui/material/Container';
import Form from '../Components/Form';
import Title from '../Components/PageTitle'
import StyledButton from '../Components/ButtonTheme';

const Item = styled(Paper)(({ theme }) => ({
    ...theme.typography.body2,
    textAlign: 'center',
    color: theme.palette.text.secondary,
}));
//New user registration
export default function Register() {
    const [imgSrc, setImgSrc] = useState(null);
    const capture = (image) => {
        localStorage.setItem("pic", image);
        setImgSrc(image);
    }
    const recapture = () => {
        localStorage.removeItem("pic")
        setImgSrc(null);
    }
    return (
        <Container maxWidth="md">
            <Grid container spacing={2} >
                <Title pagetitle="Register" />
                <Grid container justifyContent="center" spacing={4}>
                    <Grid item xs={8}>
                        {imgSrc ?
                            <Item elevation={10}>
                                <img
                                    src={imgSrc}
                                />
                                <StyledButton onClick={recapture} variant="contained">
                                    RECAPTURE
                                </StyledButton>
                            </Item>
                            :
                            <Item elevation={10}
                            >
                                <WebCam UpdateWebCamImage={capture} label="CAPTURE PHOTO"></WebCam>
                            </Item>
                        }
                    </Grid>
                    <Grid item xs={8}>
                        <Item elevation={10}>
                            <Form imgSrc={imgSrc} />
                        </Item>
                    </Grid>
                </Grid>
            </Grid>
        </Container>
    );
}