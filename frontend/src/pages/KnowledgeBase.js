import React from 'react';

const KnowledgeBase = () => {
  const baseUrl = process.env.NODE_ENV === 'production'
    ? '/ai/admin'
    : (process.env.REACT_APP_AI_ASSISTANT_URL || 'http://localhost:8001') + '/admin';

  return (
    <div className="h-full w-full -m-6">
      <iframe
        src={baseUrl}
        title="Knowledge Base Admin"
        className="w-full border-0"
        style={{ height: 'calc(100vh - 64px)' }}
      />
    </div>
  );
};

export default KnowledgeBase;
