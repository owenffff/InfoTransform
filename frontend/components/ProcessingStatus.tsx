'use client';

import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { useStore } from '@/lib/store';
import { StreamingEvent } from '@/types';
import { transformFiles } from '@/lib/api';

export function ProcessingStatus() {
  const { isProcessing, selectedFiles } = useStore();
  const [phase, setPhase] = useState('');
  const [progress, setProgress] = useState(0);
  const [total, setTotal] = useState(0);
  const [progressPercent, setProgressPercent] = useState(0);

  useEffect(() => {
    if (!isProcessing) {
      setPhase('');
      setProgress(0);
      setTotal(0);
      setProgressPercent(0);
      return;
    }

    const handleStreamingEvent = (event: CustomEvent<StreamingEvent>) => {
      const data = event.detail;
      
      if (data.type === 'phase_start') {
        setPhase(data.phase || '');
        setProgress(0);
        setTotal(data.total || 0);
        setProgressPercent(0);
      } else if (data.type === 'phase_progress') {
        setProgress(data.progress || 0);
        setTotal(data.total || 0);
        if (data.total && data.total > 0) {
          setProgressPercent(Math.round((data.progress || 0) / data.total * 100));
        }
      } else if (data.type === 'phase_complete') {
        setProgressPercent(100);
      }
    };

    window.addEventListener('streamingEvent' as any, handleStreamingEvent);
    return () => window.removeEventListener('streamingEvent' as any, handleStreamingEvent);
  }, [isProcessing]);

  if (!isProcessing) return null;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 mb-4">
          <Loader2 className="w-16 h-16 text-brand-orange-500 animate-spin" />
        </div>
        
        <p className="text-lg font-medium text-gray-900">
          {phase || 'Transforming your files...'}
        </p>
        
        {total > 0 && (
          <div className="mt-6 max-w-md mx-auto">
            <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
              <div 
                className="h-full progress-gradient transition-all duration-300 ease-out"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <p className="mt-2 text-sm text-gray-600">
              {progress} / {total} files
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

// Helper function to dispatch streaming events
export function dispatchStreamingEvent(event: StreamingEvent) {
  const customEvent = new CustomEvent('streamingEvent', { detail: event });
  window.dispatchEvent(customEvent);
}