import { AmplifyProvider } from '@aws-amplify/ui-react';
import React from "react";
import {
    FaceLivenessDetector

} from '@aws-amplify/ui-react-liveness';
import { API } from "aws-amplify";
import "react-responsive-modal/styles.css";
import { Modal } from "react-responsive-modal";
import {
    Card,
    View,
    Heading,
    Flex,
    useTheme,
    Button,
    Alert,
    SliderField,
    Image
} from '@aws-amplify/ui-react';



function Liveness({ referenceImage, livenessImageData }) {
    // const canvasRef = useRef();
    const { tokens } = useTheme();
    const [sessionId, setSessionID] = React.useState(null);
    const [imageData, setImageData] = React.useState(null);
    const [userSelectedConfidence, setuserSelectedConfidence] = React.useState(80);
    const [open, setOpen] = React.useState(true);

    const closeModal = () => setOpen(false);


    const setReferenceImage = (image) => {
        image.userSelectedConfidence = localStorage.getItem('userSelectedConfidence')
        setImageData(image)
        referenceImage(image);
    };

    const handleStartLiveness = () => {
        const fetchCreateLiveness = async () => {
            API.get("identityverification", "start-liveness-session").then(response => {
                setSessionID(response.body.SessionId);
            })
                .catch(error => {
                    console.log(error.response);
                });
        }
        fetchCreateLiveness()
    };

    const setSliderValue = (value) => {
        localStorage.setItem('userSelectedConfidence', value);
        setuserSelectedConfidence(value)
    };

    const formatValue = (value) => {
        localStorage.setItem('userSelectedConfidence', value);
        return `${value}`;
    };

    const onUserCancel = () => {
        setSessionID(null);
        handleStartLiveness()
    };


    React.useEffect(() => {
        const consentData = localStorage.getItem('userConsent') ? false : true
        setOpen(consentData)
        if (livenessImageData === null) {
            setImageData(null)
            setSessionID(null);
            handleStartLiveness()
        } else if (livenessImageData.ReferenceImageBase64) {
            setImageData(livenessImageData)
            setSessionID(livenessImageData.SessionId);
            setuserSelectedConfidence(livenessImageData.userSelectedConfidence)
            //  drawRectangle(livenessImageData);
        }

    }, [livenessImageData]);

    React.useLayoutEffect(() => {
        setuserSelectedConfidence(userSelectedConfidence)


    }, [userSelectedConfidence]);


    const handleConsent = () => {

        setOpen(false)
        localStorage.setItem('userConsent', true);
    }

    const handleGetLivenessDetection = async (sessionId) => {
        if (sessionId) {
            const requestData = {
                body: { "sessionid": sessionId },
                headers: { "Content-Type": "application/json" },
            };
            const data = await API.post('identityverification', 'liveness-session-result', requestData);
            try {
                const confidence = data.body.Confidence
                data.body.Confidence = confidence
                setuserSelectedConfidence(localStorage.getItem('userSelectedConfidence'))
                setReferenceImage(data.body)
                if (confidence >= userSelectedConfidence) {
                    return { isLive: true };
                } else {
                    return { isLive: false };

                }
            } catch (err) {
                setReferenceImage({ "error": true })
                return { isLive: false };
            }
        }


    };
    return (

        <AmplifyProvider>
            {open ? (
                <View direction={{ base: 'column', large: 'row' }}>

                    <Modal
                        open={open}
                        showCloseIcon={false}
                    >
                        <Alert

                            isDismissible={false}
                            onDismiss={() => closeModal()}
                            hasIcon={true}
                            direction={{ base: 'column', large: 'row' }}
                        >
                            <Heading

                                level={6}
                                marginBottom={tokens.space.small}
                                fontWeight={tokens.fontWeights.light}
                            >
                                This feature uses Amazon Web Services. Amazon Web Services may collect, store, and use biometric identifiers and biometric information ("biometric data") to compare an individual's image with a stored image for analysis, verification, fraud, and security purposes.</Heading>      <Heading

                                    level={6}
                                    marginBottom={tokens.space.large}
                                    fontWeight={tokens.fontWeights.light}
                                >
                                Amazon Web Services’ privacy policy will retain generated biometric information from this process. You provide your express, informed, written release and consent for Amazon Web Services to collect, use, and store your biometric data as described herein.
                            </Heading><Flex
                                direction="row"
                                justifyContent="center"
                                alignItems="center"
                                alignContent="center"
                                wrap="nowrap"
                                gap="1rem"
                            >   <Button variation="primary" onClick={handleConsent} >Ok</Button> </Flex>
                        </Alert>
                    </Modal>

                </View>
            ) : (
                <>
                    {
                        sessionId ? (
                            <>
                                {imageData &&
                                    <>

                                        <Heading level={5} marginTop={tokens.space.large} marginBottom={tokens.space.large}>Selected liveness score threshold: {imageData.userSelectedConfidence}%</Heading>

                                        {imageData.userSelectedConfidence > imageData.Confidence &&
                                            <Alert
                                                variation="error"
                                                isDismissible={true}
                                                hasIcon={true}
                                                heading=""
                                            >
                                                Check unsuccessfull. Try again!
                                            </Alert>

                                        }
                                    </>
                                }
                                <Alert
                                    variation="info"
                                    isDismissible={true}
                                    hasIcon={true}
                                >
                                    <Heading level={6}>Liveness Session ID: {sessionId}
                                        {imageData && (<> and Confidence Score: {imageData.Confidence}% </>)}
                                    </Heading>

                                </Alert>

                                {(imageData && imageData.ReferenceImageBase64) ? (
                                    <>
                                        <Card>
                                            <Flex
                                                direction="row"
                                                justifyContent="center"
                                                alignItems="center"
                                                alignContent="center"
                                                wrap="wrap"
                                                gap="1rem"
                                            >
                                                <Image
                                                    src={"data:image/jpeg;base64," + imageData.ReferenceImageBase64}
                                                    alignItems="center" alignContent="center"
                                                    // objectFit="cover"
                                                    backgroundColor="initial"
                                                    // height="40%"
                                                    // width="40%"
                                                    opacity="100%"

                                                />

                                            </Flex>
                                        </Card>
                                    </>

                                ) : (
                                    <>
                                        <Flex
                                            direction="row"
                                            justifyContent="center"
                                            alignItems="center"
                                            alignContent="center"
                                            wrap="nowrap"
                                            gap="2rem"

                                        >
                                            <SliderField
                                                marginTop={tokens.space.large}
                                                label="Set liveness score:"
                                                defaultValue={userSelectedConfidence}
                                                onChange={setSliderValue}
                                                formatValue={formatValue}

                                            />
                                        </Flex>
                                        <Card>
                                            <Flex
                                                direction="row"
                                                justifyContent="center"
                                                alignItems="center"
                                                alignContent="center"
                                                wrap="nowrap"

                                                gap="1rem"

                                            >

                                                <View
                                                    as="div"
                                                    maxHeight="600px"
                                                    height="600px"
                                                    width="740px"
                                                    maxWidth="740px"
                                                >
                                                    <FaceLivenessDetector
                                                        sessionId={sessionId}
                                                        region={process.env.REACT_APP_REGION ? process.env.REACT_APP_REGION : "us-east-1"}
                                                        onUserCancel={onUserCancel}
                                                        onAnalysisComplete={async () => {
                                                            const response = await handleGetLivenessDetection(sessionId);
                                                        }}

                                                    />
                                                </View>

                                            </Flex>
                                        </Card>
                                    </>
                                )}

                            </>
                        ) : (

                            <Button isLoading={true} loadingText="Loading..." variation="primary">
                            </Button>
                        )
                    }
                </>)}
        </AmplifyProvider >


    );

}

export default Liveness;

