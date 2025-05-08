import React from 'react';
import { getSharedWithMe } from '../mockApi';

const SharedWithMe = () => {
  const projects = getSharedWithMe('me');
  return (
    <div>
      <h3>Shared With Me</h3>
      {projects.map(p => (
        <div key={p.id} style={{ border: '1px solid lightblue', margin: 5, padding: 5 }}>
          <strong>{p.name}</strong>
          <pre>{p.content}</pre>
        </div>
      ))}
    </div>
  );
};

export default SharedWithMe;

