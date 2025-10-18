/**
 * Schema Complexity Analyzer
 *
 * Analyzes data schemas to determine optimal UI presentation mode
 * for the document review workspace.
 */

export type FieldType =
  | 'short'      // < 50 chars: single-line input
  | 'medium'     // 50-200 chars: single-line input
  | 'long'       // > 200 chars: textarea
  | 'enum'       // Literal types: select/radio
  | 'date'       // Date fields
  | 'boolean'    // Checkbox
  | 'number'     // Number input
  | 'nested';    // Arrays/objects

export interface FieldMetadata {
  name: string;
  type: FieldType;
  label: string;           // Human-readable label
  maxLength?: number;      // Expected max length (for text fields)
  isRequired: boolean;
  enumValues?: string[];   // For enum types
  isArray: boolean;        // Is this field an array?
  nestedSchema?: FieldMetadata[];  // For nested objects/arrays
  description?: string;    // Field description/tooltip
}

export type ComplexityLevel = 'simple' | 'moderate' | 'complex';
export type ViewMode = 'table' | 'table-drawer' | 'master-detail';

export interface SchemaComplexity {
  level: ComplexityLevel;
  score: number;
  fieldCount: number;
  longTextFields: number;
  nestedFields: number;
  recommendedView: ViewMode;
  fieldMetadata: FieldMetadata[];
}

/**
 * Infer field type from field name, sample data, and schema hints
 */
function inferFieldType(
  fieldName: string,
  sampleValue: any,
  fieldSchema?: any
): FieldType {
  // Check for nested structures first
  if (Array.isArray(sampleValue) || fieldSchema?.type === 'array') {
    return 'nested';
  }

  if (typeof sampleValue === 'object' && sampleValue !== null) {
    return 'nested';
  }

  // Boolean fields
  if (typeof sampleValue === 'boolean' || fieldSchema?.type === 'boolean') {
    return 'boolean';
  }

  // Number fields
  if (typeof sampleValue === 'number' || fieldSchema?.type === 'number') {
    return 'number';
  }

  // Date fields (check field name patterns)
  const datePatterns = /date|time|timestamp|created|updated|modified|_at$/i;
  if (datePatterns.test(fieldName)) {
    return 'date';
  }

  // Enum fields (check for literal types in schema)
  if (fieldSchema?.enum || fieldSchema?.type === 'enum') {
    return 'enum';
  }

  // String fields - determine length category
  if (typeof sampleValue === 'string') {
    const length = sampleValue.length;

    // Check field name for known long-text patterns
    const longTextPatterns = /description|summary|details|notes|comment|content|statement|text|body/i;
    if (longTextPatterns.test(fieldName) || length > 200) {
      return 'long';
    }

    if (length > 50) {
      return 'medium';
    }

    return 'short';
  }

  // Default to short text
  return 'short';
}

/**
 * Convert field name to human-readable label
 * Examples:
 *   root_cause_category -> Root Cause Category
 *   isActive -> Is Active
 *   createdAt -> Created At
 */
function fieldNameToLabel(fieldName: string): string {
  return fieldName
    // Handle camelCase
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    // Handle snake_case
    .replace(/_/g, ' ')
    // Capitalize first letter of each word
    .replace(/\b\w/g, char => char.toUpperCase())
    .trim();
}

/**
 * Analyze nested object/array schema
 */
function analyzeNestedField(
  fieldName: string,
  sampleValue: any,
  fieldSchema?: any
): FieldMetadata {
  const isArray = Array.isArray(sampleValue);
  const sampleItem = isArray ? sampleValue[0] : sampleValue;

  let nestedSchema: FieldMetadata[] | undefined;

  if (sampleItem && typeof sampleItem === 'object') {
    nestedSchema = Object.keys(sampleItem).map(key =>
      analyzeField(key, sampleItem[key])
    );
  }

  return {
    name: fieldName,
    type: 'nested',
    label: fieldNameToLabel(fieldName),
    isRequired: false,
    isArray,
    nestedSchema,
  };
}

/**
 * Analyze individual field
 */
function analyzeField(
  fieldName: string,
  sampleValue: any,
  fieldSchema?: any
): FieldMetadata {
  const type = inferFieldType(fieldName, sampleValue, fieldSchema);

  // Handle nested fields specially
  if (type === 'nested') {
    return analyzeNestedField(fieldName, sampleValue, fieldSchema);
  }

  const metadata: FieldMetadata = {
    name: fieldName,
    type,
    label: fieldNameToLabel(fieldName),
    isRequired: false, // Would need schema to determine this
    isArray: false,
  };

  // Add type-specific metadata
  if (type === 'enum' && fieldSchema?.enum) {
    metadata.enumValues = fieldSchema.enum;
  }

  if (type === 'long' && typeof sampleValue === 'string') {
    metadata.maxLength = Math.max(sampleValue.length, 500);
  }

  return metadata;
}

