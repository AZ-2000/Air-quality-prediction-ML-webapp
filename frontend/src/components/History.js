import React from "react";
import { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import { useSharedContext } from "./SharedContext";
import WaveBackground from "./WaveComponent";

export default function HistoricalData(){
    const { selectedCity } = useSharedContext();
    const [histdata, setHistData] = useState([])
    const [tickIndices, setTickIndices] = useState([]);
    useEffect(() => {
        if(!selectedCity) return;
    const today = new Date();
    const truncateMilliseconds = (isoString) => isoString.split(".")[0] + "Z";
    const endDate = truncateMilliseconds(today.toISOString());

    const pastDate = new Date(today);
    pastDate.setDate(today.getDate() - 10);
    const startDate = truncateMilliseconds(pastDate.toISOString());

    axios
      .post("http://localhost:5000/history", {
        city: selectedCity,
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
            console.log("i am here")


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

        setHistData(formatted);
        console.log("Historical Data Received:", formatted); // ✅

        setTickIndices(tickIndices);
      })
      .catch((err) => {
        console.error("Fetch failed:", err);
      });
  }, [selectedCity]);
return (
    <>
          <WaveBackground />
    
            <h2 style={{fontSize:"45px"}} className="text-center russo-font hover-text"> Historical Data for {selectedCity} will appear below
               </h2>
               <p style= {{ fontSize: "30px"}}className="russo-font hover-text-2 text-center">
                Use the search bar on the top right for more cities </p>
            {
                histdata.length > 0 && (
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={histdata}>
                            <XAxis dataKey= "xIndex" 
                              stroke="#9f1212" // axis line color
                                tick={{
    fill: "#ffbe47",  // tick label color
    fontSize: 18
  }}

                            ticks={tickIndices}
                            tickFormatter={(index) => {
                const item = histdata[index];
                if (!item || !item.dateOnly) return "";
                const dateObj = new Date(item.dateOnly + "T00:00:00Z");
                return isNaN(dateObj.getTime())
                  ? ""
                  : dateObj.toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    });
              }}  />
                            <YAxis
                            stroke="#9f1212" // axis line color
                                tick={{
    fill: "#ffbe47",  // tick label color
    fontSize: 18}}/>
                            <Tooltip/>
                            <Legend/>
                            <Bar dataKey="pm25" fill="#9f1212" />
                        </BarChart>
                    </ResponsiveContainer>
                )
            }    
    </>
)
}