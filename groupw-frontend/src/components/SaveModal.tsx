import React, { useState } from 'react';
import { saveProject } from '../mockApi';
import { useTokens } from '../TokenContext';

const SaveModal = ({ onSave }: { onSave: Function }) => {
  const [name, setName] = useState('');
  const [content, setContent] = useState('');
  const { updateTokens } = useTokens();

  const handleSave = () => {
    const saved = saveProject(name, content);
    updateTokens(-5);
    onSave(saved);
    setName('');
    setContent('');
  };

  return (
    <div>
      <h3>Save New Project</h3>
      <input value={name} onChange={e => setName(e.target.value)} placeholder="File name" />
      <textarea value={content} onChange={e => setContent(e.target.value)} placeholder="Text content" />
      <button onClick={handleSave}>Save</button>
    </div>
  );
};

export default SaveModal;

