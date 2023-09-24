import React, {createContext, useState} from "react";

export const UserContext = createContext();

export const UserProvider = props => {
    const [token, setToken] = useState(localStorage.getItem("token"));

    userEffect(() => {
        const fetchUser = async () => {
            const requestOptions = {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            };
            
        }
    }
}