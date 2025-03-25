import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Create a root element
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

// Render the app
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
