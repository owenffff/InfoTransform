'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { Task, TaskContent, TaskItem, TaskTrigger } from '@/components/ai-elements/task';
import { Loader as AiLoader } from '@/components/ai-elements/loader';
import {
  FileText,
  Sparkles,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import {
  addStreamingEventListener,
  removeStreamingEventListener,
  type StreamingEvent,
} from '@/components/ProcessingStatus';

type ItemState = 'pending' | 'in_progress' | 'completed' | 'error';
type FileTaskStatus = 'pending' | 'in_progress' | 'completed' | 'error';

interface TaskItemState {
  key: 'convert' | 'analyze' | 'result';
  label: string;
  state: ItemState;
  error?: string;
}

interface FileTask {
  filename: string;
  status: FileTaskStatus;
  items: TaskItemState[];
}

function statusLabel(status: FileTaskStatus) {
  switch (status) {
    case 'pending':
      return 'Pending';
    case 'in_progress':
      return 'Processing';
    case 'completed':
      return 'Completed';
    case 'error':
      return 'Failed';
    default:
      return '';
  }
}

function itemIcon(item: TaskItemState) {
  const common = 'w-4 h-4';
  if (item.key === 'convert') return <FileText className={common} />;
  if (item.key === 'analyze') return <Sparkles className={common} />;
  if (item.key === 'result') {
    if (item.state === 'completed') return <CheckCircle2 className={`${common} text-green-600`} />;
    if (item.state === 'error') return <XCircle className={`${common} text-red-600`} />;
    return <CheckCircle2 className={common} />;
  }
  return null;
}

export function ProcessingTasks() {
  const [tasks, setTasks] = useState<Record<string, FileTask>>({});
  const [handlerId] = useState(() => `tasks-${Date.now()}-${Math.random()}`);

  const ensureTask = (filename: string) => {
    setTasks((prev) => {
      if (prev[filename]) return prev;
      return {
        ...prev,
        [filename]: {
          filename,
          status: 'pending',
          items: [
            { key: 'convert', label: 'Converting to markdown', state: 'pending' },
            { key: 'analyze', label: 'Analyzing with AI', state: 'pending' },
            { key: 'result', label: 'Finalize', state: 'pending' },
          ],
        },
      };
    });
  };

  const updateItemState = (filename: string, key: TaskItemState['key'], next: Partial<TaskItemState>, overall?: FileTaskStatus) => {
    setTasks((prev) => {
      const t = prev[filename];
      if (!t) return prev;
      const items = t.items.map((it) =>
        it.key === key ? { ...it, ...next } : it
      );
      return {
        ...prev,
        [filename]: {
          ...t,
          status: overall ?? t.status,
          items,
        },
      };
    });
  };

  useEffect(() => {
    const onEvent = (event: StreamingEvent) => {
      if (event.type === 'reset') {
        setTasks({});
        return;
      }

      // Events tied to a specific file
      const filename = event.filename;
      if (!filename) return;

      switch (event.type) {
        case 'markdown_conversion':
          ensureTask(filename);
          // set convert in_progress
          updateItemState(filename, 'convert', { state: 'in_progress' }, 'in_progress');
          break;

        case 'ai_analysis':
          ensureTask(filename);
          // mark convert completed, analyze in_progress
          updateItemState(filename, 'convert', { state: 'completed' }, 'in_progress');
          updateItemState(filename, 'analyze', { state: 'in_progress' }, 'in_progress');
          break;

        case 'result':
          if (event.status === 'success') {
            // mark analyze completed and result completed
            updateItemState(filename, 'analyze', { state: 'completed' }, 'completed');
            updateItemState(filename, 'result', { state: 'completed' }, 'completed');
          } else if (event.status === 'error') {
            // mark analyze completed (or leave as-is) and result error
            updateItemState(filename, 'analyze', { state: 'completed' }, 'error');
            updateItemState(filename, 'result', { state: 'error', error: event.error || 'Processing failed' }, 'error');
          }
          break;

        default:
          break;
      }
    };

    addStreamingEventListener(handlerId, onEvent);
    return () => removeStreamingEventListener(handlerId);
  }, [handlerId]);

  const list = useMemo(() => Object.values(tasks), [tasks]);

  if (list.length === 0) return null;

  return (
    <div className="space-y-3">
      {list.map((task, idx) => (
        <Task key={task.filename} defaultOpen={idx === 0}>
          <TaskTrigger title={`${task.filename} — ${statusLabel(task.status)}`} />
          <TaskContent>
            {task.items.map((item) => {
              const dim =
                item.state === 'pending'
                  ? 'text-muted-foreground'
                  : item.state === 'error'
                  ? 'text-red-700'
                  : item.state === 'completed'
                  ? 'text-green-700'
                  : '';
              return (
                <TaskItem key={item.key}>
                  <div className="flex items-center gap-2">
                    {itemIcon(item)}
                    <span className={`text-sm ${dim}`}>{item.error ? item.error : item.label}</span>
                    {item.state === 'in_progress' && (
                      <AiLoader size={14} className="text-blue-600" />
                    )}
                  </div>
                </TaskItem>
              );
            })}
          </TaskContent>
        </Task>
      ))}
    </div>
  );
}

export default ProcessingTasks;
