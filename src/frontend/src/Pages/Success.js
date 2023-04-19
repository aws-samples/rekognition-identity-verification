import {
    View,
    Heading,
    Flex,
    Button,
    useTheme,
    Alert

} from '@aws-amplify/ui-react';
import { useNavigate } from "react-router-dom"
import { ImEnter } from "react-icons/im";
import { JSONTree } from 'react-json-tree';
import { useLocation } from 'react-router-dom'

function Success() {

    const { tokens } = useTheme();
    const navigate = useNavigate()
    const location = useLocation()
    // const { label } = location.state
    const { responseData } = location.state
    return (


        <>
            <View justifyContent="center"
                alignItems="center"
                alignContent="center"
                direction={{ base: 'row', large: 'column' }}
            >
                <Heading level={1} color="black">
                    <Alert variation="success">Success</Alert>
                </Heading>

                <Flex marginTop={tokens.space.large} direction="column"
                    justifyContent="space-around"
                    alignItems="center"
                    alignContent="stretch"
                    wrap="nowrap"
                    gap="1rem">
                    <View>
                        <Heading level={3} color="black" justifyContent="center"
                            alignItems="center"
                            alignContent="center">
                            Congratulations, your account has been successfully created.
                        </Heading>
                    </View>
                    <View marginTop={tokens.space.large} >
                        <Button gap="0.2rem" variation="primary" backgroundColor="#ec7211" color="white" onClick={() => navigate(`/login`)} >
                        <ImEnter /> Login
                        </Button>
                    </View>
                </Flex>

            </View>

            {responseData &&
                <>
                    <Heading
                        level={5}
                        color="black"
                        marginTop={tokens.space.large}
                        marginBottom={tokens.space.large}
                    >
                        Response:
                    </Heading>
                    <JSONTree data={responseData} />
                </>
            }



        </>


    );
}

export default Success;