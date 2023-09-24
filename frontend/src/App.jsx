import React, {useEffect, useState} from "react";


const App = () => {
    const [message, setMessage] = useState([]);

    const getWelcomeMessage = async () => {
        const requestOptions = {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        };
        const response = await fetch("/users/", requestOptions);
        const data = await response.json();

        if (!response.ok) {
            console.log("something went wrong");
        } else {
            console.log(data);
            setMessage(data);
        }
    };

    useEffect(() => {
        getWelcomeMessage();
    }, []);

    return (
      <div>
        <ul>
          {message.map(user => (
            <li key={user.id}>
              {user.first_name} {user.last_name} - {user.email}
            </li>
          ))}
        </ul>
      </div>
    );
};
const Testing = <h3>Render testing</h3>

export { App, Testing };
// export default App;
