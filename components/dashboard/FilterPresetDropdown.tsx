import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

export interface FilterPreset {
  key: string;
  label: string;
}

const PRESETS: FilterPreset[] = [
  { key: 'only-acquisition', label: 'Only Acquisition' },
  { key: 'only-retargeting', label: 'Only Retargeting & Retention' },
  { key: 'active-adsets', label: 'Active Ad Sets' },
];

export interface FilterPresetDropdownProps {
  selectedPreset?: string;
  onPresetChange: (preset: string) => void;
}

const FilterPresetDropdown: React.FC<FilterPresetDropdownProps> = ({
  selectedPreset,
  onPresetChange,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const selectedPresetLabel = PRESETS.find(p => p.key === selectedPreset)?.label || 'Tải bộ lọc đã lưu';

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-2 rounded-xl bg-white border border-slate-200 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
      >
        <span>{selectedPresetLabel}</span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'transform rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-slate-200 z-50 overflow-hidden">
          {PRESETS.map((preset) => (
            <button
              key={preset.key}
              onClick={() => {
                onPresetChange(preset.key);
                setIsOpen(false);
              }}
              className={`w-full px-4 py-3 text-left text-sm hover:bg-purple-50 transition-colors flex items-center gap-2 ${
                selectedPreset === preset.key ? 'bg-purple-50 text-purple-700' : 'text-slate-700'
              }`}
            >
              <div className="w-2 h-2 rounded-full bg-purple-600"></div>
              <span>{preset.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default FilterPresetDropdown;

