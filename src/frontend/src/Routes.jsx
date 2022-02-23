import * as React from 'react';
import { Route, Routes } from 'react-router-dom';
import Register from './Pages/Register';
import RegisterWithIdCard from './Pages/RegisterWithIdCard';
import SuccessPage from './Pages/SuccessPage';
import SignIn from './Pages/SignIn';
import Profile from './Pages/Profile';
import Login from './Pages/RegOrSign';

// Define routing for the Navigation on the page
const routes = (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="registerwithid" element={<RegisterWithIdCard />} />
      <Route path="register" element={<Register />} />
      <Route path="success" element={<SuccessPage />} />
      <Route path="signin" element={<SignIn />} />
      <Route path="profile" element={<Profile />} />
      <Route path="login" element={<Login />} />
    </Routes>

);
export default routes;