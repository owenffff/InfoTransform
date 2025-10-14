'use client';

import React from 'react';
import { Check, Clock, Sparkles, FileCheck, Wand2, Cpu } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/ui/spinner';
import { cn } from '@/lib/utils';

interface TransformationReadinessProps {
  fileCount: number;
  schemaName?: string;
  schemaSelected: boolean;
  aiModelName?: string;
  estimatedTime: string;
  onTransform: () => void;
  disabled?: boolean;
  isProcessing?: boolean;
}

export function TransformationReadiness({
  fileCount,
  schemaName,
  schemaSelected,
  aiModelName,
  estimatedTime,
  onTransform,
  disabled = false,
  isProcessing = false,
}: TransformationReadinessProps) {
  const isReady = fileCount > 0 && schemaSelected;

  return (
    <Card
      className={cn(
        "border-2 transition-all duration-300",
        isReady
          ? "border-primary/40 bg-gradient-to-br from-primary/5 via-primary/3 to-background shadow-lg"
          : "border-muted bg-muted/20"
      )}
      role="region"
      aria-label="Transformation readiness status"
    >
      {/* Screen reader announcements */}
      <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
        {isProcessing
          ? "Transformation in progress"
          : isReady
            ? `Ready to transform ${fileCount} file${fileCount > 1 ? 's' : ''} using ${schemaName}`
            : "Configure schema to continue"}
      </div>

      <CardContent className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className={cn(
              "p-2 rounded-lg",
              isReady ? "bg-primary/10" : "bg-muted"
            )}>
              <FileCheck className={cn(
                "w-5 h-5",
                isReady ? "text-primary" : "text-muted-foreground"
              )} />
            </div>
            <h3 className="text-lg font-semibold">
              {isReady ? "Ready to Transform" : "Configuration Required"}
            </h3>
          </div>
          {estimatedTime && isReady && (
            <Badge
              variant="outline"
              className="bg-green-50 border-green-200 text-green-700"
            >
              <Clock className="w-3 h-3 mr-1" />
              {estimatedTime}
            </Badge>
          )}
        </div>

        {/* Checklist */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
          {/* Files Ready */}
          <div className="flex items-start gap-3 p-3 rounded-lg bg-background/50 border">
            <div className={cn(
              "mt-0.5 flex-shrink-0",
              fileCount > 0 ? "text-green-500" : "text-muted-foreground"
            )}>
              {fileCount > 0 ? (
                <Check className="w-4 h-4" />
              ) : (
                <div className="w-4 h-4 rounded-full border-2 border-muted-foreground" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium text-muted-foreground mb-0.5">
                Files Ready
              </div>
              <div className={cn(
                "text-sm font-semibold truncate",
                fileCount > 0 ? "text-foreground" : "text-muted-foreground"
              )}>
                {fileCount > 0 ? `${fileCount} file${fileCount > 1 ? 's' : ''}` : 'No files'}
              </div>
            </div>
          </div>

          {/* Schema Selected */}
          <div className="flex items-start gap-3 p-3 rounded-lg bg-background/50 border">
            <div className={cn(
              "mt-0.5 flex-shrink-0",
              schemaSelected ? "text-green-500" : "text-muted-foreground"
            )}>
              {schemaSelected ? (
                <Check className="w-4 h-4" />
              ) : (
                <div className="w-4 h-4 rounded-full border-2 border-muted-foreground" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium text-muted-foreground mb-0.5">
                Schema Selected
              </div>
              <div className={cn(
                "text-sm font-semibold truncate",
                schemaSelected ? "text-foreground" : "text-muted-foreground"
              )}>
                {schemaName || 'Not selected'}
              </div>
            </div>
          </div>

          {/* AI Model */}
          <div className="flex items-start gap-3 p-3 rounded-lg bg-background/50 border">
            <div className={cn(
              "mt-0.5 flex-shrink-0",
              aiModelName ? "text-green-500" : "text-muted-foreground"
            )}>
              {aiModelName ? (
                <Check className="w-4 h-4" />
              ) : (
                <div className="w-4 h-4 rounded-full border-2 border-muted-foreground" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium text-muted-foreground mb-0.5">
                AI Model
              </div>
              <div className={cn(
                "text-sm font-semibold truncate",
                aiModelName ? "text-foreground" : "text-muted-foreground"
              )}>
                {aiModelName || 'Default'}
              </div>
            </div>
          </div>
        </div>

        {/* Transform Button */}
        <Button
          onClick={onTransform}
          size="lg"
          disabled={disabled || !isReady || isProcessing}
          aria-label={isProcessing ? "Transformation in progress" : !isReady ? "Select a schema to enable transformation" : "Transform files to structured data"}
          aria-busy={isProcessing}
          className={cn(
            "w-full h-12 text-base font-semibold transition-all duration-200",
            isReady && !isProcessing
              ? "bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 hover:scale-[1.02] shadow-md hover:shadow-lg"
              : "bg-muted text-muted-foreground cursor-not-allowed"
          )}
        >
          {isProcessing ? (
            <>
              <Spinner className="w-5 h-5 mr-2" />
              Initializing transformation...
            </>
          ) : !isReady ? (
            <>
              <Wand2 className="w-5 h-5 mr-2" />
              Select a schema to continue
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5 mr-2" />
              Transform to Structured Data
            </>
          )}
        </Button>

        {/* Helper Text */}
        {!isReady && (
          <p className="text-xs text-center text-muted-foreground mt-3">
            Configure your document schema in the tabs above to get started
          </p>
        )}
      </CardContent>
    </Card>
  );
}
