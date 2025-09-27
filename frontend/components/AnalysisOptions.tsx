'use client';

import React, { useState, useEffect } from 'react';
import { Sparkles, Settings2, Wand2, Info, Clock, Check, ChevronsUpDown, Search } from 'lucide-react';
import { useStore } from '@/lib/store';
import { transformFiles } from '@/lib/api';
import { showToast } from './Toast';
import { StreamingEvent as ProcessingStreamingEvent, dispatchStreamingEvent } from './ProcessingStatus';
import { StreamingEvent as ApiStreamingEvent } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';

export function AnalysisOptions({ onTransformStart }: { onTransformStart: () => void }) {
  const { 
    selectedFiles, 
    modelsData, 
    setStreamingResults,
    addStreamingResult,
    setModelFields,
    setIsProcessing,
    clearResults
  } = useStore();
  
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedAIModel, setSelectedAIModel] = useState('');
  const [customInstructions, setCustomInstructions] = useState('');
  const [modelDescription, setModelDescription] = useState('');
  const [schemaFields, setSchemaFields] = useState<Record<string, any>>({});
  const [activeTab, setActiveTab] = useState('model');
  const [estimatedTime, setEstimatedTime] = useState<string>('');
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (modelsData?.ai_models?.default_model) {
      setSelectedAIModel(modelsData.ai_models.default_model);
    } else if (modelsData?.ai_models?.models) {
      const firstModel = Object.keys(modelsData.ai_models.models)[0];
      if (firstModel) {
        setSelectedAIModel(firstModel);
      }
    }
  }, [modelsData]);

  useEffect(() => {
    // Estimate processing time based on file count and type
    if (selectedFiles.length > 0 && selectedModel) {
      const avgTimePerFile = 3; // seconds
      const totalSeconds = selectedFiles.length * avgTimePerFile;
      const minutes = Math.floor(totalSeconds / 60);
      const seconds = totalSeconds % 60;
      
      if (minutes > 0) {
        setEstimatedTime(`~${minutes}m ${seconds}s`);
      } else {
        setEstimatedTime(`~${seconds}s`);
      }
    } else {
      setEstimatedTime('');
    }
  }, [selectedFiles.length, selectedModel]);

  const handleModelChange = (modelKey: string) => {
    setSelectedModel(modelKey);
    if (modelKey && modelsData?.models[modelKey]) {
      const model = modelsData.models[modelKey];
      setModelDescription(model.description);
      
      // Store full field information for tooltips
      if (typeof model.fields === 'object' && !Array.isArray(model.fields)) {
        setSchemaFields(model.fields);
        setModelFields(Object.keys(model.fields));
      } else if (Array.isArray(model.fields)) {
        // If fields is an array, create a simple object
        const fieldsObj: Record<string, any> = {};
        model.fields.forEach(field => {
          fieldsObj[field] = { type: 'string', description: `Extract ${field} information` };
        });
        setSchemaFields(fieldsObj);
        setModelFields(model.fields);
      } else {
        setSchemaFields({});
        setModelFields([]);
      }
    } else {
      setModelDescription('');
      setSchemaFields({});
      setModelFields([]);
    }
    setOpen(false);
  };

  const handleTransform = async () => {
    if (!selectedModel) {
      showToast('error', 'Please select an analysis model');
      return;
    }

    // Reset ProcessingStatus state before starting new processing
    dispatchStreamingEvent({ type: 'reset' });
    
    clearResults();
    setIsProcessing(true);
    onTransformStart();

    const handleEvent = (event: ApiStreamingEvent) => {
      // Convert API event to Processing event
      const processingEvent: ProcessingStreamingEvent = {
        type: event.type === 'phase_start' && event.phase === 'markdown_conversion' ? 'markdown_conversion' :
              event.type === 'phase_start' && event.phase === 'ai_analysis' ? 'ai_analysis' :
              event.type === 'init' ? 'start' :
              event.type === 'result' ? 'result' :
              event.type === 'complete' ? 'complete' :
              event.type === 'error' ? 'error' : 'result',
        filename: event.filename || event.file,
        status: event.status === 'success' ? 'success' : 
                event.status === 'error' ? 'error' : 'processing',
        error: event.error,
        progress: event.progress,
        total: event.total || event.total_files,
        markdown_content: event.markdown_content,
        structured_data: event.structured_data,
        model_fields: event.model_fields,
        processing_time: event.processing_time,
        was_summarized: event.was_summarized,
        summarization_metrics: event.summarization_metrics,
        summary: event.summary ? {
          total_files: event.summary.total_files,
          successful_files: event.summary.successful_files,
          failed_files: event.summary.failed_files,
          total_time: 0
        } : undefined
      };
      
      dispatchStreamingEvent(processingEvent);
      
      // Persist both successful and failed results so totals/failed counts are accurate
      const fname = event.filename || event.file;
      if (event.type === 'result' && fname) {
        if (event.status === 'success' && event.structured_data) {
          addStreamingResult({
            filename: fname,
            status: 'success',
            markdown_content: event.markdown_content,
            structured_data: event.structured_data,
            model_fields: event.model_fields,
            processing_time: event.processing_time,
            was_summarized: event.was_summarized,
            summarization_metrics: event.summarization_metrics
          });
        } else if (event.status === 'error') {
          addStreamingResult({
            filename: fname,
            status: 'error',
            error: event.error || 'Processing failed',
            markdown_content: event.markdown_content
          });
        }
      }
      if (event.type === 'complete') {
        setIsProcessing(false);
        if (event.summary) {
          if (event.summary.successful_files > 0) {
            showToast('success', `Successfully processed ${event.summary.successful_files} file(s)`);
          }
          if (event.summary.failed_files > 0) {
            showToast('error', `Failed to process ${event.summary.failed_files} file(s)`);
          }
        }
      }
      if (event.type === 'error') {
        showToast('error', event.error || 'An error occurred');
      }
    };

    const handleError = (error: string) => {
      setIsProcessing(false);
      showToast('error', error);
    };

    await transformFiles(
      selectedFiles,
      selectedModel,
      customInstructions,
      selectedAIModel,
      handleEvent,
      handleError
    );
  };

  const getFieldInfo = (fieldName: string) => {
    const field = schemaFields[fieldName];
    if (!field) return { type: 'string', description: `Extract ${fieldName}` };
    
    if (typeof field === 'object') {
      return {
        type: field.type || field.data_type || 'string',
        description: field.description || field.help_text || `Extract ${fieldName} information`
      };
    }
    
    return { type: 'string', description: `Extract ${fieldName}` };
  };

  if (!selectedFiles.length) return null;

  return (
    <Card className="shadow-lg border-gray-200">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          <span className="text-primary">2.</span>
          Configure Extraction
          {estimatedTime && (
            <Badge variant="outline" className="ml-auto">
              <Clock className="w-3 h-3 mr-1" />
              Est. {estimatedTime}
            </Badge>
          )}
        </CardTitle>
        <CardDescription>
          Choose an analysis model and configure AI settings for data extraction
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="model" className="flex items-center gap-2">
              <Wand2 className="w-4 h-4" />
              Analysis Model
            </TabsTrigger>
            <TabsTrigger value="ai" className="flex items-center gap-2">
              <Settings2 className="w-4 h-4" />
              AI Settings
            </TabsTrigger>
            <TabsTrigger value="advanced" className="flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              Advanced
            </TabsTrigger>
          </TabsList>

          <TabsContent value="model" className="mt-6 space-y-4">
            <div>
              <Label htmlFor="modelSelect" className="text-sm font-semibold mb-2 block">
                Select Analysis Model
              </Label>
              
              {/* Searchable Dropdown using Command */}
              <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    role="combobox"
                    aria-expanded={open}
                    className="w-full justify-between font-normal"
                  >
                    {selectedModel
                      ? modelsData?.models[selectedModel]?.name
                      : "Search and select an analysis model..."}
                    <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0" align="start">
                  <Command>
                    <CommandInput placeholder="Search models..." className="h-9" />
                    <CommandEmpty>No model found.</CommandEmpty>
                    <CommandGroup>
                      <ScrollArea className="h-72">
                        {modelsData?.models && Object.entries(modelsData.models).map(([key, model]) => (
                          <CommandItem
                            key={key}
                            value={model.name}
                            onSelect={() => handleModelChange(key)}
                          >
                            <Check
                              className={cn(
                                "mr-2 h-4 w-4",
                                selectedModel === key ? "opacity-100" : "opacity-0"
                              )}
                            />
                            <div className="flex-1">
                              <div className="font-medium">{model.name}</div>
                              <div className="text-xs text-muted-foreground line-clamp-1">
                                {model.description}
                              </div>
                            </div>
                          </CommandItem>
                        ))}
                      </ScrollArea>
                    </CommandGroup>
                  </Command>
                </PopoverContent>
              </Popover>
            </div>

            {modelDescription && (
              <Alert className="border-primary/20 bg-primary/5">
                <Info className="h-4 w-4 text-primary" />
                <AlertDescription className="text-sm">
                  {modelDescription}
                </AlertDescription>
              </Alert>
            )}

            {Object.keys(schemaFields).length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Label className="text-sm font-semibold">Schema Fields</Label>
                  <Badge variant="secondary" className="text-xs">
                    {Object.keys(schemaFields).length} fields
                  </Badge>
                </div>
                <ScrollArea className="h-32 w-full rounded-lg border bg-muted/20 p-3">
                  <div className="flex flex-wrap gap-2">
                    {Object.keys(schemaFields).map((fieldName) => {
                      const fieldInfo = getFieldInfo(fieldName);
                      return (
                        <TooltipProvider key={fieldName}>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Badge
                                variant="outline"
                                className="cursor-help border-primary/30 bg-primary/10 text-primary hover:bg-primary/20"
                              >
                                {fieldName}
                              </Badge>
                            </TooltipTrigger>
                            <TooltipContent className="max-w-xs">
                              <div className="space-y-1">
                                <p className="font-semibold text-xs">Field: {fieldName}</p>
                                <p className="text-xs">
                                  <span className="font-medium">Type:</span> {fieldInfo.type}
                                </p>
                                <p className="text-xs">
                                  <span className="font-medium">Description:</span> {fieldInfo.description}
                                </p>
                              </div>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                      );
                    })}
                  </div>
                </ScrollArea>
              </div>
            )}
          </TabsContent>

          <TabsContent value="ai" className="mt-6 space-y-4">
            <div>
              <Label htmlFor="aiModelSelect" className="text-sm font-semibold mb-2 block">
                AI Model
              </Label>
              <Select value={selectedAIModel} onValueChange={setSelectedAIModel}>
                <SelectTrigger id="aiModelSelect" className="w-full">
                  <SelectValue placeholder="Select AI model..." />
                </SelectTrigger>
                <SelectContent>
                  {modelsData?.ai_models?.models && Object.entries(modelsData.ai_models.models).map(([key, model]) => (
                    <SelectItem key={key} value={key}>
                      <div className="flex items-center justify-between w-full">
                        <span>{model.display_name || key}</span>
                        {key === modelsData.ai_models.default_model && (
                          <Badge variant="secondary" className="ml-2 text-xs">
                            Default
                          </Badge>
                        )}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground mt-2">
                Choose the AI model for processing. GPT-4o recommended for best results.
              </p>
            </div>

            {selectedAIModel && modelsData?.ai_models?.models[selectedAIModel] && (
              <Alert className="border-blue-200 bg-blue-50">
                <Info className="h-4 w-4 text-blue-600" />
                <AlertDescription className="text-sm">
                  <strong>Model Info:</strong> {`Using ${modelsData.ai_models.models[selectedAIModel].display_name} for analysis`}
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>

          <TabsContent value="advanced" className="mt-6 space-y-4">
            <div>
              <Label htmlFor="customInstructions" className="text-sm font-semibold mb-2 block">
                Custom Instructions
                <span className="font-normal text-muted-foreground ml-2">(Optional)</span>
              </Label>
              <Textarea
                id="customInstructions"
                rows={6}
                value={customInstructions}
                onChange={(e) => setCustomInstructions(e.target.value)}
                className="resize-none"
                placeholder="Add specific instructions for the AI analysis...

Examples:
• Focus on financial data and monetary values
• Extract dates in YYYY-MM-DD format
• Include confidence scores for each extracted field
• Prioritize accuracy over completeness"
              />
              <p className="text-xs text-muted-foreground mt-2">
                Provide additional context or specific requirements for the analysis
              </p>
            </div>

            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription className="text-sm">
                <strong>Batch Processing:</strong> Files will be processed in batches of 5 for optimal performance.
                Large files may be automatically summarized to fit context limits.
              </AlertDescription>
            </Alert>
          </TabsContent>
        </Tabs>

        <Separator className="my-6" />

        <div className="flex justify-between items-center">
          <div className="text-sm text-muted-foreground">
            Ready to process {selectedFiles.length} file{selectedFiles.length > 1 ? 's' : ''}
          </div>
          
          <Button
            onClick={handleTransform}
            size="lg"
            className="bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70"
            disabled={!selectedModel}
          >
            <Sparkles className="w-5 h-5 mr-2" />
            Transform to Structured Data
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
