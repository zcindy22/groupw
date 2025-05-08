import React, { createContext, useContext, useState } from 'react';

const TokenContext = createContext({ tokens: 50, updateTokens: (n: number) => {} });

export const TokenProvider = ({ children }: { children: React.ReactNode }) => {
  const [tokens, setTokens] = useState(50);
  const updateTokens = (change: number) => setTokens(prev => Math.max(0, prev + change));
  return (
    <TokenContext.Provider value={{ tokens, updateTokens }}>
      {children}
    </TokenContext.Provider>
  );
};

export const useTokens = () => useContext(TokenContext);
