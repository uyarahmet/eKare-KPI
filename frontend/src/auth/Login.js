import React, {useState, useContext} from "react"
import './login.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import {AuthContext} from '../contexts/AuthContext'


export default function (props) {

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { isLoggedIn, setIsLoggedIn }  = useContext(AuthContext)


  function handleMailChange(event) {
    setEmail(event.target.value)
  }

  function handlePasswordChange(event) {
    setPassword(event.target.value)
  }

  async function handleSubmit() {
    // fill in backend integration
    const details = {'username': email, 'password': password}

    var formBody = [];
    for (var property in details) {
      var encodedKey = encodeURIComponent(property);
      var encodedValue = encodeURIComponent(details[property]);
      formBody.push(encodedKey + "=" + encodedValue);
    }

    formBody = formBody.join("&");

    const response = await fetch("http://localhost:8000/access", {
      method: "POST",
      body: formBody,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
      }
    })

    if(response.status == 200){
      setIsLoggedIn(true)
      window.location = '/'
    }else{
      //
    }

    console.log(response)

  }

  return (
    <div className="Auth-form-container">
      <form className="Auth-form">
        <div className="Auth-form-content">
          <h3 className="Auth-form-title">Sign In</h3>
          <div className="form-group mt-3">
            <label>Email address</label>
            <input
              type="email"
              className="form-control mt-1"
              placeholder="Enter email"
              onChange={handleMailChange}
            />
          </div>
          <div className="form-group mt-3">
            <label>Password</label>
            <input
              type="password"
              className="form-control mt-1"
              placeholder="Enter password"
              onChange={handlePasswordChange}
            />
          </div>
          <div className="d-grid gap-2 mt-3" style={{position: 'relative', top: '10px'}}>
            <button type="submit" className="btn btn-primary" onClick={handleSubmit}>
              Submit
            </button>
          </div>
          <p className="forgot-password text-right mt-2" style={{position: 'relative', top: '18px'}}>
            Forgot <a href="#">password?</a>
          </p>
          <p className="forgot-password text-right mt-2" style={{position: 'relative', top: '18px'}}>
            Don't have an account? <a href="/signup">Sign Up</a>
          </p>
        </div>
      </form>
    </div>
  )
}
