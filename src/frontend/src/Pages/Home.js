import {
    Card,
    Image,
    View,
    Heading,
    Flex,
    Text,
    Button,
    useTheme,
    Link,
    ButtonGroup,
    Collection

} from '@aws-amplify/ui-react';
import { useNavigate } from "react-router-dom"
import YouTube from 'react-youtube';
function Home() {

    const { tokens } = useTheme();
    const navigate = useNavigate()

    return (
        <>
            <View direction={{ base: 'column', large: 'row' }}>
                <Heading level={1} color="black">
                    Identity Verification using Amazon Rekognition
                </Heading>
                <Heading level={5} color="black" >
                    Verify user identity online using machine learning.
                </Heading>
                <ButtonGroup marginTop={tokens.space.large}>
                    <Button backgroundColor="#ec7211" color="white">
                        <Link color="white"
                            href="https://github.com/aws-samples/rekognition-identity-verification"
                            isExternal={true}
                        >
                            Deploy Solution Template
                        </Link>
                    </Button>
                    <Button variation="primary" onClick={() => navigate(`/login`)} color="black">

                        Try it Out

                    </Button>
                </ButtonGroup>
            </View>
            <View marginTop={tokens.space.large} direction={{ base: 'column', large: 'row' }}>

                <Card>
                    <Flex alignItems="flex-start"
                        backgroundColor={tokens.colors.background.secondary}
                        marginTop={tokens.space.large}
                        direction={{ base: 'column', large: 'row' }}>
                        <Text
                            as="span"
                            color="black"
                        >
                        In-person user identity verification is slow to scale, costly, and has high friction. Machine learning-powered facial biometrics can enable online user identity verification. Amazon Rekognition offers pre-trained facial recognition and analysis capabilities to quickly add to user onboarding and authentication workflows to verify opted-in users' identities online. No machine learning expertise is required. With Amazon Rekognition, you can onboard and authenticate users in seconds while detecting fraudulent or duplicate accounts. As a result, you can grow users faster, reduce fraud, and lower user verification costs.
                         </Text>

                        <YouTube videoId="VOrSs5Mw_dQ" />
                    </Flex>
                </Card>
            </View>

        
            <Heading
                level={4}
                isTruncated={true}
                color="black"
                marginTop={tokens.space.large}
            >
                How it works
            </Heading>

            <Image
                alt="How Identity Verification using Amazon Rekognition works"
                src="https://d1.awsstatic.com/partner-network/partner_marketing_web_team/product-page-diagram_Amazon-Rekognition-Face-Liveness-2.e3ab161d23fab1fb31025871fb7621c34443cdc6.png"
                objectFit="initial"
                objectPosition="50% 50%"
                backgroundColor="initial"
                opacity="100%"
                marginTop={tokens.space.large}
            />
        </>
    );
}

export default Home;