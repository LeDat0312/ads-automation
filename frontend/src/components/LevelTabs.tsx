
export type Level = 'campaign' | 'adset' | 'ad';

interface LevelTabsProps {
  currentLevel: Level;
  onLevelChange: (level: Level) => void;
  drillDownPath?: {
    campaignId?: string;
    campaignName?: string;
    adsetId?: string;
    adsetName?: string;
  };
  onDrillUp?: () => void;
}

export default function LevelTabs({
  currentLevel,
  onLevelChange,
  drillDownPath,
  onDrillUp,
}: LevelTabsProps) {
  const tabs: { level: Level; label: string; icon: string }[] = [
    { level: 'campaign', label: 'Chiến dịch', icon: '🎯' },
    { level: 'adset', label: 'Nhóm quảng cáo', icon: '📊' },
    { level: 'ad', label: 'Quảng cáo', icon: '📱' },
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2 mb-6">
      <div className="flex items-center gap-2">
        {/* Level Tabs */}
        <div className="flex gap-1 flex-1">
          {tabs.map((tab) => (
            <button
              key={tab.level}
              onClick={() => onLevelChange(tab.level)}
              className={`
                flex-1 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200
                ${
                  currentLevel === tab.level
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200'
                    : 'text-gray-700 hover:bg-gray-50'
                }
              `}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Drill-down Path */}
        {drillDownPath && (drillDownPath.campaignId || drillDownPath.adsetId) && (
          <div className="flex items-center gap-2 px-4 py-2 bg-indigo-50 rounded-lg border border-indigo-200">
            {drillDownPath.campaignId && (
              <>
                <span className="text-sm font-medium text-indigo-700">
                  🎯 {drillDownPath.campaignName || drillDownPath.campaignId}
                </span>
                {drillDownPath.adsetId && (
                  <>
                    <span className="text-indigo-400">→</span>
                    <span className="text-sm font-medium text-indigo-700">
                      📊 {drillDownPath.adsetName || drillDownPath.adsetId}
                    </span>
                  </>
                )}
              </>
            )}
            {onDrillUp && (
              <button
                onClick={onDrillUp}
                className="ml-2 px-2 py-1 text-xs bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors"
                title="Quay lại"
              >
                ← Quay lại
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

