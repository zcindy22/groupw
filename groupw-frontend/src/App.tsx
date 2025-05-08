import React from 'react';
import SaveModal from './components/SaveModal';
import MyProjects from './components/MyProjects';
import SharedWithMe from './components/SharedWithMe';
import { TokenProvider, useTokens } from './TokenContext';

const TokenDisplay = () => {
  const { tokens } = useTokens();
  return <div><strong>Tokens:</strong> {tokens}</div>;
};

const App = () => {
  return (
    <TokenProvider>
      <div style={{ padding: 20 }}>
        <h2>LLM Editor – E4 File Management</h2>
        <TokenDisplay />
        <SaveModal onSave={() => {}} />
        <MyProjects />
        <SharedWithMe />
      </div>
    </TokenProvider>
  );
};

export default App;
