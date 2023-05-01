import './App.css';
import { API, Auth } from 'aws-amplify';
import React from "react";
import RIVHeader from './Components/Header'
import AppLayout from "@awsui/components-react/app-layout";
import { AppLayoutProvider } from "./Components/context/AppLayoutContext"
import {
    ThemeProvider
} from '@aws-amplify/ui-react';
import { useAppLayoutContext } from "./Components/context/AppLayoutContext"
import { useAppLayout } from "use-awsui"
import { BrowserRouter } from "react-router-dom"
import Routes from "./Components/Routes"
import SideNavigation from './Components/SideNavigation'


Auth.configure({
    "Auth": {
        "identityPoolId": process.env.REACT_APP_IDENTITYPOOL_ID,
        "region": process.env.REACT_APP_REGION,
        "userPoolId": process.env.REACT_APP_USERPOOL_ID,
        "mandatorySignIn": false,
        "userPoolWebClientId": process.env.REACT_APP_WEBCLIENT_ID
        // "identityPoolId": "us-east-1:763cb669-b748-498a-ae6b-4cabfb0e457e",
        // "region": "us-east-1",
        // "userPoolId": "us-east-1_dJkZVBJIN",
        // "mandatorySignIn": false,
        // "userPoolWebClientId": "6uvfrd4dllnh1h2rck8utka07d"
    }
})

API.configure({
    API: {
        endpoints: [
            {
                name: "identityverification",
                endpoint: process.env.REACT_APP_ENV_API_URL
                // endpoint: "https://bu3wsszai5.execute-api.us-east-1.amazonaws.com/prod/"
            },
        ],
    },
})

function App() {
    const theme = {
        name: 'my-theme',
        tokens: {
            components: {
                text: {
                    color: { value: '232f3e' },
                },

                card: {
                    backgroundColor: { value: '#fff' },
                    // Variations
                    outlined: {
                    },
                    elevated: {
                        boxShadow: { value: '{shadows.large}' },
                    },

                }
            },
            colors: {
                background: {
                    primary: { value: '#0F1111' },
                    secondary: { value: '#fff' },
                    tertiary: { value: '#0F1111' },
                },
                border: {
                    primary: { value: '#0F1111' },
                    secondary: { value: '#0F1111' },
                    tertiary: { value: '#0F1111' },
                },
            },
        },
    };
    const { handleNavigationChange, navigationOpen } = useAppLayout({
        defaultNavigationOpen: true,
        defaultToolsOpen: true
    })
    let {
        state: { navigationHide, contentType }
    } = useAppLayoutContext()

    return (

        <AppLayoutProvider>
            <ThemeProvider theme={theme} >
                <BrowserRouter>
                    <RIVHeader></RIVHeader>
                    <AppLayout
                        headerSelector="#header"
                        onNavigationChange={handleNavigationChange}
                        navigationOpen={navigationOpen}
                        navigationHide={navigationHide}
                        navigation={<SideNavigation />}
                        toolsHide
                        contentType={contentType}
                        content={
                            <div>
                                <Routes></Routes>
                            </div>
                        }
                    />
                </BrowserRouter>
            </ThemeProvider>
        </AppLayoutProvider>

    );
}

export default App;
