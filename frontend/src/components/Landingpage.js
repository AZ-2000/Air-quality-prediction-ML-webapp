import React, { useState, useEffect } from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import WaveBackground from "./WaveComponent";
import axios from 'axios';

const CityData = ({ city }) => {
  const [value, setValue] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:5000/get_latest', {
      params: { city }
    })
    .then(res => {
      setValue(res.data.value);
    })
    .catch(err => {
      console.error(err);
    });
  }, [city]);

  return (
    <div className="card bg-transparent border-0 p-3 text-center">
      <h5 className="hover-text" style={{ fontSize: '40px' }}>{city}</h5>
      <p className="hover-text-2" style={{ fontSize: '26px' }}>
        {value !== null ? `${value.toFixed(1)} mg` : 'Loading...'}
      </p>
    </div>
  );
};

export default function LandingPage() {
  const cities = ["Lahore", "Islamabad", "Karachi", "Peshawar", "WWF", "EPA Office"];

  return (
    <>
      <WaveBackground />
      <div className="container my-5 landing-content">
        <div className="row">
          <div className="mb-3 col-md-9">
            <h2 className="russo-font hover-text" style={{ fontSize: '50px' }}>Air Quality of major cities</h2>
          </div>
          <div className="col-md-3 mb-2">
            <h2 className="russo-font text-center hover-text" style={{ fontSize: '40px' }}>About PM25</h2>
          </div>
        </div>

        <div className="row russo-font">
          {/* Left 9/12 section with cards */}
          <div className="col-md-9">
            <div className="row mb-5">
              {cities.slice(0, 3).map(city => (
                <div className="col-md-4" key={city}>
                  <CityData city={city} />
                </div>
              ))}
            </div>
            <div className="row">
              {cities.slice(3).map(city => (
                <div className="col-md-4" key={city}>
                  <CityData city={city} />
                </div>
              ))}
            </div>
          </div>

          {/* Right 3/12 section for paragraph */}
          <div className="col-md-3">
            <div className="p-3">
              <p className=" hover-text-2" style={{ fontSize: '25px' }}>
 Make use of our state of the art technological methods to predict, and view historical trends about the very air that you breathe!
      </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