/**
 * Calculate complexity score
 *
 * Scoring rubric:
 * - Base: 1 point per field
 * - Long text fields: +3 points (harder to display in tables)
 * - Nested fields: +4 points (require special UI)
 * - Many records: +2 points (if > 10 records)
 */
function calculateComplexityScore(
  fieldMetadata: FieldMetadata[],
  recordCount: number
): number {
  let score = 0;

  fieldMetadata.forEach(field => {
    score += 1; // Base score per field

    if (field.type === 'long') {
      score += 3;
    }

    if (field.type === 'nested') {
      score += 4;

      // Recursively score nested fields
      if (field.nestedSchema) {
        score += calculateComplexityScore(field.nestedSchema, 1);
      }
    }
  });

  // Add penalty for large record counts
  if (recordCount > 10) {
    score += 2;
  }

  return score;
}

/**
 * Determine complexity level from score
 */
function scoreToComplexity(score: number): ComplexityLevel {
  if (score <= 8) return 'simple';
  if (score <= 20) return 'moderate';
  return 'complex';
}

/**
 * Recommend view mode based on complexity
 */
function recommendViewMode(
  complexity: ComplexityLevel,
  fieldCount: number,
  nestedFieldCount: number
): ViewMode {
  // Simple schemas: compact table
  if (complexity === 'simple') {
    return 'table';
  }

  // Moderate complexity: table with drawer for details
  if (complexity === 'moderate') {
    return 'table-drawer';
  }

  // Complex schemas: master-detail split view
  // Also use master-detail if there are any nested fields
  if (complexity === 'complex' || nestedFieldCount > 0) {
    return 'master-detail';
  }

  return 'table-drawer';
}

/**
 * Main analysis function
 *
 * @param data - Sample data (single record or array of records)
 * @param schema - Optional schema definition (Pydantic-like structure)
 * @returns Schema complexity analysis
 */
export function analyzeSchema(
  data: any,
  schema?: any
): SchemaComplexity {
  // Handle single record vs array of records
  const isMultiRecord = Array.isArray(data);
  const sampleRecord = isMultiRecord ? data[0] : data;
  const recordCount = isMultiRecord ? data.length : 1;

  if (!sampleRecord || typeof sampleRecord !== 'object') {
    // No data to analyze - return minimal complexity
    return {
      level: 'simple',
      score: 0,
      fieldCount: 0,
      longTextFields: 0,
      nestedFields: 0,
      recommendedView: 'table',
      fieldMetadata: [],
    };
  }

  // Analyze each field
  const fieldMetadata = Object.keys(sampleRecord).map(fieldName =>
    analyzeField(fieldName, sampleRecord[fieldName], schema?.[fieldName])
  );

  // Count field types
  const fieldCount = fieldMetadata.length;
  const longTextFields = fieldMetadata.filter(f => f.type === 'long').length;
  const nestedFields = fieldMetadata.filter(f => f.type === 'nested').length;

  // Calculate complexity
  const score = calculateComplexityScore(fieldMetadata, recordCount);
  const level = scoreToComplexity(score);
  const recommendedView = recommendViewMode(level, fieldCount, nestedFields);

  return {
    level,
    score,
    fieldCount,
    longTextFields,
    nestedFields,
    recommendedView,
    fieldMetadata,
  };
}

/**
 * Utility: Check if schema should use multi-record view
 */
export function isMultiRecordSchema(data: any): boolean {
  return Array.isArray(data) && data.length > 1;
}

/**
 * Utility: Get primary identifier field (best guess)
 * Looks for common ID/reference field names
 */
export function getPrimaryIdentifier(fieldMetadata: FieldMetadata[]): string | null {
  const idPatterns = ['id', 'reference', 'ref', 'code', 'number', 'key'];

  for (const pattern of idPatterns) {
    const field = fieldMetadata.find(f =>
      f.name.toLowerCase().includes(pattern)
    );
    if (field) return field.name;
  }

  // Fallback: use first short text field
  const firstShort = fieldMetadata.find(f => f.type === 'short');
  return firstShort?.name || fieldMetadata[0]?.name || null;
}

/**
 * Utility: Get title field (best guess)
 * Looks for common title/name field patterns
 */
export function getTitleField(fieldMetadata: FieldMetadata[]): string | null {
  const titlePatterns = ['title', 'name', 'subject', 'heading', 'label'];

  for (const pattern of titlePatterns) {
    const field = fieldMetadata.find(f =>
      f.name.toLowerCase().includes(pattern)
    );
    if (field) return field.name;
  }

  // Fallback: use second short/medium text field
  const textFields = fieldMetadata.filter(f =>
    f.type === 'short' || f.type === 'medium'
  );
  return textFields[1]?.name || textFields[0]?.name || null;
}
