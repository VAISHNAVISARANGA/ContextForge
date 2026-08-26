import { useState } from "react";
import { login, signup } from "../api";

export default function Login({ onLoggedIn }) {
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      if (isSignup) {
        await signup(email, password);
      }
      const res = await login(email, password);
      localStorage.setItem("token", res.data.access_token);
      onLoggedIn();
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    }
  };

  return (
    <div className="auth-card">
      <h2>{isSignup ? "Create account" : "Log in"}</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">{isSignup ? "Sign up" : "Log in"}</button>
      </form>
      {error && <p className="error">{error}</p>}
      <button className="link" onClick={() => setIsSignup(!isSignup)}>
        {isSignup ? "Already have an account? Log in" : "Need an account? Sign up"}
      </button>
    </div>
  );
}
