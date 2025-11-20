import { useState, useEffect, useRef } from 'react';

interface DatePickerProps {
  dateFrom: string;
  dateTo: string;
  onDateChange: (from: string, to: string) => void;
  onClose: () => void;
}

// Helper: Get Vietnam date (UTC+7)
const getVietnamDate = (offsetDays: number = 0): Date => {
  const now = new Date();
  const vietnamTime = new Date(now.getTime() + (7 * 60 * 60 * 1000) + (offsetDays * 86400000));
  return vietnamTime;
};

// Helper: Format date to YYYY-MM-DD
const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0];
};

// Helper: Format date to DD/MM for display
const formatDateDisplay = (date: Date): string => {
  return `${date.getDate()}/${date.getMonth() + 1}`;
};

// Helper: Get first day of month
const getFirstDayOfMonth = (date: Date): Date => {
  return new Date(date.getFullYear(), date.getMonth(), 1);
};

// Helper: Get last day of month
const getLastDayOfMonth = (date: Date): Date => {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0);
};

// Helper: Get days in month
const getDaysInMonth = (date: Date): number => {
  return getLastDayOfMonth(date).getDate();
};

// Helper: Get first day of week (0 = Sunday, 1 = Monday, ...)
const getFirstDayOfWeek = (date: Date): number => {
  const firstDay = getFirstDayOfMonth(date);
  return firstDay.getDay();
};

interface DatePreset {
  label: string;
  value: string;
  getDates: () => { from: string; to: string };
}

const datePresets: DatePreset[] = [
  {
    label: 'Hôm nay',
    value: 'today',
    getDates: () => {
      const today = getVietnamDate();
      return { from: formatDate(today), to: formatDate(today) };
    },
  },
  {
    label: 'Hôm qua',
    value: 'yesterday',
    getDates: () => {
      const yesterday = getVietnamDate(-1);
      return { from: formatDate(yesterday), to: formatDate(yesterday) };
    },
  },
  {
    label: 'Hôm nay và hôm qua',
    value: 'today_yesterday',
    getDates: () => {
      const today = getVietnamDate();
      const yesterday = getVietnamDate(-1);
      return { from: formatDate(yesterday), to: formatDate(today) };
    },
  },
  {
    label: '7 ngày qua',
    value: 'last_7d',
    getDates: () => {
      const to = getVietnamDate();
      const from = getVietnamDate(-6);
      return { from: formatDate(from), to: formatDate(to) };
    },
  },
  {
    label: '14 ngày qua',
    value: 'last_14d',
    getDates: () => {
      const to = getVietnamDate();
      const from = getVietnamDate(-13);
      return { from: formatDate(from), to: formatDate(to) };
    },
  },
  {
    label: '28 ngày qua',
    value: 'last_28d',
    getDates: () => {
      const to = getVietnamDate();
      const from = getVietnamDate(-27);
      return { from: formatDate(from), to: formatDate(to) };
    },
  },
  {
    label: '30 ngày qua',
    value: 'last_30d',
    getDates: () => {
      const to = getVietnamDate();
      const from = getVietnamDate(-29);
      return { from: formatDate(from), to: formatDate(to) };
    },
  },
  {
    label: 'Tuần này',
    value: 'this_week',
    getDates: () => {
      const today = getVietnamDate();
      const dayOfWeek = today.getDay(); // 0 = Sunday, 1 = Monday, ...
      const monday = getVietnamDate(-dayOfWeek + 1); // Monday of this week
      return { from: formatDate(monday), to: formatDate(today) };
    },
  },
  {
    label: 'Tuần trước',
    value: 'last_week',
    getDates: () => {
      const today = getVietnamDate();
      const dayOfWeek = today.getDay();
      const lastMonday = getVietnamDate(-dayOfWeek - 6); // Monday of last week
      const lastSunday = getVietnamDate(-dayOfWeek); // Sunday of last week
      return { from: formatDate(lastMonday), to: formatDate(lastSunday) };
    },
  },
  {
    label: 'Tháng này',
    value: 'this_month',
    getDates: () => {
      const today = getVietnamDate();
      const firstDay = getFirstDayOfMonth(today);
      return { from: formatDate(firstDay), to: formatDate(today) };
    },
  },
  {
    label: 'Tháng trước',
    value: 'last_month',
    getDates: () => {
      const today = getVietnamDate();
      const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
      const firstDay = getFirstDayOfMonth(lastMonth);
      const lastDay = getLastDayOfMonth(lastMonth);
      return { from: formatDate(firstDay), to: formatDate(lastDay) };
    },
  },
];

