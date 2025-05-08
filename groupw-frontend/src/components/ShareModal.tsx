import React, { useState } from 'react';
import { shareProject } from '../mockApi';

const ShareModal = ({ projectId }: { projectId: string }) => {
  const [user, setUser] = useState('');
  const handleShare = () => {
    shareProject(projectId, user);
    alert(`Shared with ${user}`);
    setUser('');
  };

  return (
    <div>
      <input value={user} onChange={e => setUser(e.target.value)} placeholder="User to share with" />
      <button onClick={handleShare}>Share</button>
    </div>
  );
};

export default ShareModal;

