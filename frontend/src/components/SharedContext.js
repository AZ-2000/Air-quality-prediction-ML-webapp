import React, { createContext, useContext, useState } from "react";

const SharedContext = createContext();
export const useSharedContext = () => useContext(SharedContext);

export const SharedContextProvider = ({children}) =>{
    const [selectedCity, setSelectedCity] = useState("")
    return(
    <SharedContext.Provider value = {{selectedCity, setSelectedCity}}>
        {children}
    </SharedContext.Provider>
    )
}