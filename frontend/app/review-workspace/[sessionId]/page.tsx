'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { ReviewWorkspace } from '@/components/review/ReviewWorkspace';
import { ReviewSession } from '@/types';
import { getReviewSession } from '@/lib/api';

export default function ReviewWorkspacePage() {
  const params = useParams();
  const sessionId = params.sessionId as string;
  const [session, setSession] = useState<ReviewSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (sessionId) {
      getReviewSession(sessionId)
        .then(data => {
          setSession(data);
          setLoading(false);
        })
        .catch(err => {
          setError(err.message);
          setLoading(false);
        });
    }
  }, [sessionId]);

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-orange-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading review session...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Review session not found</h2>
          <p className="text-gray-600">The requested review session could not be found.</p>
        </div>
      </div>
    );
  }

  return <ReviewWorkspace session={session} />;
}
