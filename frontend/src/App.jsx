import { useState } from "react";
import Chat from "./components/Chat.jsx";
import DocumentUpload from "./components/DocumentUpload.jsx";
import Login from "./components/Login.jsx";

export default function App() {
  const [loggedIn, setLoggedIn] = useState(!!localStorage.getItem("token"));

  const handleLogout = () => {
    localStorage.removeItem("token");
    setLoggedIn(false);
  };

  if (!loggedIn) {
    return (
      <div className="app-container centered">
        <Login onLoggedIn={() => setLoggedIn(true)} />
      </div>
    );
  }

  return (
    <div className="app-container">
      <header>
        <h1>📚 Technical Document Assistant</h1>
        <button onClick={handleLogout}>Log out</button>
      </header>
      <main>
        <DocumentUpload />
        <Chat />
      </main>
    </div>
  );
}
