import React from "react";
import SearchButton from "./Button";
import { Link } from "react-router-dom";
import { useSharedContext } from "./SharedContext";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Navbar() {
  const { selectedCity, setSelectedCity } = useSharedContext();
  const [inputValue, setInputValue] = useState("");
  const exceptions = ["WWF", "EPA"]; // Add more acronyms here
  const fullPhraseExceptions = {
  "us diplomatic post: islamabad": "US Diplomatic Post: Islamabad",
  "farhan shah labs": "Farhan Shah Labs",
  "buraq integrated solutions": "Buraq integrated solutions"
};
const cityList = ["Islamabad","Farhan Shah Labs",
    "WWF", "Lahore"
  ];
    const navigate = useNavigate(); // ✅ initialize



const formatCityName = (input) => {
  const trimmed = input.trim();

  // Normalize and match against full phrase exceptions
  const normalized = trimmed.replace(/\s+/g, ' ').toLowerCase();
  if (fullPhraseExceptions.hasOwnProperty(normalized)) {
    return fullPhraseExceptions[normalized];
  }

  // If the whole input is an acronym
  const upper = trimmed.toUpperCase();
  if (exceptions.includes(upper) && trimmed.length === upper.length) {
    return upper;
  }

  // Otherwise, title case and preserve acronyms inside phrases
  return trimmed
    .split(" ")
    .map((word) => {
      const cleaned = word.trim();
      const wordUpper = cleaned.toUpperCase();

      if (exceptions.includes(wordUpper)) {
        return wordUpper;
      }

      return cleaned.charAt(0).toUpperCase() + cleaned.slice(1).toLowerCase();
    })
    .join(" ");
};

  const handleSubmit = (e) =>{
       e.preventDefault();
     const trimmed = inputValue.trim();
     if (!trimmed) return;

      const formatted = formatCityName(trimmed);
          if (cityList.includes(formatted)) {
      setSelectedCity(formatted);
      setInputValue("");
      navigate("/history"); // ✅ Navigate after valid input
    } else {
      alert("Please enter a valid city.");
    }

  setSelectedCity(formatted);
  setInputValue("");
;

    // if (trimmed) {      
    // setSelectedCity(inputValue.trim().toLowerCase().replace(/^\w/, c => c.toUpperCase()));
    // console.log({selectedCity})
    //   setInputValue(""); // Optional: clear the input
      
    // }

  }
  
    return(
  <nav class="navbar navbar-expand-lg navbar-dark py-4 mb-2 nav-wrapper"
    style={{ backgroundColor: '#8B0000' }}
>
  <div class="container-fluid">
    <Link className="navbar-brand text-warning russo-font" to="/">Air Quality</Link>
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">
        <li class="nav-item">
          <Link className="nav-link active text-warning russo-font" aria-current="page" to="/">Home</Link>
        </li>
            <li className="nav-item">
              <Link className="nav-link active text-warning russo-font" to="/predictions">Predictions</Link>
            </li>
          <li>
              <Link className="nav-link active text-warning russo-font" to="/history">History</Link>
          </li>

      </ul>
      <form class="d-flex" onSubmit={handleSubmit}>
        <input list="CityOptions" class="form-control me-2 russo-font" type="text" placeholder="Search Historical data"
        value={inputValue}
        onChange={(e)=>setInputValue(e.target.value)} aria-label="Search"/>
        <datalist id= "CityOptions">
          {cityList.map((city,index) => (
            <option key={index} value={city}/>
          ) )}
        </datalist>
        <SearchButton/>
              </form>
    </div>
  </div>
</nav>
)
}
