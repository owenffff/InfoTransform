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
  TooltipTrigger,
} from '@/components/ui/tooltip';
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
      showToast('error', 'Please select an document schema');
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
        type: event.type === 'init' ? 'start' :
              event.type === 'phase' && event.phase === 'markdown_conversion' && event.status === 'started' ? 'markdown_conversion' :
              event.type === 'phase' && event.phase === 'ai_processing' && event.status === 'started' ? 'ai_analysis' :
              event.type === 'conversion_progress' ? 'markdown_conversion' :
              event.type === 'result' ? 'result' :
              event.type === 'complete' ? 'complete' :
              event.type === 'error' ? 'error' : 'result',
        filename: event.filename || event.file,
        status: event.status === 'success' ? 'success' :
                event.status === 'error' ? 'error' : 'processing',
        error: event.error,
        progress: event.progress !== undefined ? event.progress : event.current,
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
            summarization_metrics: event.summarization_metrics,
            is_primary_result: event.is_primary_result,
            source_file: event.source_file
          });
        } else if (event.status === 'error') {
          addStreamingResult({
            filename: fname,
            status: 'error',
            error: event.error || 'Processing failed',
            markdown_content: event.markdown_content,
            is_primary_result: event.is_primary_result,
            source_file: event.source_file
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

  const formatPythonType = (pythonType: string): string => {
    // Clean up <class 'type'> format first
    let cleanType = pythonType.replace(/<class '(.+?)'>/, '$1');
    
    // Convert Python type annotations to user-friendly format
    const typeMap: Record<string, string> = {
      'str': 'Text',
      'int': 'Number (Integer)',
      'float': 'Number (Decimal)',
      'bool': 'Yes/No',
      'datetime.datetime': 'Date & Time',
      'datetime': 'Date & Time',
      'date': 'Date',
      'dict': 'Object',
      'Any': 'Any type',
    };
    
    // Handle Optional types - extract inner type without adding "(Optional)" suffix
    // since we have a dedicated "Required" field in the tooltip
    if (cleanType.includes('Optional[')) {
      const innerType = cleanType.match(/Optional\[(.+)\]/)?.[1] || cleanType;
      return formatPythonType(innerType);
    }
    
    // Handle Union types
    if (cleanType.includes('Union[')) {
      const types = cleanType.match(/Union\[(.+)\]/)?.[1]?.split(',').map(t => t.trim()) || [];
      return types.map(t => formatPythonType(t)).join(' or ');
    }
    
    // Handle List types
    if (cleanType.includes('List[') || cleanType.includes('list[')) {
      const innerType = cleanType.match(/[Ll]ist\[(.+)\]/)?.[1] || 'items';
      return `List of ${formatPythonType(innerType)}`;
    }
    
    // Handle Dict types
    if (cleanType.includes('Dict[') || cleanType.includes('dict[')) {
      const match = cleanType.match(/[Dd]ict\[(.+?),\s*(.+)\]/);
      if (match) {
        return `Dictionary (${formatPythonType(match[1])} → ${formatPythonType(match[2])})`;
      }
      return 'Dictionary';
    }
    
    // Check if it's a basic type we know
    for (const [pyType, friendlyType] of Object.entries(typeMap)) {
      if (cleanType === pyType || cleanType.endsWith('.' + pyType)) {
        return friendlyType;
      }
    }
    
    // Clean up any remaining typing module prefixes and config module paths
    cleanType = cleanType.replace(/typing\./gi, '');
    cleanType = cleanType.replace(/config\.analysis_schemas\./gi, '');
    
    // If it's still a complex type, just return the cleaned version
    return cleanType;
  };

  const getFieldInfo = (fieldName: string) => {
    const field = schemaFields[fieldName];
    if (!field) return {
      type: 'Text',
      description: `Extract ${fieldName}`,
      required: false,
      constraints: null
    };

    if (typeof field === 'object') {
      const rawType = field.type || field.data_type || 'str';
      // Check if type contains Optional - if so, treat as not required
      const isOptional = rawType.includes('Optional[');

      return {
        type: formatPythonType(rawType),
        description: field.description || field.help_text || `Extract ${fieldName} information`,
        // If type is Optional, always set required to false regardless of backend value
        required: isOptional ? false : (field.required !== undefined ? field.required : false),
        constraints: field.constraints || null
      };
    }

    return {
      type: 'Text',
      description: `Extract ${fieldName}`,
      required: false,
      constraints: null
    };
  };

  if (!selectedFiles.length) return null;

  return (
    <Card className="shadow-lg border-gray-200">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          Configure Extraction
          {estimatedTime && (
            <Badge variant="outline" className="ml-auto">
              <Clock className="w-3 h-3 mr-1" />
              Est. {estimatedTime}
            </Badge>
          )}
        </CardTitle>
        <CardDescription>
          Choose a document schema and configure AI settings for data extraction
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="model" className="flex items-center gap-2">
              <Wand2 className="w-4 h-4" />
              Document Schema
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
                Select Document Schema
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
                      : "Search and select an document schema..."}
                    <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0" align="start">
                  <Command>
                    <CommandInput placeholder="Search models..." className="h-9" />
                    <CommandEmpty>No model found.</CommandEmpty>
                    <CommandGroup className="max-h-72 overflow-y-auto">
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
                <div className="h-32 w-full rounded-lg border bg-muted/20 p-3 overflow-y-auto custom-scrollbar">
                  <div className="flex flex-wrap gap-2">
                      {Object.keys(schemaFields).map((fieldName) => {
                        const fieldInfo = getFieldInfo(fieldName);
                        return (
                          <Tooltip key={fieldName}>
                            <TooltipTrigger asChild>
                              <Badge
                                variant="outline"
                                className="cursor-help border-primary/30 bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                              >
                                {fieldName}
                                {fieldInfo.required && (
                                  <span className="ml-1 text-red-500">*</span>
                                )}
                              </Badge>
                            </TooltipTrigger>
                            <TooltipContent>
                              <div className="space-y-2">
                                <div className="border-b pb-1">
                                  <p className="font-semibold text-sm">{fieldName}</p>
                                </div>
                                
                                <div className="space-y-1.5">
                                  <div className="flex items-start gap-2">
                                    <span className="font-medium text-xs min-w-[60px]">Type:</span>
                                    <span className="text-xs font-mono bg-muted px-1.5 py-0.5 rounded">
                                      {fieldInfo.type}
                                    </span>
                                  </div>
                                  
                                  {fieldInfo.description && (
                                    <div className="flex items-start gap-2">
                                      <span className="font-medium text-xs min-w-[60px]">About:</span>
                                      <span className="text-xs leading-relaxed">
                                        {fieldInfo.description}
                                      </span>
                                    </div>
                                  )}
                                  
                                  <div className="flex items-start gap-2">
                                    <span className="font-medium text-xs min-w-[60px]">Required:</span>
                                    <span className={`text-xs font-medium ${fieldInfo.required ? 'text-red-500' : 'text-green-500'}`}>
                                      {fieldInfo.required ? 'Yes' : 'No (Optional)'}
                                    </span>
                                  </div>
                                  
                                  {fieldInfo.constraints && (
                                    <div className="flex items-start gap-2">
                                      <span className="font-medium text-xs min-w-[60px]">Limits:</span>
                                      <span className="text-xs">
                                        {fieldInfo.constraints}
                                      </span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </TooltipContent>
                          </Tooltip>
                        );
                      })}
                  </div>
                </div>
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
                Choose the AI model for processing.
              </p>
            </div>
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
