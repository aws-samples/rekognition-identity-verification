import React, { useState } from 'react'
import { API } from "aws-amplify";
import Liveness from '../Components/Liveness'
import Form from "@awsui/components-react/form";
import SpaceBetween from "@awsui/components-react/space-between";
import { TextField } from '@aws-amplify/ui-react';
import { ImUser } from "react-icons/im";
import { Table, TableCell, TableRow } from '@aws-amplify/ui-react';
import { useNavigate } from "react-router-dom"
import ErrorMessage from '../Error'
import { Navigate } from "react-router-dom";
import {
    // Image,
    Heading,
    FieldGroupIcon,
    useTheme,
    Button,
    Alert,
    SliderField,
    Flex,
    View,
    Card,
    Text,
    Image as PreviewIDCard


} from '@aws-amplify/ui-react';
import { JSONTree } from 'react-json-tree';




//User SignIn page
const RegisterWithIdCard = () => {
    const { tokens } = useTheme();
    // const canvasRef = useRef(null)
    const [id, setId] = useState(null)
    const [image, setImage] = useState({ 'imageName': '', 'imageFile': '', 'base64Image': '', width: '', height: '', refImage: '' })
    const [preview, setPreview] = useState()
    const [properties, setProperties] = useState({})
    const [livenessImageData, setLivenessImageData] = useState(null)
    const [livenessStart, setLivenessStart] = useState(false)
    const [step1, setStep1] = useState(true)
    const [step2, setStep2] = useState(false)
    const [error, setError] = useState({ 'idError': false })
    const [loading, setLoading] = useState(false)
    const [formSubmit, setFormSubmit] = useState(true)
    const [referenceImage, setreferenceImage] = useState(null)
    const [hasformError, setHasFormError] = React.useState('');
    const [sliderValue, setSliderValue] = useState(1);
    const [registerSuccess, setregisterSuccess] = useState();
    const [jsonResponse, setJsonResponse] = useState(null)
    const navigate = useNavigate()


    const getReferenceImage = (image) => {
        setHasFormError('')
        if (!errorCheck() && image !== null && image.ReferenceImage) {
            setreferenceImage(image.ReferenceImage)
            setLivenessImageData(image)
            setJsonResponse(image)
            if (image.Confidence >= image.userSelectedConfidence) {
                setFormSubmit(false)
            } else if (image.error) {
                setHasFormError(ErrorMessage['GenericError'])
            }
        }
    }

    // const drawRectangleIDCard = (idImage) => {
    //     var imageWidth = image.width;
    //     var imageHeight = image.height;
    //     var left = imageWidth * idImage.DetectFace.FaceDetails[0].BoundingBox.Left
    //     var top = imageHeight * idImage.DetectFace.FaceDetails[0].BoundingBox.Top
    //     var width = imageWidth * idImage.DetectFace.FaceDetails[0].BoundingBox.Width
    //     var height = imageHeight * idImage.DetectFace.FaceDetails[0].BoundingBox.Height
   
    //     const context = canvasRef.current.getContext("2d");
    //     context.strokeStyle = "#75FF33";
    //     context.lineWidth = 1;
    //     context.strokeRect(left, top, width, height)
    // };

    function errorCheck() {
        var isError = false;
        if (id === '' || id === null) {
            setError(error => ({ ...error, idError: true }))
            isError = true
        }
        return isError;

    }

    const handleDocumentUpload = (event) => {
        const reader = new FileReader();
        reader.onloadend = function () {
            var filedata = reader.result;
            var base64ImageId = filedata.replace(/^data:image\/[a-z]+;base64,/, "");
            const image = new Image();
            image.src = window.URL.createObjectURL(event.target.files[0]);
            image.onload = function () {
                var height = this.height;
                var width = this.width;
                // var canvas = document.getElementById('refImage');
                // canvas.width = width
                // canvas.height = height
              
                setImage({
                    imageFile: event.target.files[0],
                    imageName: event.target.files[0].name,
                    base64Image: base64ImageId,
                    width: width,
                    height: height

                })
            }


            setProperties({})

        }

        reader.readAsDataURL(event.target.files[0]);


        if (event.target.files[0].name === '') {
            setPreview(undefined)

        }
        const objectUrl = URL.createObjectURL(event.target.files[0])
        setPreview(objectUrl)

    }

    const handleNextSubmit = () => {
        setError({ 'idError': false })
        if (!errorCheck()) {
            setHasFormError('')
            const requestData = {
                body: { "UserId": id }, // replace this with attributes you need
                headers: { "Content-Type": "application/json" }, // OPTIONAL
            };
            API.post("identityverification", "check-userid", requestData).then(response => {
                let responseData = response;
                console.log(responseData)
                setJsonResponse(responseData)
                if (responseData.Reason === "User not Exist") {
                    setStep2(true)
                    setStep1(false)
                    setSliderValue(2)
                } else {
                    setHasFormError(ErrorMessage['UserAlreadyExists'])
                    setError(error => ({ ...error, idError: true }))
                }
            })
                .catch(error => {
                    console.log(error.response);
                    setHasFormError(ErrorMessage['GenericError'])
                });



        }
    }
    const handlePreviousSubmit = () => {
        setLivenessStart(false)
        setStep2(true)
        setSliderValue(2)
     // drawRectangleIDCard(properties)
    }

    const handleNextStep2Submit = () => {
        setLivenessStart(true)
        setStep2(false)
        setSliderValue(3)
    }

    const handleReCheck = () => {
        setLivenessStart(false)
        setLivenessImageData(null)
        setFormSubmit(true)
        setLivenessStart(true)

    }



    const handleConfirmToFetchImageData = () => {
        setHasFormError('')
        setLoading(true)
        const requestData = {
            body: { "UserId": id, "IdCard": image.base64Image, "ImageName": image.imageName }, // replace this with attributes you need
            headers: { "Content-Type": "application/json" }, // OPTIONAL
        };
        API.post("identityverification", "extract-idcard", requestData).then(response => {
            let responseData = response;
            setJsonResponse(responseData)
            setLoading(false)
            if (JSON.stringify(responseData.Properties) !== "{}") {
                setProperties(responseData)
                //drawRectangleIDCard(responseData)
            } else {
                setHasFormError("We are unable to validate your document at this time. Please try again later.")
            }
        })
            .catch(error => {
                console.log(error);
                setLoading(false)
                setHasFormError("We are unable to validate your document at this time. Please try again later.")
            });
    }

    const handlePreviousStep1Submit = () => {
        setStep1(true)
        setStep2(false)
        setLivenessStart(false)
        setSliderValue(1)
    }

    const handleFormSubmit = () => {
        setSliderValue(4)
        setHasFormError('')
        setLoading(true)
        console.log(referenceImage)
        console.log(referenceImage.S3Object.Bucket)
        console.log(referenceImage.S3Object.Name)
        const requestData = {
            body: { "Properties": properties, "UserId": id, "IdCardName": id + '/' + image.imageName, "Bucket": referenceImage.S3Object.Bucket, "Name": referenceImage.S3Object.Name }, // replace this with attributes you need
            headers: { "Content-Type": "application/json" }, // OPTIONAL
        };
        API.post("identityverification", "register-idcard", requestData).then(response => {
            let responseData = response
            setJsonResponse(responseData)
            if (responseData.status === "SUCCEEDED") {
                let responseSuccessData = JSON.parse(responseData.output)
                localStorage.removeItem("userSelectedConfidence")
                setregisterSuccess({ "userName": responseSuccessData.UserId, "imageId": responseSuccessData.ImageId, "label": "       Successfully Registered User", "properties": responseSuccessData.Properties, "responseData": responseData })

            } else {
                console.log(responseData.error)
                if (responseData.error === 'FaceNotMatchWithIDCard') {
                    console.log(responseData.error)
                    setHasFormError(ErrorMessage['FaceNotMatchWithIDCard'])
                } else if (responseData.error === 'UserAlreadyExists') {
                    setHasFormError(ErrorMessage['UserAlreadyExists'])
                } else {
                    setHasFormError(ErrorMessage['GenericError'])
                }
            }
            setLoading(false)
            //  setprogress(false)
        })
            .catch(error => {
                console.log(error);
                setLoading(false)
                setHasFormError(ErrorMessage['GenericError'])
            });


    }




    return (
        <>
            <View>
                <Heading
                    level={1}
                    color="black"
                    marginTop={tokens.space.large}
                    marginBottom={tokens.space.large}
                >
                    Onboarding user using Identity verification.
                </Heading>

                <SliderField
                    label="Slider"
                    min={1}
                    max={4}
                    step={sliderValue}
                    value={sliderValue}
                    size="large"
                    isDisabled
                    isValueHidden
                    labelHidden
                    filledTrackColor='#ec7211'
                    marginBottom={tokens.space.large}
                />


                {hasformError !== '' &&
                    <>
                        <Alert
                            variation="error"
                            isDismissible={true}
                            hasIcon={true}
                            heading=""
                        >
                            {hasformError}
                        </Alert>
                    </>
                }

            </View>
            <Form
                direction={{ base: 'column', large: 'row' }}
                actions={
                    <SpaceBetween direction="horizontal" size="xs">

                        {livenessStart &&
                            <>
                                <Button variation="primary" onClick={handlePreviousSubmit}>Previous</Button>
                                {loading ? (
                                    <Button isLoading={true} loadingText="Submitting..." variation="primary">
                                    </Button>
                                ) : (
                                    <>
                                        {livenessImageData &&
                                            <Button variation="primary" type="submit" onClick={handleReCheck}>Re-Check</Button>}
                                        <Button variation="primary" type="submit" isDisabled={formSubmit} onClick={handleFormSubmit}>Submit</Button>

                                    </>)}
                            </>
                        }
                        {step1 &&
                            <>
                                <Button variation="primary" onClick={() => navigate(`/`)}>Cancel</Button>
                                <Button variation="primary" type="submit" onClick={handleNextSubmit}>Next</Button>
                            </>
                        }
                        {step2 &&
                            <>
                                <Button variation="primary" onClick={handlePreviousStep1Submit}>Previous</Button>
                                {preview &&
                                    <>
                                        {loading ? (
                                            <Button isLoading={true} loadingText="Fetching Data ..." variation="primary">
                                            </Button>
                                        ) : (
                                            <>
                                                {JSON.stringify(properties) === "{}" ? (
                                                    <Button variation="primary" type="submit" onClick={handleConfirmToFetchImageData}>Confirm</Button>
                                                ) : (<Button variation="primary" type="submit" onClick={handleNextStep2Submit}>Next</Button>
                                                )}
                                            </>

                                        )}


                                    </>
                                }
                            </>
                        }

                    </SpaceBetween>
                }
            >
                {step1 &&
                    <>
                        <Card>
                            <Flex alignItems="center"
                                alignContent="center"
                                direction="column"
                                justifyContent="center"
                            >
                                <View
                                    maxWidth="100%"
                                    padding="1rem"
                                    width="50rem"
                                    as="div"
                                >
                                    <TextField
                                        label={
                                            <Text>
                                                Username
                                                <Text as="span" fontSize="0.8rem" color="red">
                                                    {' '}
                                                    (required)
                                                </Text>
                                            </Text>
                                        }
                                        onChange={e => { setId(e.target.value); setError(error => ({ ...error, idError: false })) }}
                                        size="large"
                                        color="black"
                                        hasError={error.idError}
                                        errorMessage="Please enter username"
                                        value={id}
                                        innerStartComponent={
                                            <FieldGroupIcon ariaLabel="" >
                                                <ImUser />
                                            </FieldGroupIcon>
                                        }


                                    />
                                </View></Flex></Card>
                    </>
                }

                {step2 &&
                    <>

                        <Card>
                            <Flex alignItems="center"
                                alignContent="center"
                                justifyContent="center"
                                direction={{ base: 'column', large: 'row' }}
                            >
                                <View
                                    // maxWidth="100%"
                                    padding="1rem"
                                    // width="50rem"
                                    as="p"
                                >
                                    <Button variation="primary">
                                        <input
                                            type="file"
                                            capture
                                            onChange={handleDocumentUpload}

                                        />
                                    </Button>
                                </View></Flex>
                            <Flex alignItems="center"
                                alignContent="center"
                                justifyContent="center"
                                direction={{ base: 'column', large: 'row' }}
                            >
                                <View
                                    // maxWidth="100%"
                                    padding="1rem"
                                    // width="50rem"
                                    as="p"
                                >

                                    {/* {preview &&
                                        <Alert
                                            variation="info"
                                            isDismissible={false}
                                            hasIcon={false}
                                            heading={image.imageName}
                                        >

                                        </Alert>
                                    } */}
                                    <View >
                                        <Flex  alignItems="center"
                                            alignContent="center"
                                            justifyContent="center" direction={{ base: 'column', large: 'row' }}>
                                            <Flex
                                                direction="column"
                                                alignItems="center"
                                                alignContent="center"
                                                justifyContent="center"
                                                gap={tokens.space.xs}
                                            >


                                                {JSON.stringify(properties) !== "{}" &&
                                                    <>
                                                        <Table variation="striped" color="black">
                                                            {
                                                                Object.keys(properties.Properties).map((key, i) => (
                                                                    <>
                                                                        {properties.Properties[key] !== '' &&
                                                                            <TableRow>
                                                                                <TableCell color="black">{key} </TableCell>
                                                                                <TableCell color="black">{properties.Properties[key]}</TableCell>
                                                                            </TableRow>
                                                                        }
                                                                    </>
                                                                ))
                                                            }
                                                        </Table>
                                                    </>
                                                }

                                            </Flex>
                                            {preview &&
                                                <>

                                                    {/* <canvas
                                                        id="refImage"
                                                        ref={canvasRef}
                                                        width= '100%'
                                                        height= 'auto'
                                                        max-width='100%'
                                                        style={{
                                                            //   width: "400px",
                                                            //   height: "400px",

                                                            alignItems: "center", alignContent: "center",
                                                            backgroundImage: 'url("' + preview + '")',
                                                            // backgroundSize: 'cover',
                                                            backgroundRepeat: 'no-repeat',
                                                            backgroundPosition: 'center',
                                                            // height: image.height,
                                                            // width: image.width,
                                                            width: '100%',
                                                            height: 'auto',
                                                            // maxWidth:"400px",
                                                            overflow: 'hidden',
                                                            display: "block",
                                                            // position: 'relative'
                                                        }}
                                                    /> */}

                                                    <PreviewIDCard
                                                        alt="Trusted Source Document"
                                                        src={preview}
                                                        width="50%"
                                                        height="50%"
                                                        objectFit="cover"
                                                        objectPosition="50% 50%"
                                                    />



                                                </>
                                            }
                                        </Flex>
                                    </View>


                                </View></Flex></Card>



                    </>


                }

                {livenessStart &&

                    <Liveness referenceImage={getReferenceImage} livenessImageData={livenessImageData}></Liveness>


                }
                {registerSuccess && < Navigate
                    to='/success'
                    state={registerSuccess
                    }
                >
                </Navigate >}

            </Form>

            {jsonResponse &&
                <>
                    <Heading
                        level={5}
                        color="black"
                        marginTop={tokens.space.large}
                        marginBottom={tokens.space.large}
                    >
                        Response:
                    </Heading>
                    <JSONTree data={jsonResponse} 
                    valueRenderer={(raw) => raw.length > 200  ? (<span style={{whiteSpace: 'nowrap',display:'inline-block',maxWidth: '100%',overflow:'hidden',textOverflow: 'ellipsis',verticalAlign:'middle'}} >{raw}</span>) : raw } />
                </>
            }
        </>
    );
}
export default RegisterWithIdCard;