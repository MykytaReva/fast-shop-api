import React from 'react';
import createRoot from 'react-dom';
// import App from "./App";
import { App, Testing } from "./App";

createRoot.render(<App />, document.getElementById('root'));
createRoot.render(Testing, document.getElementById('testing'));