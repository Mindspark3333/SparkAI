import React, { useState } from "react";
import axios from "axios";

/**
 * ResearchSubmission component
 * Allows users to submit a URL for research/analysis
 */
const ResearchSubmission = ({ userId, onSubmitted }) => {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError(null);

    try {
      const res = await axios.post("/api/research/submit", {
        url,
        user_id: userId,
      });
      if (onSubmitted) onSubmitted(res.data);
      setUrl("");
    } catch (err) {
      console.error(err);
      setError("Failed to submit research request.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded-md shadow-sm bg-white">
      <h3 className="text-lg font-semibold mb-2">Submit Research</h3>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter a URL to analyze"
          className="flex-1 border px-3 py-2 rounded-md"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Submitting..." : "Submit"}
        </button>
      </form>
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </div>
  );
};

export default ResearchSubmission;