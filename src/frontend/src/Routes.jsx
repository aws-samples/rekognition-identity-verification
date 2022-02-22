import * as React from 'react';
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom';
import Register from './Pages/Register';
import RegisterWithID from './Pages/RegisterWithID';
import SuccessPage from './Pages/SuccessPage';
import SignIn from './Pages/SignIn';
import Profile from './Pages/Profile';
import Login from './Pages/RegOrSign';

// function ProtectedRoute({ component: Component, ...restOfProps }) {
//   const isAuthenticated = localStorage.getItem("isAuthenticated");
//   console.log("this", isAuthenticated);

//   return (
//     <Route
//       {...restOfProps}
//       render={(props) =>
//         isAuthenticated ? <Component {...props} /> : <Navigate to="/login" />
//       }
//     />
//   );
// }

const routes = (


    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="registerwithid" element={<RegisterWithID />} />
      <Route path="register" element={<Register />} />
      <Route path="success" element={<SuccessPage />} />
      <Route path="signin" element={<SignIn />} />
      <Route path="profile" element={<Profile />} />
      <Route path="login" element={<Login />} />
    </Routes>

);

export default routes;