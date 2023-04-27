import React, {useContext} from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import Login from './auth/Login'
import SignUp from './auth/SignUp'
import Home from './Home'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import AuthContextProvider, {AuthContext} from './contexts/AuthContext'

const RouteComponent = () => {

  const {isLoggedIn, setIsLoggedIn} = useContext(AuthContext)

  return (
    <BrowserRouter>
      <Routes>
      {isLoggedIn? <>
        <Route path="login" element={<Login/>}/>
        <Route path="signup" element={<SignUp/>}/>
        </>
        :
          <Route path="" element={<Home/>}/>
        }
      </Routes>
    </BrowserRouter>
  )
}

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
    <React.StrictMode>
      <AuthContextProvider>
        <RouteComponent/>
      </AuthContextProvider>
    </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
