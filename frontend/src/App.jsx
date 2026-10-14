import { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("Connecting to ScopeSentry API...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/health")
      .then((response) => {
        if (!response.ok) {
          throw new Error("API request failed");
        }
        return response.json();
      })
      .then((data) => {
        setMessage(`API Status: ${data.status} | Application: ${data.application}`);
      })
      .catch(() => {
        setMessage("Could not connect to the backend.");
      });
  }, []);

  return (
    <main style={{ fontFamily: "Arial, sans-serif", padding: "40px" }}>
      <h1>ScopeSentry</h1>
      <p>Client Request Scope Analysis Platform</p>
      <p>{message}</p>
    </main>
  );
}

export default App;