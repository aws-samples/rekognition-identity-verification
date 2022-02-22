import './App.css';
import React from 'react';
import Amplify from "aws-amplify";
import Layout from './Pages/Layout'
import Header from './Components/Header';
import { BrowserRouter } from 'react-router-dom';
Amplify.configure({
  // Add in our new API, "name" can be whatever we want
  API: {
    endpoints: [
      {
        name: "identityverification",
        endpoint:process.env.REACT_APP_ENV_API_URL
      },
    ],
  },
});


function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Header />
        <Layout />
      </BrowserRouter>
    </div>
  );
}

export default App;
