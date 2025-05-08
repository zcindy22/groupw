import { Project } from './types';

let projects: Project[] = [];

export const saveProject = (name: string, content: string): Project => {
  const newProject = { id: Date.now().toString(), name, content, sharedWith: [] };
  projects.push(newProject);
  return newProject;
};

export const shareProject = (projectId: string, user: string) => {
  const proj = projects.find(p => p.id === projectId);
  if (proj && !proj.sharedWith.includes(user)) proj.sharedWith.push(user);
};

export const getMyProjects = () => projects;
export const getSharedWithMe = (user: string) => projects.filter(p => p.sharedWith.includes(user));

