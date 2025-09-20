import React, { useState } from 'react';
import { format } from 'date-fns';
import { Calendar as CalendarIcon } from 'lucide-react';
import { DateRange } from 'react-day-picker';

import { cn } from '../../lib/utils';
import { Button } from '../ui/button';
import { Calendar } from '../ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';

interface DateRangePickerProps {
  value?: DateRange;
  onChange: (range: DateRange | undefined) => void;
  placeholder?: string;
  className?: string;
}

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  value,
  onChange,
  placeholder = "Pick a date range",
  className,
}) => {
  const [startDateOpen, setStartDateOpen] = useState(false);
  const [endDateOpen, setEndDateOpen] = useState(false);

  const formatDate = (date: Date | undefined) => {
    return date ? format(date, 'MMM dd, yyyy') : 'Select date';
  };

  const handleStartDateSelect = (date: Date | undefined) => {
    if (date) {
      const newRange: DateRange = {
        from: date,
        to: value?.to || new Date() // Set end date to today if not already selected
      };
      onChange(newRange);
    }
    setStartDateOpen(false);
  };

  const handleEndDateSelect = (date: Date | undefined) => {
    if (date) {
      const newRange: DateRange = {
        from: value?.from,
        to: date
      };
      onChange(newRange);
    }
    setEndDateOpen(false);
  };

  return (
    <div className={cn("flex items-center gap-2", className)}>
      {/* Start Date Picker */}
      <Popover open={startDateOpen} onOpenChange={setStartDateOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              "justify-start text-left font-normal flex-1",
              !value?.from && "text-muted-foreground"
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {formatDate(value?.from)}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="single"
            selected={value?.from}
            onSelect={handleStartDateSelect}
            disabled={(date) => {
              const today = new Date();
              today.setHours(23, 59, 59, 999); // End of today
              return date > today || (value?.to ? date > value.to : false);
            }}
          />
        </PopoverContent>
      </Popover>

      <span className="text-muted-foreground">to</span>

      {/* End Date Picker */}
      <Popover open={endDateOpen} onOpenChange={setEndDateOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              "justify-start text-left font-normal flex-1",
              !value?.to && "text-muted-foreground"
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {formatDate(value?.to)}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="single"
            selected={value?.to}
            onSelect={handleEndDateSelect}
            disabled={(date) => {
              const today = new Date();
              today.setHours(23, 59, 59, 999); // End of today
              return date > today || (value?.from ? date < value.from : false);
            }}
          />
        </PopoverContent>
      </Popover>
    </div>
  );
};