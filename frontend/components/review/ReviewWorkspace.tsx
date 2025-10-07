'use client';

import { useEffect } from 'react';
import { ReviewSession } from '@/types';
import { useReviewStore } from '@/lib/store';
import { FileListSidebar } from './FileListSidebar';
import { DocumentViewer } from './DocumentViewer';
import { DataPanel } from './DataPanel';

interface ReviewWorkspaceProps {
  session: ReviewSession;
}

export function ReviewWorkspace({ session }: ReviewWorkspaceProps) {
  const { currentSession, currentFileIndex, setCurrentSession, isSidebarCollapsed } = useReviewStore();

  useEffect(() => {
    if (session) {
      setCurrentSession(session);
    }
  }, [session, setCurrentSession]);

  if (!currentSession) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-orange-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading review session...</p>
        </div>
      </div>
    );
  }

  const currentFile = currentSession.files[currentFileIndex];

  if (!currentFile) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No files to review</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Review Workspace</h1>
            <p className="text-sm text-gray-600 mt-1">
              {currentFile.filename} ({currentFileIndex + 1} of {currentSession.files.length})
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="text-sm">
              <span className="font-medium text-green-600">
                {currentSession.batch_metadata?.approved_count || 0}
              </span>
              <span className="text-gray-600"> approved</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <FileListSidebar files={currentSession.files} />
        
        <div className={cn(
          'flex-1 flex transition-all duration-300',
          isSidebarCollapsed ? 'ml-0' : ''
        )}>
          <div className="flex-1 overflow-hidden">
            <DocumentViewer file={currentFile} />
          </div>
          
          <div className="w-1/2 border-l overflow-hidden">
            <DataPanel file={currentFile} />
          </div>
        </div>
      </div>
    </div>
  );
}

function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(' ');
}
