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

    const items = [
        {
            title: 'Grow users faster',
            description:
                'Convert more visitors into customers by decreasing onboarding time and increasing user convenience. With Amazon Rekognition, you can verify users in seconds online anywhere in the world, and scale from hundreds to millions of identity verifications per hour. Users can now access your services online without having to visit in-person.',
        },
        {
            title: 'Reduce fraud',
            description:
                'Strengthen your fraud prevention capabilities by complementing passwords-based authentication with online visual identity verification. Guard against fraudulent account openings or transactions by comparing user’s selfie picture with identity document picture or your collection of existing users’ pictures.',
        },
        {
            title: 'Lower costs and overheads',
            description:
                "Reduce the time and cost of in-person identity verification by using Amazon Rekognition pre-trained and customizable APIs. With Amazon Rekognition, you can onboard and authenticate users online without building and managing your own ML infrastructure.",
        },
    ];

    // const opts = {
    //     height: '330',
    //     width: '480',
    //     playerVars: {
    //         // https://developers.google.com/youtube/player_parameters
    //         //   autoplay: 1,
    //     },
    // };
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

                        Try Out

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
                            In-person user identity verification is slow to scale, costly, and high friction for users. Machine learning powered facial biometrics can enable online user identity verification. Amazon Rekognition offers pre-trained facial recognition and analysis capabilities that you can quickly add to your user onboarding and authentication workflows to verify opted-in users' identity online. No machine learning expertise is required. With Amazon Rekognition, you can onboard and authenticate users in seconds while detecting fraudulent or duplicate accounts. As a result, you can grow users faster, reduce fraud, and lower user verification costs.
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
                Benefits
            </Heading>



            <Collection
                type="list"
                items={items}
                backgroundColor={'none'}
                justifyContent="space-around"
                alignItems="baseline"
                alignContent="space-around"
                wrap="nowrap"
                gap="1rem"
                direction={{ base: 'column', large: 'row' }}
                marginTop={tokens.space.large}
            >
                {(item, index) => (
                    <Card
                        key={index}
                        backgroundColor={'none'}
                    >
                        <Heading
                            level={5}
                            isTruncated={true}
                            color="black"
                            marginBottom={tokens.space.medium}
                        >{item.title}</Heading>
                        <Text variation="primary"
                            as="p"
                            color="black"
                            lineHeight="1.5em"
                            fontWeight={400}
                            fontSize="1em"
                            fontStyle="normal"
                            textDecoration="none">{item.description}</Text>
                    </Card>
                )}
            </Collection>

            <Heading
                level={4}
                isTruncated={true}
                color="black"
                marginTop={tokens.space.large}
            >
                How it works
            </Heading>

            <Image
                alt="Amplify logo"
                src="https://d1.awsstatic.com/Amazon-Rekognition_Diagram_Identity-Verification_Use-Case.db65dbca5b05473b42e17b218496ed3a820fd13d.png"
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