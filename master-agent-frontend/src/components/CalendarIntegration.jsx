import React, { useState } from "react";

/**
 * CalendarIntegration component
 * Stub for integrating with Google Calendar or other calendar APIs.
 */
const CalendarIntegration = () => {
  const [connected, setConnected] = useState(false);

  const handleConnect = () => {
    // In real implementation: redirect to OAuth flow for Google Calendar
    setConnected(true);
    alert("Calendar integration connected (stub).");
  };

  return (
    <div className="p-4 border rounded-md shadow-sm bg-white">
      <h3 className="text-lg font-semibold mb-2">Calendar Integration</h3>
      {connected ? (
        <p className="text-green-600">Connected to your calendar!</p>
      ) : (
        <button
          onClick={handleConnect}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Connect Calendar
        </button>
      )}
    </div>
  );
};

export default CalendarIntegration;