export default function DatePicker({ dateFrom, dateTo, onDateChange, onClose }: DatePickerProps) {
  const [selectedPreset, setSelectedPreset] = useState<string>('');
  const [tempFrom, setTempFrom] = useState(dateFrom);
  const [tempTo, setTempTo] = useState(dateTo);
  const [currentMonth1, setCurrentMonth1] = useState(() => {
    const date = dateFrom ? new Date(dateFrom) : getVietnamDate();
    return new Date(date.getFullYear(), date.getMonth(), 1);
  });
  const [currentMonth2, setCurrentMonth2] = useState(() => {
    const date = dateFrom ? new Date(dateFrom) : getVietnamDate();
    const nextMonth = new Date(date.getFullYear(), date.getMonth() + 1, 1);
    return nextMonth;
  });
  const [selectedRange, setSelectedRange] = useState<{ from: Date | null; to: Date | null }>({
    from: dateFrom ? new Date(dateFrom) : null,
    to: dateTo ? new Date(dateTo) : null,
  });
  const pickerRef = useRef<HTMLDivElement>(null);

  // Check which preset matches current dates
  useEffect(() => {
    const matchingPreset = datePresets.find(preset => {
      const dates = preset.getDates();
      return dates.from === dateFrom && dates.to === dateTo;
    });
    if (matchingPreset) {
      setSelectedPreset(matchingPreset.value);
    } else {
      setSelectedPreset('');
    }
  }, [dateFrom, dateTo]);

  // Update temp dates when props change
  useEffect(() => {
    setTempFrom(dateFrom);
    setTempTo(dateTo);
    if (dateFrom) {
      const fromDate = new Date(dateFrom);
      setCurrentMonth1(new Date(fromDate.getFullYear(), fromDate.getMonth(), 1));
      setCurrentMonth2(new Date(fromDate.getFullYear(), fromDate.getMonth() + 1, 1));
    }
  }, [dateFrom, dateTo]);

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
        onClose();
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onClose]);

  const handlePresetClick = (preset: DatePreset) => {
    const dates = preset.getDates();
    setSelectedPreset(preset.value);
    setTempFrom(dates.from);
    setTempTo(dates.to);
    setSelectedRange({
      from: new Date(dates.from),
      to: new Date(dates.to),
    });
    onDateChange(dates.from, dates.to);
    onClose();
  };

  const handleDateClick = (date: Date) => {
    const dateStr = formatDate(date);
    if (!selectedRange.from || (selectedRange.from && selectedRange.to)) {
      // Start new selection
      setSelectedRange({ from: date, to: null });
      setTempFrom(dateStr);
      setTempTo(dateStr);
    } else {
      // Complete selection
      if (date < selectedRange.from!) {
        // If clicked date is before from, swap them
        setSelectedRange({ from: date, to: selectedRange.from });
        setTempFrom(dateStr);
        setTempTo(formatDate(selectedRange.from!));
      } else {
        setSelectedRange({ from: selectedRange.from, to: date });
        setTempTo(dateStr);
      }
    }
  };

  const handleApply = () => {
    if (tempFrom && tempTo) {
      onDateChange(tempFrom, tempTo);
      onClose();
    }
  };

  const renderCalendar = (month: Date, isFirst: boolean) => {
    const daysInMonth = getDaysInMonth(month);
    const firstDayOfWeek = getFirstDayOfWeek(month);
    const days: (Date | null)[] = [];
    
    // Add empty cells for days before month starts
    for (let i = 0; i < firstDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(month.getFullYear(), month.getMonth(), day));
    }

    const monthNames = ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6', 
                        'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'];
    const dayNames = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];

    const isDateInRange = (date: Date): boolean => {
      if (!selectedRange.from) return false;
      if (!selectedRange.to) {
        return formatDate(date) === formatDate(selectedRange.from);
      }
      return date >= selectedRange.from && date <= selectedRange.to;
    };

    const isDateSelected = (date: Date): boolean => {
      if (!selectedRange.from) return false;
      if (formatDate(date) === formatDate(selectedRange.from)) return true;
      if (selectedRange.to && formatDate(date) === formatDate(selectedRange.to)) return true;
      return false;
    };

    const isDateToday = (date: Date): boolean => {
      const today = getVietnamDate();
      return formatDate(date) === formatDate(today);
    };

    return (
      <div className="flex flex-col">
        {/* Month Header */}
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={() => {
              const prevMonth = new Date(month.getFullYear(), month.getMonth() - 1, 1);
              if (isFirst) {
                setCurrentMonth1(prevMonth);
                setCurrentMonth2(new Date(prevMonth.getFullYear(), prevMonth.getMonth() + 1, 1));
              } else {
                setCurrentMonth2(prevMonth);
              }
            }}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div className="flex items-center gap-2">
            <select
              value={month.getMonth()}
              onChange={(e) => {
                const newMonth = new Date(month.getFullYear(), parseInt(e.target.value), 1);
                if (isFirst) {
                  setCurrentMonth1(newMonth);
                  setCurrentMonth2(new Date(newMonth.getFullYear(), newMonth.getMonth() + 1, 1));
                } else {
                  setCurrentMonth2(newMonth);
                }
              }}
              className="text-sm font-medium text-gray-700 border border-gray-300 rounded px-2 py-1"
            >
              {monthNames.map((name, idx) => (
                <option key={idx} value={idx}>{name}</option>
              ))}
            </select>
            <select
              value={month.getFullYear()}
              onChange={(e) => {
                const newMonth = new Date(parseInt(e.target.value), month.getMonth(), 1);
                if (isFirst) {
                  setCurrentMonth1(newMonth);
                  setCurrentMonth2(new Date(newMonth.getFullYear(), newMonth.getMonth() + 1, 1));
                } else {
                  setCurrentMonth2(newMonth);
                }
              }}
              className="text-sm font-medium text-gray-700 border border-gray-300 rounded px-2 py-1"
            >
              {Array.from({ length: 10 }, (_, i) => month.getFullYear() - 5 + i).map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
          <button
            onClick={() => {
              const nextMonth = new Date(month.getFullYear(), month.getMonth() + 1, 1);
              if (isFirst) {
                setCurrentMonth1(nextMonth);
                setCurrentMonth2(new Date(nextMonth.getFullYear(), nextMonth.getMonth() + 1, 1));
              } else {
                setCurrentMonth2(nextMonth);
              }
            }}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        {/* Day Names */}
        <div className="grid grid-cols-7 gap-1 mb-2">
          {dayNames.map((day, idx) => (
            <div key={idx} className="text-center text-xs font-medium text-gray-500 py-1">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-1">
          {days.map((date, idx) => {
            if (!date) {
              return <div key={idx} className="aspect-square" />;
            }
            const inRange = isDateInRange(date);
            const isSelected = isDateSelected(date);
            const isToday = isDateToday(date);
            
            return (
              <button
                key={idx}
                onClick={() => handleDateClick(date)}
                className={`
                  aspect-square text-sm rounded transition-colors
                  ${isSelected 
                    ? 'bg-blue-600 text-white font-semibold' 
                    : inRange
                    ? 'bg-blue-100 text-blue-700'
                    : isToday
                    ? 'bg-blue-50 text-blue-600 font-medium'
                    : 'text-gray-700 hover:bg-gray-100'
                  }
                `}
              >
                {date.getDate()}
              </button>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <>
      <div className="fixed inset-0 z-40" onClick={onClose} />
      <div 
        ref={pickerRef}
        className="fixed z-50 bg-white rounded-lg shadow-2xl border border-gray-200 flex"
        style={{ 
          top: '50%', 
          left: '50%', 
          transform: 'translate(-50%, -50%)',
          width: '900px',
          maxHeight: '90vh',
        }}
      >
        {/* Left Sidebar - Presets */}
        <div className="w-64 border-r border-gray-200 overflow-y-auto" style={{ maxHeight: '90vh' }}>
          <div className="p-4">
            <div className="text-sm font-semibold text-gray-700 mb-3">Đã dùng mới đây</div>
            <div className="space-y-1">
              {datePresets.map((preset) => (
                <label
                  key={preset.value}
                  className="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="radio"
                    name="datePreset"
                    value={preset.value}
                    checked={selectedPreset === preset.value}
                    onChange={() => handlePresetClick(preset)}
                    className="w-4 h-4 text-blue-600"
                  />
                  <span className="text-sm text-gray-700">{preset.label}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Right Section - Calendars */}
        <div className="flex-1 p-6">
          <div className="flex gap-6 mb-4">
            {/* Calendar 1 */}
            <div className="flex-1">
              {renderCalendar(currentMonth1, true)}
            </div>
            {/* Calendar 2 */}
            <div className="flex-1">
              {renderCalendar(currentMonth2, false)}
            </div>
          </div>

          {/* Date Range Inputs */}
          <div className="border-t border-gray-200 pt-4 mt-4">
            <div className="flex items-center gap-4 mb-4">
              <input
                type="checkbox"
                id="compare"
                className="w-4 h-4 text-blue-600"
              />
              <label htmlFor="compare" className="text-sm text-gray-700">So sánh</label>
              
              <div className="flex items-center gap-2">
                <input
                  type="radio"
                  name="rangeType"
                  id="rangeType"
                  defaultChecked
                  className="w-4 h-4 text-blue-600"
                />
                <select className="text-sm border border-gray-300 rounded px-3 py-1">
                  <option>Hôm nay</option>
                </select>
                <input
                  type="text"
                  value={tempFrom ? formatDateDisplay(new Date(tempFrom)) : ''}
                  readOnly
                  placeholder="Từ ngày"
                  className="text-sm border border-gray-300 rounded px-3 py-1 w-32"
                />
                <span className="text-gray-500">-</span>
                <input
                  type="text"
                  value={tempTo ? formatDateDisplay(new Date(tempTo)) : ''}
                  readOnly
                  placeholder="Đến ngày"
                  className="text-sm border border-gray-300 rounded px-3 py-1 w-32"
                />
              </div>
            </div>

            <div className="text-xs text-gray-500 mb-4">
              Ngày hiển thị theo Giờ TP Hồ Chí Minh
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end gap-3">
              <button
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Hủy
              </button>
              <button
                onClick={handleApply}
                className="px-4 py-2 bg-blue-600 text-white rounded text-sm font-medium hover:bg-blue-700"
              >
                Cập nhật
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

