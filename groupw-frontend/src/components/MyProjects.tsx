import React from 'react';
import { getMyProjects } from '../mockApi';
import ShareModal from './ShareModal';

const MyProjects = () => {
  const projects = getMyProjects();
  return (
    <div>
      <h3>My Projects</h3>
      {projects.map(p => (
        <div key={p.id} style={{ border: '1px solid gray', margin: 5, padding: 5 }}>
          <strong>{p.name}</strong>
          <pre>{p.content}</pre>
          <ShareModal projectId={p.id} />
        </div>
      ))}
    </div>
  );
};

export default MyProjects;

