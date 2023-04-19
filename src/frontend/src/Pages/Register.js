import React, { useState } from 'react'
import { API } from "aws-amplify";
import Liveness from '../Components/Liveness'
import Form from "@awsui/components-react/form";
import SpaceBetween from "@awsui/components-react/space-between";
import ErrorMessage from '../Error'
import { TextField } from '@aws-amplify/ui-react';
import { ImUser, ImCalendar, ImUserTie } from "react-icons/im";
import { Navigate } from "react-router-dom";
import { useNavigate } from "react-router-dom"
import {
    Card,
    View,
    Heading,
    Flex,
    Text,
    FieldGroupIcon,
    useTheme,
    Button,
    Alert,
    SliderField
} from '@aws-amplify/ui-react';
import { JSONTree } from 'react-json-tree';

//User SignIn page
const Register = () => {
    const { tokens } = useTheme();
    const [jsonResponse, setJsonResponse] = useState(null)
    const [id, setId] = useState(null)
    const [firstName, setFirstName] = useState(null)
    const [lastName, setLastName] = useState(null)
    const [dob, setDOB] = useState(null)
    const [livenessStart, setLivenessStart] = useState(false)
    const [livenessImageData, setLivenessImageData] = useState(null)
    const [step1, setStep1] = useState(true)
    const [error, setError] = useState({ 'idError': false, 'firstNameError': false, 'lastNameError': false, 'dobError': false })
    const [loading, setLoading] = useState(false)
    const [formSubmit, setFormSubmit] = useState(true)
    const [referenceImage, setreferenceImage] = useState(null)
    const [sliderValue, setSliderValue] = useState(1);
    const [hasformError, setHasFormError] = React.useState('');
    const [registerSuccess, setregisterSuccess] = useState();
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

    function errorCheck() {
        var isError = false;
        if (id === '' || id === null) {
            setError(error => ({ ...error, idError: true }))
            isError = true
        }
        if (firstName === '' || firstName === null) {
            setError(error => ({ ...error, firstNameError: true }))
            isError = true
        }
        if (lastName === '' || lastName === null) {
            setError(error => ({ ...error, lastNameError: true }))
            isError = true
        } if (dob === '' || dob === null) {
            setError(error => ({ ...error, dobError: true }))
            isError = true
        }
        return isError;

    }


    const handleNextSubmit = () => {
        setError({ 'idError': false, 'firstNameError': false, 'lastNameError': false, 'dobError': false })
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
                    setLivenessStart(true)
                    setStep1(false)
                    setSliderValue(2)
                } else {
                    setHasFormError(ErrorMessage['UserAlreadyExists'])
                    setError(error => ({ ...error, idError: true }))
                }
            })
                .catch(error => {
                    console.log(error);
                    setHasFormError(ErrorMessage['GenericError'])
                });



        }
    }
    const handlePreviousSubmit = () => {
        setLivenessStart(false)
        setStep1(true)
        setSliderValue(1)

    }
    const handleReCheck = () => {
        setLivenessStart(false)
        setLivenessImageData(null)
        setFormSubmit(true)
        setLivenessStart(true)

    }
    const handleFormSubmit = () => {
        setSliderValue(3)
        setHasFormError('')
        setLoading(true)
        console.log(referenceImage)
        console.log(referenceImage.S3Object.Bucket)
        console.log(referenceImage.S3Object.Name)
        const requestData = {
            body: { "Properties": { firstName, lastName, dob, id }, "UserId": id, "Bucket": referenceImage.S3Object.Bucket, "Name": referenceImage.S3Object.Name }, // replace this with attributes you need
            headers: { "Content-Type": "application/json" }, // OPTIONAL
        };
        API.post("identityverification", "register", requestData).then(response => {
            let responseData = response;
            console.log(response)
            setJsonResponse(responseData)
            if (responseData.status === "SUCCEEDED") {
                console.log(responseData)
                let responseSuccessData = JSON.parse(responseData.output)
                console.log(responseSuccessData)
                localStorage.removeItem("userSelectedConfidence")
                setregisterSuccess({ "label": "Welcome " + responseSuccessData.UserId + ". Login Successful", "responseData": responseData })
            } else if (responseData.error === 'UserAlreadyExists') {
                setHasFormError(ErrorMessage['UserAlreadyExists'])
            } else {
                setHasFormError(ErrorMessage['GenericError'])
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
                    max={3}
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

                        {livenessStart ? (
                            <>
                                <Button variation="primary" onClick={handlePreviousSubmit}>Previous</Button>
                                {loading ? (
                                    <Button isLoading={true} loadingText="Submitting..." variation="primary">
                                    </Button>
                                ) : (<>
                                    {livenessImageData &&
                                        <Button variation="primary" type="submit" onClick={handleReCheck}>Re-Check</Button>}
                                    <Button variation="primary" type="submit" isDisabled={formSubmit} onClick={handleFormSubmit}>Submit</Button></>)}
                            </>
                        ) : (
                            <>
                                <Button variation="primary" onClick={() => navigate(`/`)}>Cancel</Button>
                                <Button variation="primary" type="submit" onClick={handleNextSubmit}>Next</Button>
                            </>

                        )}
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
                                        onChange={e => { setId(e.target.value); setError(error => ({ ...error, idError: false })) }}
                                        label={
                                            <Text>
                                                Username
                                                <Text as="span" fontSize="0.8rem" color="red">
                                                    {' '}
                                                    (required)
                                                </Text>
                                            </Text>
                                        }
                                        marginBottom={tokens.space.large}
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
                                    <TextField
                                        onChange={e => { setFirstName(e.target.value); setError(error => ({ ...error, firstNameError: false })) }}
                                        label={
                                            <Text>
                                                First name
                                                <Text as="span" fontSize="0.8rem" color="red">
                                                    {' '}
                                                    (required)
                                                </Text>
                                            </Text>
                                        }
                                        marginBottom={tokens.space.large}
                                        size="large"
                                        color="black"
                                        value={firstName}
                                        hasError={error.firstNameError}
                                        errorMessage="Please enter first name"
                                        innerStartComponent={
                                            <FieldGroupIcon ariaLabel="">
                                                <ImUserTie />
                                            </FieldGroupIcon>
                                        }


                                    />
                                    <TextField
                                        onChange={e => { setLastName(e.target.value); setError(error => ({ ...error, lastNameError: false })) }}
                                        label={
                                            <Text>
                                                Last name
                                                <Text as="span" fontSize="0.8rem" color="red">
                                                    {' '}
                                                    (required)
                                                </Text>
                                            </Text>
                                        }
                                        marginBottom={tokens.space.large}
                                        size="large"
                                        color="black"
                                        value={lastName}
                                        hasError={error.lastNameError}
                                        errorMessage="Please enter last name"
                                        innerStartComponent={
                                            <FieldGroupIcon ariaLabel="">
                                                <ImUserTie />
                                            </FieldGroupIcon>
                                        }


                                    />
                                    <TextField
                                        onChange={e => { setDOB(e.target.value); setError(error => ({ ...error, dobError: false })) }}
                                        label={
                                            <Text>
                                                Date of birth
                                                <Text as="span" fontSize="0.8rem" color="red">
                                                    {' '}
                                                    (required)
                                                </Text>
                                            </Text>
                                        }
                                        type="date"
                                        size="large"
                                        color="black"
                                        value={dob}
                                        hasError={error.dobError}
                                        errorMessage="Please enter date of birth (yyyy-mm-dd)"
                                        innerStartComponent={
                                            <FieldGroupIcon ariaLabel="">
                                                <ImCalendar />
                                            </FieldGroupIcon>
                                        }


                                    />
                                </View></Flex></Card>
                    </>

                }

                {livenessStart &&

                    <Liveness referenceImage={getReferenceImage} livenessImageData={livenessImageData}></Liveness>


                }
                {registerSuccess && < Navigate to='/success' state={registerSuccess}>
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
                        valueRenderer={(raw) => raw.length > 200 ? (<span style={{ whiteSpace: 'nowrap', display: 'inline-block', maxWidth: '100%', overflow: 'hidden', textOverflow: 'ellipsis', verticalAlign: 'middle' }} >{raw}</span>) : raw} />
                </>
            }

        </>
    );
}
export default Register;