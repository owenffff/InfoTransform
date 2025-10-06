'use client';

import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Button } from '@/components/ui/button';

export function TooltipTest() {
  return (
    <div className="p-4">
      <h3 className="text-sm font-semibold mb-2">Tooltip Test:</h3>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="outline" size="sm">
            Hover me for tooltip
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>This is a test tooltip!</p>
        </TooltipContent>
      </Tooltip>
    </div>
  );
}