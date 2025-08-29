import React, { useState } from "react";

const API_BASE = "https://k3rzy54109.execute-api.us-east-2.amazonaws.com";

function App() {
  const [email, setEmail] = useState("");
  const [coin, setCoin] = useState("");
  const [condition, setCondition] = useState("above");
  const [price, setPrice] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch(`${API_BASE}/set-alert`, {
      method: "POST",
      body: JSON.stringify({ userEmail: email, coin, condition, price }),
      headers: { "Content-Type": "application/json" }
    });
    const data = await res.json();
    setMessage(data.message || JSON.stringify(data));
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Crypto Price Alerts</h1>
      <form onSubmit={handleSubmit}>
        <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
        <input placeholder="Coin (e.g., bitcoin)" value={coin} onChange={e => setCoin(e.target.value)} required />
        <select value={condition} onChange={e => setCondition(e.target.value)}>
          <option value="above">Above</option>
          <option value="below">Below</option>
        </select>
        <input placeholder="Price" type="number" value={price} onChange={e => setPrice(e.target.value)} required />
        <button type="submit">Set Alert</button>
      </form>
      <p>{message}</p>
    </div>
  );
}

export default App;
