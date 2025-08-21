import React, { useState, useEffect } from 'react';

const ResearchBrowser = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // Backend API URL
  const BACKEND_URL = 'https://backend-prod-dot-pure-album-439502-s4.uc.r.appspot.com';

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/research/results`);
      
      if (response.ok) {
        const data = await response.json();
        setResults(data.results || []);
        setError('');
      } else {
        setError('Failed to fetch research results');
      }
    } catch (err) {
      console.error('Error fetching results:', err);
      setError(`Failed to fetch research results: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const createCalendarEvent = async (resultId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/research/${resultId}/create-event`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        alert('Calendar event created successfully!');
      } else {
        const error = await response.text();
        alert(`Failed to create calendar event: ${error}`);
      }
    } catch (error) {
      console.error('Error creating calendar event:', error);
      alert(`Failed to create calendar event: ${error.message}`);
    }
  };

  const filteredResults = results.filter(result =>
    result.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    result.url?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    result.summary?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>Loading research results...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Research Results</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Search results..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            width: '100%',
            padding: '10px',
            fontSize: '16px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            boxSizing: 'border-box'
          }}
        />
      </div>

      {error && (
        <div style={{
          padding: '10px',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          border: '1px solid #f5c6cb',
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          {error}
        </div>
      )}

      {filteredResults.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#666' }}>
          <p>No research results found.</p>
          <p>Submit some URLs for research to see results here!</p>
        </div>
      ) : (
        <div>
          {filteredResults.map((result) => (
            <div
              key={result.id}
              style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '15px',
                marginBottom: '15px',
                backgroundColor: '#f9f9f9'
              }}
            >
              <div style={{ marginBottom: '10px' }}>
                <h3 style={{ margin: '0 0 5px 0', color: '#333' }}>
                  {result.title || 'Research Result'}
                </h3>
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: '#007cba', textDecoration: 'none', fontSize: '14px' }}
                >
                  {result.url}
                </a>
              </div>
              
              {result.summary && (
                <div style={{ marginBottom: '10px' }}>
                  <p style={{ margin: '0', lineHeight: '1.5' }}>{result.summary}</p>
                </div>
              )}
              
              {result.key_insights && result.key_insights.length > 0 && (
                <div style={{ marginBottom: '10px' }}>
                  <strong>Key Insights:</strong>
                  <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                    {result.key_insights.map((insight, index) => (
                      <li key={index}>{insight}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <small style={{ color: '#666' }}>
                  {result.created_at ? new Date(result.created_at).toLocaleDateString() : 'Unknown date'}
                </small>
                
                <button
                  onClick={() => createCalendarEvent(result.id)}
                  style={{
                    backgroundColor: '#28a745',
                    color: 'white',
                    border: 'none',
                    padding: '8px 16px',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  Create Calendar Event
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ResearchBrowser;
