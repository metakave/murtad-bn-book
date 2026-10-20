import React, { Component } from 'react';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, info: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('Reader App Error:', error, info);
    this.setState({ info });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '24px', fontFamily: 'sans-serif', color: '#b91c1c', background: '#fef2f2', minHeight: '100vh' }}>
          <h2>Application Rendering Error</h2>
          <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', background: '#fff', padding: '16px', borderRadius: '8px', border: '1px solid #fca5a5' }}>
            {this.state.error?.toString()}
          </pre>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px', marginTop: '12px' }}>
            {this.state.info?.componentStack}
          </pre>
          <button 
            onClick={() => { localStorage.clear(); window.location.reload(); }}
            style={{ marginTop: '16px', padding: '10px 18px', background: '#dc2626', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer' }}
          >
            Clear Cache & Reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

const rootEl = document.getElementById('root');
if (rootEl) {
  if (!window.__reactRoot) {
    window.__reactRoot = createRoot(rootEl);
  }
  window.__reactRoot.render(
    <StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </StrictMode>
  );
}
