import React, { useEffect, useState } from "react";
import axios from "axios";

/**
 * ResearchBrowser component
 * Displays a list of research results for the user
 */
const ResearchBrowser = ({ userId }) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`/api/research/list/${userId}`);
      setResults(res.data);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch research results.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchResults();
    }
  }, [userId]);

  if (loading) return <p>Loading research results...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold mb-4">Research Results</h3>
      {results.length === 0 ? (
        <p>No research results yet. Submit a URL to get started.</p>
      ) : (
        <ul className="space-y-4">
          {results.map((r) => (
            <li key={r.id} className="border p-4 rounded-md bg-white shadow-sm">
              <h4 className="font-bold">{r.title || r.source_url}</h4>
              <p className="text-sm text-gray-600">{r.source_url}</p>
              {r.content_summary && (
                <p className="mt-2 text-gray-800">{r.content_summary}</p>
              )}
              {r.key_points && r.key_points.length > 0 && (
                <ul className="list-disc list-inside mt-2 text-gray-700">
                  {r.key_points.map((pt, i) => (
                    <li key={i}>{pt}</li>
                  ))}
                </ul>
              )}
              {r.tags && r.tags.length > 0 && (
                <div className="mt-2">
                  {r.tags.map((tag, i) => (
                    <span
                      key={i}
                      className="inline-block bg-gray-200 text-gray-700 text-xs px-2 py-1 rounded mr-2"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ResearchBrowser;