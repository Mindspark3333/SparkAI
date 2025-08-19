import React, { useState } from "react";

/**
 * Setup Configuration component.
 * Lets user configure API keys, preferences, etc.
 */
const SetupConfiguration = ({ onSave }) => {
  const [geminiKey, setGeminiKey] = useState("");
  const [preferences, setPreferences] = useState({});

  const handleSave = () => {
    const config = {
      geminiKey,
      preferences,
    };
    if (onSave) onSave(config);
    alert("Configuration saved!");
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Setup Configuration</h2>

      <div className="mb-4">
        <label className="block font-medium mb-1">Gemini API Key</label>
        <input
          type="password"
          value={geminiKey}
          onChange={(e) => setGeminiKey(e.target.value)}
          className="w-full border rounded-md px-3 py-2"
          placeholder="Enter your Gemini API key"
        />
      </div>

      <div className="mb-4">
        <label className="block font-medium mb-1">Preferences (JSON)</label>
        <textarea
          value={JSON.stringify(preferences, null, 2)}
          onChange={(e) => {
            try {
              setPreferences(JSON.parse(e.target.value));
            } catch {
              // Ignore JSON parse errors
            }
          }}
          className="w-full border rounded-md px-3 py-2 font-mono text-sm"
          rows={6}
        />
      </div>

      <button
        onClick={handleSave}
        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
      >
        Save Configuration
      </button>
    </div>
  );
};

export default SetupConfiguration;