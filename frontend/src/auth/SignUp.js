import React, {useState} from "react"
import './signup.css'
import 'bootstrap/dist/css/bootstrap.min.css';


export default function (props) {

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [reenteredPassword, setReenteredPassword] = useState('')


  function handleMailChange(event) {
    setEmail(event.target.value)
  }

  function handlePasswordChange(event) {
    setPassword(event.target.value)
  }

  function handleReenteredPasswordChange(event) {
    setReenteredPassword(event.target.value)
  }

  function handleSubmit() {
    // fill in backend integration
  }

  return (
    <div className="Auth-form-container">
      <form className="Auth-form">
        <div className="Auth-form-content">
          <h3 className="Auth-form-title">Sign Up</h3>
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
          <div className="form-group mt-3">
            <label>Reenter Password</label>
            <input
              type="password"
              className="form-control mt-1"
              placeholder="Enter password again"
              onChange={handleReenteredPasswordChange}
            />
          </div>
          <div className="d-grid gap-2 mt-3" style={{position: 'relative', top: '10px'}}>
            <button type="submit" className="btn btn-primary" onClick={handleSubmit}>
              Submit
            </button>
          </div>

          <p className="forgot-password text-right mt-2" style={{position: 'relative', top: '18px'}}>
            Already have an account? <a href="/login">Login</a>
          </p>
        </div>
      </form>
    </div>
  )
}
