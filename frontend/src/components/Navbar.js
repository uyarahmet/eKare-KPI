import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.min.js';


export default function Navbar() {



  return(
    <nav className="navbar sticky-top navbar-expand-lg navbar-dark bg-black" style={{height: '60px'}}>
        <div className="container-fluid" style= {{position: 'relative', left: '10px'}}>
        <a style={{position: 'relative', bottom: '0.5px'}} className="navbar-brand" style= {{zoom: '1'}}>KPI</a>
        <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
                <span className="navbar-toggler-icon"></span>
            </button>
        <div className="collapse navbar-collapse " id="navbarNavAltMarkup">
          <div className="navbar-nav me-auto">
          <a className="nav-link" style= {{zoom: '1'}}>My Charts</a>
          <a className="nav-link" style= {{zoom: '1'}}>Data</a>
          </div>
        </div>
        </div>
    </nav>
  )
}
