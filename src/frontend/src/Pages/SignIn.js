import React, { useState } from 'react'
import { API } from "aws-amplify";
import Liveness from '../Components/Liveness'
import Form from "@awsui/components-react/form";

import SpaceBetween from "@awsui/components-react/space-between";

import { TextField } from '@aws-amplify/ui-react';
import { ImUser } from "react-icons/im";
import { Navigate } from "react-router-dom";
import ErrorMessage from '../Error'
import { useNavigate } from "react-router-dom"
import { JSONTree } from 'react-json-tree';
import {
    Card,
    View,
    Heading,
    Flex,
    Text,
    FieldGroupIcon,
    useTheme,
    Button,
    Alert


} from '@aws-amplify/ui-react';

//User SignIn page
const SignIn = () => {
    const { tokens } = useTheme();


    const [id, setId] = useState(null)
    const [livenessStart, setLivenessStart] = useState(false)
    const [livenessImageData, setLivenessImageData] = useState(null)
    const [step1, setStep1] = useState(true)
    const [error, setError] = useState({ 'idError': false })
    const [loading, setLoading] = useState(false)
    const [formSubmit, setFormSubmit] = useState(true)
    const [referenceImage, setreferenceImage] = useState(null)
    const [hasformError, setHasFormError] = React.useState('');
    const [registerSuccess, setregisterSuccess] = useState()
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
            }

        } else if (image.error) {
            setHasFormError(ErrorMessage['GenericError'])
        }
    }

    function errorCheck() {
        var isError = false;
        if (id === '' || id === null) {
            setError(error => ({ ...error, idError: true }))
            isError = true
        }
        return isError;

    }


    const handleNextSubmit = () => {
        setError({ 'idError': false })
        if (!errorCheck()) {
            setHasFormError('')
            const requestData = {
                body: { "UserId": id },
                headers: { "Content-Type": "application/json" },
            };
            API.post("identityverification", "check-userid", requestData).then(response => {
                let responseData = response;
                setJsonResponse(responseData)
                if (responseData.Reason === "User Exist") {
                    setLivenessStart(true)
                    setStep1(false)
                } else {
                    setHasFormError(ErrorMessage['ValueError'])
                    setError(error => ({ ...error, idError: true }))
                }
            })
                .catch(error => {
                    setHasFormError(ErrorMessage['GenericError'])
                });
        }
    }

    const handlePreviousSubmit = () => {
        setLivenessStart(false)
        setStep1(true)

    }
    const handleReCheck = () => {
        setLivenessStart(false)
        setLivenessImageData(null)
        setFormSubmit(true)
        setLivenessStart(true)

    }
    const handleFormSubmit = () => {
        setHasFormError('')
        setLoading(true)
        const requestData = {
            body: { "UserId": id, "Bucket": referenceImage.S3Object.Bucket, "Name": referenceImage.S3Object.Name }, // replace this with attributes you need
            headers: { "Content-Type": "application/json" }, // OPTIONAL
        };
        API.post("identityverification", "auth", requestData).then(response => {
            let responseData = response;
            setJsonResponse(responseData)
            console.log(responseData)
            if (responseData.status === "SUCCEEDED") {
                let responseSuccessData = JSON.parse(responseData.output)
                console.log(responseSuccessData)
                localStorage.removeItem("userSelectedConfidence")
                setregisterSuccess({ "label": responseSuccessData.UserId, "responseData": responseData })

            } else if (responseData.error === 'ValueError') {
                setHasFormError(ErrorMessage['ValueError'])
            }
            else if (responseData.error === 'UserAccessDenied') {
                setHasFormError(ErrorMessage['UserAccessDenied'])
            } else {
                setHasFormError(ErrorMessage['GenericError'])
            }

            //  setprogress(false)
            setLoading(false)
        })
            .catch(error => {
                console.log(error);
                setLoading(false)
                setHasFormError("Error Occur in submitting the form . Please try again")
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
                    User Authentication using Identity verification.
                </Heading>

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
                    <SpaceBetween direction="horizontal" size="s">
                        {livenessStart ? (
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
                                    value={id}
                                    hasError={error.idError}
                                    errorMessage="Please enter username"
                                    innerStartComponent={
                                        <FieldGroupIcon ariaLabel="">
                                            <ImUser />
                                        </FieldGroupIcon>
                                    }


                                />
                            </View></Flex></Card>
                }
                {livenessStart &&

                    <Liveness referenceImage={getReferenceImage} livenessImageData={livenessImageData}></Liveness>


                }

                {registerSuccess && < Navigate
                    to='/loggedin'
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
                        valueRenderer={(raw) => raw.length > 200 ? (<span style={{ whiteSpace: 'nowrap', display: 'inline-block', maxWidth: '100%', overflow: 'hidden', textOverflow: 'ellipsis', verticalAlign: 'middle' }} >{raw}</span>) : raw} />
                </>
            }
        </>
    );
}
export default SignIn;