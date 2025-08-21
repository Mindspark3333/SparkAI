import React, { useState, useEffect } from 'react';

const SetupConfiguration = () => {
  const [geminiApiKey, setGeminiApiKey] = useState('');
  const [googleCalendarEnabled, setGoogleCalendarEnabled] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

  // Backend API URL
  const BACKEND_URL = 'https://backend-prod-dot-pure-album-439502-s4.uc.r.appspot.com';

  useEffect(() => {
    loadCurrentSettings();
  }, []);

  const loadCurrentSettings = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/user/settings`);
      if (response.ok) {
        const settings = await response.json();
        setGeminiApiKey(settings.gemini_api_key || '');
        setGoogleCalendarEnabled(settings.google_calendar_enabled || false);
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    
    if (!geminiApiKey.trim()) {
      setMessage('Please enter a Gemini API key');
      return;
    }

    setIsSaving(true);
    setMessage('');

    try {
      const response = await fetch(`${BACKEND_URL}/api/user/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          gemini_api_key: geminiApiKey.trim(),
          google_calendar_enabled: googleCalendarEnabled
        }),
      });

      if (response.ok) {
        setMessage('Configuration saved successfully!');
      } else {
        const error = await response.text();
        setMessage(`Failed to save configuration: ${error}`);
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      setMessage(`Failed to save configuration: ${error.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleGoogleCalendarAuth = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/calendar/auth-url`);
      if (response.ok) {
        const data = await response.json();
        window.open(data.auth_url, '_blank');
      } else {
        setMessage('Failed to get Google Calendar authorization URL');
      }
    } catch (error) {
      console.error('Error getting auth URL:', error);
      setMessage(`Failed to authorize Google Calendar: ${error.message}`);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>Setup Configuration</h1>
      
      <form onSubmit={handleSave}>
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Gemini API Key
          </label>
          <input
            type="password"
            value={geminiApiKey}
            onChange={(e) => setGeminiApiKey(e.target.value)}
            placeholder="Enter your Gemini API key"
            style={{
              width: '100%',
              padding: '12px',
              fontSize: '16px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              boxSizing: 'border-box'
            }}
            disabled={isSaving}
          />
          <small style={{ color: '#666', fontSize: '12px' }}>
            Get your API key from <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer">Google AI Studio</a>
          </small>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={googleCalendarEnabled}
              onChange={(e) => setGoogleCalendarEnabled(e.target.checked)}
              style={{ marginRight: '8px' }}
              disabled={isSaving}
            />
            <span>Enable Google Calendar Integration</span>
          </label>
          
          {googleCalendarEnabled && (
            <div style={{ marginTop: '10px', marginLeft: '24px' }}>
              <button
                type="button"
                onClick={handleGoogleCalendarAuth}
                style={{
                  backgroundColor: '#4285f4',
                  color: 'white',
                  border: 'none',
                  padding: '8px 16px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                Authorize Google Calendar
              </button>
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={isSaving}
          style={{
            backgroundColor: isSaving ? '#ccc' : '#28a745',
            color: 'white',
            padding: '12px 24px',
            fontSize: '16px',
            border: 'none',
            borderRadius: '4px',
            cursor: isSaving ? 'not-allowed' : 'pointer'
          }}
        >
          {isSaving ? 'Saving...' : 'Save Configuration'}
        </button>
      </form>

      {message && (
        <div style={{
          marginTop: '15px',
          padding: '10px',
          backgroundColor: message.includes('successfully') ? '#d4edda' : '#f8d7da',
          color: message.includes('successfully') ? '#155724' : '#721c24',
          border: `1px solid ${message.includes('successfully') ? '#c3e6cb' : '#f5c6cb'}`,
          borderRadius: '4px'
        }}>
          {message}
        </div>
      )}
    </div>
  );
};

export default SetupConfiguration;

