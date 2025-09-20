import React, { useState, useMemo } from 'react';
import { ChevronsUpDown, Search, X } from 'lucide-react';

import { cn } from '../../lib/utils';
import { Button } from '../ui/button';
import { Checkbox } from '../ui/checkbox';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';
import { Property } from '../../types/api';

interface PropertyMultiSelectProps {
  properties: Property[];
  selectedIds: number[];
  onChange: (selectedIds: number[]) => void;
  placeholder?: string;
  className?: string;
  isLoading?: boolean;
}

export const PropertyMultiSelect: React.FC<PropertyMultiSelectProps> = ({
  properties,
  selectedIds,
  onChange,
  placeholder = "Select properties...",
  className,
  isLoading = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Filter properties based on search term
  const filteredProperties = useMemo(() => {
    if (!searchTerm) return properties;
    return properties.filter(property =>
      property.property_name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [properties, searchTerm]);

  // Get display text for selected properties
  const getDisplayText = () => {
    if (selectedIds.length === 0) return placeholder;
    if (selectedIds.length === 1) {
      const property = properties.find(p => p.property_id === selectedIds[0]);
      return property?.property_name || placeholder;
    }
    return `${selectedIds.length} properties selected`;
  };

  // Handle individual property selection
  const handlePropertyToggle = (propertyId: number) => {
    const newSelectedIds = selectedIds.includes(propertyId)
      ? selectedIds.filter(id => id !== propertyId)
      : [...selectedIds, propertyId];
    onChange(newSelectedIds);
  };

  // Handle select all / deselect all
  const handleSelectAll = () => {
    if (selectedIds.length === properties.length) {
      onChange([]);
    } else {
      onChange(properties.map(p => p.property_id));
    }
  };

  // Clear all selections
  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange([]);
  };

  const isAllSelected = selectedIds.length === properties.length && properties.length > 0;
  const isPartiallySelected = selectedIds.length > 0 && selectedIds.length < properties.length;

  return (
    <div className={cn("grid gap-2", className)}>
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={isOpen}
            className={cn(
              "w-full justify-between font-normal",
              selectedIds.length === 0 && "text-muted-foreground"
            )}
            disabled={isLoading}
          >
            <span className="truncate">{getDisplayText()}</span>
            <div className="flex items-center gap-1">
              {selectedIds.length > 0 && (
                <X
                  className="h-4 w-4 opacity-50 hover:opacity-100"
                  onClick={handleClear}
                />
              )}
              <ChevronsUpDown className="h-4 w-4 shrink-0 opacity-50" />
            </div>
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-full p-0" align="start">
          <div className="p-3 space-y-3">
            {/* Search input */}
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search properties..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8"
              />
            </div>

            {/* Select All / Deselect All */}
            <div className="flex items-center space-x-2 border-b pb-2">
              <Checkbox
                id="select-all"
                checked={isAllSelected}
                ref={(el) => {
                  if (el) {
                    const input = el.querySelector('input');
                    if (input) input.indeterminate = isPartiallySelected;
                  }
                }}
                onCheckedChange={handleSelectAll}
              />
              <Label htmlFor="select-all" className="text-sm font-medium">
                {isAllSelected ? 'Deselect All' : 'Select All'}
                {properties.length > 0 && ` (${properties.length})`}
              </Label>
            </div>

            {/* Property list */}
            <div className="max-h-60 overflow-y-auto space-y-2">
              {isLoading ? (
                <div className="text-sm text-muted-foreground text-center py-4">
                  Loading properties...
                </div>
              ) : filteredProperties.length === 0 ? (
                <div className="text-sm text-muted-foreground text-center py-4">
                  {searchTerm ? 'No properties found' : 'No properties available'}
                </div>
              ) : (
                filteredProperties.map((property) => (
                  <div key={property.property_id} className="flex items-center space-x-2">
                    <Checkbox
                      id={`property-${property.property_id}`}
                      checked={selectedIds.includes(property.property_id)}
                      onCheckedChange={() => handlePropertyToggle(property.property_id)}
                    />
                    <Label
                      htmlFor={`property-${property.property_id}`}
                      className="text-sm flex-1 cursor-pointer"
                    >
                      <div className="flex justify-between items-center">
                        <span>{property.property_name}</span>
                        <span className="text-xs text-muted-foreground">
                          {property.reviews_count} reviews
                        </span>
                      </div>
                    </Label>
                  </div>
                ))
              )}
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
};