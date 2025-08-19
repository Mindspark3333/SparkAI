import React from "react";
import { Routes, Route, Link } from "react-router-dom";
import ResearchSubmission from "./components/ResearchSubmission";
import ResearchBrowser from "./components/ResearchBrowser";
import CalendarIntegration from "./components/CalendarIntegration";
import SetupConfiguration from "./components/SetupConfiguration";
import PWAInstaller from "./components/PWAInstaller";

const App = () => {
  const userId = 1; // TODO: replace with real user authentication

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-blue-600 text-white px-4 py-3 flex gap-4">
        <Link to="/">Home</Link>
        <Link to="/research">Research</Link>
        <Link to="/calendar">Calendar</Link>
        <Link to="/setup">Setup</Link>
      </nav>

      <div className="p-6">
        <Routes>
          <Route path="/" element={<h1 className="text-2xl">Welcome to Master Agent</h1>} />
          <Route
            path="/research"
            element={
              <div className="space-y-6">
                <ResearchSubmission userId={userId} onSubmitted={() => {}} />
                <ResearchBrowser userId={userId} />
              </div>
            }
          />
          <Route path="/calendar" element={<CalendarIntegration />} />
          <Route path="/setup" element={<SetupConfiguration />} />
        </Routes>
      </div>

      <PWAInstaller />
    </div>
  );
};

export default App;