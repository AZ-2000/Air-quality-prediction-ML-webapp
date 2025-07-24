import React, { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import WaveBackground from "./WaveComponent";

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const { predicted_pm25, dateOnly } = payload[0].payload;

    return (
      <div
        style={{
          background: "#fff",
          border: "1px solid #ccc",
          padding: "8px",
          borderRadius: "6px",
        }}
      >
        <p><strong>{dateOnly}</strong></p>
        <p>PM2.5: {predicted_pm25.toFixed(2)}</p>
      </div>
    );
  }
  return null;
};
const BeforeToggle = ({selectedCityP,setSelectedCityP}) => {
    const [citiesFromDb, setCitiesFromDb] = useState([]);
  useEffect(() => {
    axios.get("http://localhost:5000/get_cities")
      .then((res) => {
        setCitiesFromDb(res.data);
      })
      .catch((err) => {
        console.error("Error fetching cities from DB", err);
      });
  }, []);
    return (
<div className="container mt-4">
      {/* 2x2 Card Grid */}
      <div className="row hover-text">
        <div className="col-md-6 mb-4 russo-font">
          <div
            className="card bg-transparent text-center border-0"
            style={{
              height: "150px",
              paddingTop: "40px",
              fontSize: "10px",
              borderRadius: "12px",
            }}
          >
            <h1 style={{fontSize:"40px"}} className="hover-text">Real time data!</h1>
            <p style={{fontSize:"27px"}} className="hover-text-2">Real time updates on your
              locations air quality </p>
          </div>
        </div>
        <div className="col-md-6 mb-4 russo-font">
          <div
            className="card hover-text bg-transparent text-center border-0"
            style={{
              color: "black",
              height: "150px",
              paddingTop: "40px",
              fontSize: "20px",
              borderRadius: "12px",
            }}
          >
            <h2 className="hover-text"
            style={{fontSize:"40px"}}> Historical trends </h2>
            <p style={{fontSize:"27px"}} className="hover-text-2">
                Just put the name of your city on the search bar on the top right and find out!
              </p>
            
          </div>
        </div>
        <div className="col-md-6 mb-4 russo-font">
          <div
           className="card bg-transparent text-center border-0"
            style={{
              color: "black",
              height: "150px",
              paddingTop: "40px",
              fontSize: "20px",
              borderRadius: "12px",
            }}
          >
 <h2 className="hover-text"
            style={{fontSize:"40px"}}>Similar cities?</h2>
    <p style={{fontSize:"27px"}} className="hover-text-2">
      Curious about cities that have similar air quality? 
      Leverage FAISS to find out!
    </p>

          </div>
        </div>
        <div className="col-md-6 mb-4 russo-font">
          <div
            className="card bg-transparent text-center border-0"
            style={{
              backgroundColor: "rgba(255,255,255,0.1)",
              color: "black",
              height: "150px",
              paddingTop: "40px",
              fontSize: "20px",
              borderRadius: "12px",
            }}
          >
             <h2 className="hover-text"
            style={{fontSize:"40px"}}>Predictions </h2>
        <p style={{fontSize:"27px"}} className="hover-text-2">
          Get accurate predictions for your city by selecting the menu below!
          </p>

          </div>
        </div>
      </div>

      {/* Dropdown Button */}
      <div className="mt-4">
        <label className = "russo-font hover-text" htmlFor="cityDropdown" style={{ fontSize: "16px" }}>
          Select a City:
        </label>
      <select
  id="cityDropdown"
  className="form-select mt-2"
  value={selectedCityP}
  onChange={(e) => setSelectedCityP(e.target.value)}
>
  <option className="russo-font" value="">Choose City</option>
  {citiesFromDb.map((city, index) => (
    <option key={index} className="russo-font" value={city}>
      {city}
    </option>
  ))}
</select>


        {/* <select
  id="cityDropdown"
  className="form-select mt-2"
  value={selectedCity}
  onChange={(e) => setSelectedCity(e.target.value)}
>
  <option value="">-- Choose City --</option>
  {citiesFromDb.map((cityObj, index) => (
    <option key={index} value={cityObj.City_name}>
      {cityObj.City_name}
    </option>
  ))}
</select> */}

      </div>
    </div>

  );
}



