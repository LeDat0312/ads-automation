import React, { useState, useRef, useEffect } from 'react';
import { ChevronLeft, ChevronRight, X } from 'lucide-react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, startOfWeek, endOfWeek } from 'date-fns';

export interface DateRange {
  from: Date;
  to: Date;
}

export interface DateRangePickerPopoverProps {
  value: DateRange;
  onChange: (range: DateRange) => void;
  children: React.ReactElement;
}

const QUICK_RANGES = [
  { key: 'today', label: 'Hôm nay' },
  { key: 'yesterday', label: 'Hôm qua' },
  { key: 'last3days', label: '3 ngày qua' },
  { key: 'last7days', label: '7 ngày qua' },
  { key: 'last14days', label: '14 ngày qua' },
  { key: 'last30days', label: '30 ngày qua' },
];

const DateRangePickerPopover: React.FC<DateRangePickerPopoverProps> = ({
  value,
  onChange,
  children,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(value.from);
  const [selectedRange, setSelectedRange] = useState<{ start: Date | null; end: Date | null }>({
    start: value.from,
    end: value.to,
  });
  const [tempRange, setTempRange] = useState<{ start: Date | null; end: Date | null }>({
    start: value.from,
    end: value.to,
  });
  const popoverRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(event.target as Node)) {
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

  useEffect(() => {
    setTempRange({ start: value.from, end: value.to });
    setSelectedRange({ start: value.from, end: value.to });
  }, [value]);

  const handleQuickRange = (key: string) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    let start: Date;
    let end: Date = new Date(today);
    end.setHours(23, 59, 59, 999);

    switch (key) {
      case 'today':
        start = new Date(today);
        break;
      case 'yesterday':
        start = new Date(today);
        start.setDate(start.getDate() - 1);
        end = new Date(start);
        end.setHours(23, 59, 59, 999);
        break;
      case 'last3days':
        start = new Date(today);
        start.setDate(start.getDate() - 2);
        break;
      case 'last7days':
        start = new Date(today);
        start.setDate(start.getDate() - 6);
        break;
      case 'last14days':
        start = new Date(today);
        start.setDate(start.getDate() - 13);
        break;
      case 'last30days':
        start = new Date(today);
        start.setDate(start.getDate() - 29);
        break;
      default:
        return;
    }

    setTempRange({ start, end });
    setSelectedRange({ start, end });
  };

  const handleDateClick = (date: Date) => {
    if (!tempRange.start || (tempRange.start && tempRange.end)) {
      setTempRange({ start: date, end: null });
      setSelectedRange({ start: date, end: null });
    } else {
      const start = tempRange.start;
      const end = date;
      if (end < start) {
        setTempRange({ start: end, end: start });
        setSelectedRange({ start: end, end: start });
      } else {
        setTempRange({ start, end });
        setSelectedRange({ start, end });
      }
    }
  };

  const handleUpdate = () => {
    if (selectedRange.start && selectedRange.end) {
      onChange({
        from: selectedRange.start,
        to: selectedRange.end,
      });
      setIsOpen(false);
    }
  };

  const handleCancel = () => {
    setTempRange({ start: value.from, end: value.to });
    setSelectedRange({ start: value.from, end: value.to });
    setIsOpen(false);
  };

  const renderCalendar = (month: Date) => {
    const monthStart = startOfMonth(month);
    const monthEnd = endOfMonth(month);
    const calendarStart = startOfWeek(monthStart, { weekStartsOn: 0 });
    const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 0 });
    const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

    const isInRange = (date: Date) => {
      if (!selectedRange.start || !selectedRange.end) return false;
      return date >= selectedRange.start && date <= selectedRange.end;
    };

    const isRangeStart = (date: Date) => {
      return selectedRange.start && isSameDay(date, selectedRange.start);
    };

    const isRangeEnd = (date: Date) => {
      return selectedRange.end && isSameDay(date, selectedRange.end);
    };

    return (
      <div className="w-full">
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
            className="p-1 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-slate-600" />
          </button>
          <div className="flex items-center gap-2">
            <select
              value={month.getMonth()}
              onChange={(e) => setCurrentMonth(new Date(month.getFullYear(), parseInt(e.target.value), 1))}
              className="px-2 py-1 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {Array.from({ length: 12 }, (_, i) => (
                <option key={i} value={i}>
                  Tháng {i + 1}
                </option>
              ))}
            </select>
            <select
              value={month.getFullYear()}
              onChange={(e) => setCurrentMonth(new Date(parseInt(e.target.value), month.getMonth(), 1))}
              className="px-2 py-1 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {Array.from({ length: 10 }, (_, i) => month.getFullYear() - 5 + i).map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
            className="p-1 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <ChevronRight className="w-5 h-5 text-slate-600" />
          </button>
        </div>

        <div className="grid grid-cols-7 gap-1 mb-2">
          {['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'].map((day) => (
            <div key={day} className="text-center text-xs font-medium text-slate-500 py-2">
              {day}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7 gap-1">
          {days.map((day) => {
            const isCurrentMonth = isSameMonth(day, month);
            const inRange = isInRange(day);
            const isStart = isRangeStart(day);
            const isEnd = isRangeEnd(day);

            return (
              <button
                key={day.toString()}
                onClick={() => handleDateClick(day)}
                className={`
                  h-9 text-sm rounded-lg transition-colors
                  ${!isCurrentMonth ? 'text-slate-300' : 'text-slate-700'}
                  ${inRange ? 'bg-purple-100' : ''}
                  ${isStart || isEnd ? 'bg-purple-600 text-white font-semibold' : ''}
                  ${isCurrentMonth && !inRange && !isStart && !isEnd ? 'hover:bg-purple-50' : ''}
                `}
              >
                {format(day, 'd')}
              </button>
            );
          })}
        </div>
      </div>
    );
  };

  const formatDateInput = (date: Date | null) => {
    if (!date) return '';
    return format(date, 'MM/dd/yyyy');
  };

  return (
    <div className="relative" ref={popoverRef}>
      {React.cloneElement(children, {
        onClick: () => setIsOpen(!isOpen),
      })}

      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-[800px] bg-white rounded-2xl shadow-xl border border-slate-100 z-50 overflow-hidden">
          <div className="flex">
            {/* Calendars */}
            <div className="flex-1 p-6">
              <div className="flex gap-6">
                <div className="flex-1">
                  {renderCalendar(currentMonth)}
                </div>
                <div className="flex-1">
                  {renderCalendar(addMonths(currentMonth, 1))}
                </div>
              </div>

              {/* Date Inputs */}
              <div className="mt-6 pt-6 border-t border-slate-200">
                <div className="flex items-center gap-4 mb-2">
                  <div className="flex-1">
                    <label className="block text-xs text-slate-500 mb-1">Từ:</label>
                    <div className="relative">
                      <input
                        type="text"
                        value={formatDateInput(selectedRange.start)}
                        readOnly
                        className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                      {selectedRange.start && (
                        <button
                          onClick={() => setSelectedRange({ ...selectedRange, start: null })}
                          className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 hover:bg-slate-100 rounded"
                        >
                          <X className="w-3 h-3 text-slate-400" />
                        </button>
                      )}
                    </div>
                  </div>
                  <div className="flex-1">
                    <label className="block text-xs text-slate-500 mb-1">Đến:</label>
                    <div className="relative">
                      <input
                        type="text"
                        value={formatDateInput(selectedRange.end)}
                        readOnly
                        className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                      {selectedRange.end && (
                        <button
                          onClick={() => setSelectedRange({ ...selectedRange, end: null })}
                          className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 hover:bg-slate-100 rounded"
                        >
                          <X className="w-3 h-3 text-slate-400" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
                <p className="text-xs text-slate-500">Múi giờ tài khoản: Asia/Ho_Chi_Minh</p>
              </div>
            </div>

            {/* Quick Ranges */}
            <div className="w-48 border-l border-slate-200 p-4 overflow-y-auto max-h-[500px]">
              <h3 className="text-sm font-semibold text-slate-700 mb-3">Khoảng thời gian</h3>
              <div className="space-y-1">
                {QUICK_RANGES.map((range) => {
                  const isSelected = 
                    (range.key === 'today' && selectedRange.start && isSameDay(selectedRange.start, new Date()) && selectedRange.end && isSameDay(selectedRange.end, new Date())) ||
                    (range.key === 'yesterday' && selectedRange.start && selectedRange.end && 
                     isSameDay(selectedRange.start, (() => { const d = new Date(); d.setDate(d.getDate() - 1); return d; })()) &&
                     isSameDay(selectedRange.end, (() => { const d = new Date(); d.setDate(d.getDate() - 1); return d; })()));

                  return (
                    <button
                      key={range.key}
                      onClick={() => handleQuickRange(range.key)}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                        isSelected
                          ? 'bg-purple-100 text-purple-700 font-medium'
                          : 'text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      {range.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-slate-200 flex justify-end gap-3">
            <button
              onClick={handleCancel}
              className="px-4 py-2 rounded-xl bg-white border border-slate-200 text-slate-700 text-sm font-medium hover:bg-slate-50 transition-colors"
            >
              Hủy
            </button>
            <button
              onClick={handleUpdate}
              disabled={!selectedRange.start || !selectedRange.end}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white text-sm font-medium hover:from-purple-700 hover:to-pink-700 transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cập nhật
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DateRangePickerPopover;

