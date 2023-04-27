import {
    View,
    Heading,
    Flex,
    useTheme,
    Alert

} from '@aws-amplify/ui-react';

import { JSONTree } from 'react-json-tree';
import { useLocation } from 'react-router-dom'

function LoggedIn() {

    const { tokens } = useTheme();
    // const navigate = useNavigate()
    const location = useLocation()
    const { label } = location.state
    const { responseData } = location.state
    return (
        <>
            <View justifyContent="center"
                alignItems="center"
                alignContent="center"
                direction={{ base: 'row', large: 'column' }}
            >
                <Heading level={1} color="black">
                    <Alert variation="success">Login Successful!!</Alert>
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
                            Welcome {label}
                        </Heading>
                    </View>
                    {/* <View marginTop={tokens.space.large} >
                        <Button gap="0.2rem" variation="primary" backgroundColor="#ec7211" color="white" onClick={() => navigate(`/login`)} >
                        <ImEnter /> Login
                        </Button>
                    </View> */}
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
                    <JSONTree data={responseData}
                        valueRenderer={(raw) => raw.length > 200 ? (<span style={{ whiteSpace: 'nowrap', display: 'inline-block', maxWidth: '100%', overflow: 'hidden', textOverflow: 'ellipsis', verticalAlign: 'middle' }} >{raw}</span>) : raw} />
                </>
            }

        </>


    );
}

export default LoggedIn;