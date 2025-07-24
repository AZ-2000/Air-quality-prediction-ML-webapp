import React from "react";
import { useState } from "react";

export default function SearchButton()
{
    const [hover, setHover] = useState(false);
    const buttonstyle = {
        backgroundColor : hover? "#FFD700" : "#8B0000",
        color: hover ? "#8B0000" : "#FFD700",
        border: `1px solid ${hover ? "#FFD700" : "#8B0000"}`,
        padding: "0.375rem 0.75rem",
        fontSize: "1rem",
        borderRadius: "0.25rem",
        cursor: "pointer",
        fontFamily: "'Russo One', sans-serif",
        transition: "all 0.3s ease"
    }

    return(
        <button
        type="submit"
        style={buttonstyle}
        onMouseEnter={()=>setHover(true)}
        onMouseLeave = {() =>setHover(false)}>
        Search
        </button>
    )
}