const PredictionChartWithCards = ({selectedCityP}) => {
  const [predictionData, setPredictionData] = useState([]);
  const [tickIndices, setTickIndices] = useState([]);
  const [cityNames, setCityNames] = useState([]);
  const [cityValues, setCityValues] = useState([]);

 useEffect(() => {
  // 1. Fetch similar cities
    console.log("selectedCityP:", selectedCityP, typeof selectedCityP);
    const today = new Date();
    const truncateMilliseconds = (isoString) => isoString.split(".")[0] + "Z";
    const endDate = truncateMilliseconds(today.toISOString());

    const pastDate = new Date(today);
    pastDate.setDate(today.getDate() - 3);
    const startDate = truncateMilliseconds(pastDate.toISOString());
  axios.post("http://localhost:5000/search", {
    start_date: startDate,
    end_date: endDate,
  })
    .then((res) => {
      console.log(res)
      const cities = res.data.map((item) => item[0]); // ["Lahore", "Karachi", ...]
      // const values = res.data.map((item) => item[1]); // [83.2, 91.5, ...]
      console.log(cities)
      // console.log(values)
      setCityNames(cities);
      // setCityValues(values);
    })
    .catch((err) => console.error(err));
}, []);
useEffect(() => {
  const fetchLatestValues = async () => {
    const results = await Promise.all(
      cityNames.map(city =>
        axios
          .get('http://localhost:5000/get_latest', { params: { city } })
          .then(res => res.data.value.toFixed(2))  // Round to 2 decimals
          .catch(err => {
            console.error(`Error fetching value for ${city}`, err);
            return "N/A";
          })
      )
    );
    setCityValues(results); // Array like ["83.42", "90.25", ...]
  };

  if (cityNames.length > 0) {
    fetchLatestValues();
  }
}, [cityNames]);

  useEffect(() => {
    const today = new Date();
    const truncateMilliseconds = (isoString) => isoString.split(".")[0] + "Z";
    const endDate = truncateMilliseconds(today.toISOString());

    const pastDate = new Date(today);
    pastDate.setDate(today.getDate() - 3);
    const startDate = truncateMilliseconds(pastDate.toISOString());

    axios
      .post("http://localhost:5000/train_model", {
        city: selectedCityP,
        start_date: startDate,
        end_date: endDate,
      })
      .then((res) => {
        const formatted = res.data.map((item, index) => {
          const dateOnly = item.datetime
            ? new Date(item.datetime).toISOString().split("T")[0]
            : "";
          return {
            ...item,
            xIndex: index,
            dateOnly,
          };
        });

        const dateToIndexMap = new Map();
        formatted.forEach((item) => {
          if (!dateToIndexMap.has(item.dateOnly)) {
            dateToIndexMap.set(item.dateOnly, item.xIndex);
          }
        });

        const uniqueDates = Array.from(dateToIndexMap.keys());
        let selectedDates;
        if (uniqueDates.length >= 3) {
          selectedDates = [
            uniqueDates[0],
            uniqueDates[Math.floor(uniqueDates.length / 2)],
            uniqueDates[uniqueDates.length - 1],
          ];
        } else {
          selectedDates = uniqueDates;
        }

        const tickIndices = selectedDates.map((date) =>
          dateToIndexMap.get(date)
        );

        setPredictionData(formatted);
        setTickIndices(tickIndices);
      })
      .catch((err) => {
        console.error("Fetch failed:", err);
      });
  }, []);

  return (
  <div className="container-fluid mt-4">
    <div className="row align-items-center">
      {/* Graph: wider - col-md-8 */}
      <div className="col-md-8">
        <h5 className="russo-font hover-text" style={{ fontSize: "26px", textAlign: "center"  }}> PM 2.5 PREDICTION FOR {selectedCityP.toUpperCase()} (µg/m³)</h5>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart
            data={predictionData}
            margin={{ top: 20, right: 20, bottom: 20, left: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="xIndex"
              ticks={tickIndices}
              tickFormatter={(index) => {
                const item = predictionData[index];
                if (!item || !item.dateOnly) return "";
                const dateObj = new Date(item.dateOnly + "T00:00:00Z");
                return isNaN(dateObj.getTime())
                  ? ""
                  : dateObj.toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    });
              }}
              stroke="#9f1212" // axis line color
                                tick={{
    fill: "#ffbe47",  // tick label color
    fontSize: 18}}
            />
            <YAxis stroke="#9f1212" // axis line color
                                tick={{
    fill: "#ffbe47",  // tick label color
    fontSize: 18}} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="predicted_pm25"
              name="PM2.5"
              stroke="#9f1212"
              strokeWidth={3}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Cards: 2x2 layout - col-md-4 */}
      <div className="col-md-4">
        <h1 className="hover-text russo-font text-center" style={{
          fontSize:"30px"
        }}> Cities with similar PM2.5 </h1>
        <div className="row">
          {cityNames.slice(0, cityValues.length).map((city, idx) => (
  <div className="col-6 mb-3" key={city}>
    <div
      className="card text-center border-0 russo-font "
      style={{
        backgroundColor: "transparent",
        color: "white",
        height: "178px",
        paddingTop: "25px",
      }}
     >
      <h5 className="hover-text" style={{fontSize:"25px"}}>{city}</h5>
      <p className= "hover-text-2"style={{ fontSize: "20px" }}>
        {cityValues[idx] ? `${cityValues[idx]} µg/m³` : "Loading..."}
                    </p>
             </div>
             </div>
))}

        </div>
      </div>
    </div>
  </div>
);
}

export default function Predictions() {
  
  const [selectedCityP, setSelectedCityP] = useState("");
return(
  <div>
          <WaveBackground />
    
      {selectedCityP ? (
        <PredictionChartWithCards selectedCityP={selectedCityP} />
      ) : (
        <BeforeToggle selectedCityP={selectedCityP} setSelectedCityP={setSelectedCityP} />
      )}
    </div>
)
}


