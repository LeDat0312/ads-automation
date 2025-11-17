# 📊 Facebook Ads Dashboard - Madgicx Style Implementation

## 🎯 Dashboard Overview

### Core Objectives
- **Unified Ads Manager 2.0**: All campaigns/adsets/ads in one interface
- **Real-time Performance Monitoring**: Live metrics with auto-refresh
- **Advanced Filtering & Segmentation**: Like Madgicx's powerful filters
- **Actionable Insights**: Not just data, but recommendations
- **Automation Integration**: Seamless connection to automation rules

## 🏗️ Architecture Design

### 1. Data Layer
```typescript
// Core data models
interface CampaignMetrics {
  // Identity
  campaign_id: string;
  campaign_name: string;
  account_id: string;
  account_name: string;
  
  // Performance Metrics
  spend: number;
  impressions: number;
  clicks: number;
  purchases: number;
  purchase_value: number;
  leads: number;
  
  // Calculated Metrics
  ctr: number;
  cpc: number;
  cpm: number;
  cpa: number;
  roas: number;
  frequency: number;
  
  // Meta Data
  status: 'ACTIVE' | 'PAUSED' | 'DELETED';
  objective: string;
  date_range: DateRange;
  created_time: string;
  updated_time: string;
}

interface AdsetMetrics extends CampaignMetrics {
  adset_id: string;
  adset_name: string;
  campaign_id: string;
  bid_strategy: string;
  budget_type: 'DAILY' | 'LIFETIME';
  budget: number;
  targeting_summary: string;
}

interface AdMetrics extends AdsetMetrics {
  ad_id: string;
  ad_name: string;
  adset_id: string;
  creative_type: 'IMAGE' | 'VIDEO' | 'CAROUSEL' | 'COLLECTION';
  creative_thumbnail: string;
}
```

### 2. API Endpoints
```
GET /api/dashboard/overview
├── Summary metrics (total spend, ROAS, etc.)
├── Top performers (campaigns/adsets/ads)
├── Alerts & recommendations
└── Automation status

GET /api/dashboard/campaigns
├── Paginated campaigns list
├── Advanced filtering
├── Sorting & grouping
└── Bulk actions support

GET /api/dashboard/adsets/{campaign_id}
├── Adsets for specific campaign
├── Performance comparison
├── Budget utilization
└── Targeting insights

GET /api/dashboard/ads/{adset_id}
├── Ads performance
├── Creative analysis
├── A/B testing results
└── Optimization suggestions

GET /api/dashboard/analytics
├── Performance trends
├── Attribution analysis
├── Conversion funnel
└── Audience insights
```

### 3. Frontend Components Structure
```
/components/dashboard/
├── overview/
│   ├── MetricsSummary.tsx       # Top-level KPIs
│   ├── PerformanceChart.tsx     # Trends visualization
│   ├── TopPerformers.tsx        # Best/worst performers
│   └── AlertsPanel.tsx          # Alerts & recommendations
├── ads-manager/
│   ├── AdsTable.tsx             # Main table view
│   ├── FiltersPanel.tsx         # Advanced filters
│   ├── BulkActions.tsx          # Mass edit capabilities
│   ├── PerformanceView.tsx      # Performance-focused view
│   └── CreativeView.tsx         # Creative-focused view
├── analytics/
│   ├── TrendAnalysis.tsx        # Performance trends
│   ├── AttributionReport.tsx    # Attribution analysis
│   ├── AudienceInsights.tsx     # Audience breakdown
│   └── ConversionFunnel.tsx     # Funnel analysis
└── shared/
    ├── MetricCard.tsx           # Reusable metric display
    ├── ChartContainer.tsx       # Chart wrapper
    ├── FilterBuilder.tsx        # Filter construction
    └── ActionDropdown.tsx       # Action menus
```

## 🎨 UI/UX Design - Madgicx Inspired

### 1. Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│ Header: Search + Filters + Date Range + Account Switcher   │
├─────────────────────────────────────────────────────────────┤
│ ┌─ Metrics Bar ─────────────────────────────────────────┐   │
│ │ Total Spend | ROAS | CPA | Leads | Active Campaigns  │   │
│ └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│ ┌─ View Controls ──────┐ ┌─ Action Bar ─────────────────┐   │
│ │ • Table View         │ │ ☐ Bulk Edit  📊 Analyze     │   │
│ │ • Performance View   │ │ ▶ Start      ⏸ Pause        │   │
│ │ • Creative View      │ │ 💰 Budget    📋 Duplicate    │   │
│ └─────────────────────┘ └─────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                 MAIN DATA TABLE                             │
│                                                             │
│ Campaign Name    Status    Spend    ROAS    CPA    Actions │
│ ├─ Adset 1      Active   $1,245   4.2x   $12.5    [...]   │
│ │  ├─ Ad A      Active    $645    5.1x   $9.8     [...]   │
│ │  └─ Ad B      Paused    $600    3.2x   $15.2    [...]   │
│ └─ Adset 2      Active   $2,100   3.8x   $18.3    [...]   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Footer: Pagination + Export + Automation Status            │
└─────────────────────────────────────────────────────────────┘
```

### 2. Advanced Filtering System
```typescript
interface FilterConfig {
  // Performance Filters
  spend: { min?: number; max?: number };
  roas: { min?: number; max?: number };
  cpa: { min?: number; max?: number };
  
  // Status Filters
  status: ('ACTIVE' | 'PAUSED' | 'DELETED')[];
  delivery_status: string[];
  
  // Date Filters
  date_range: {
    preset: 'today' | 'yesterday' | 'last_7_days' | 'last_30_days' | 'custom';
    start_date?: string;
    end_date?: string;
  };
  
  // Targeting Filters
  age_range: { min?: number; max?: number };
  gender: ('male' | 'female' | 'unknown')[];
  countries: string[];
  interests: string[];
  
  // Creative Filters
  creative_type: ('IMAGE' | 'VIDEO' | 'CAROUSEL')[];
  has_video: boolean;
  text_length: { min?: number; max?: number };
  
  // Custom Filters
  custom_rules: FilterRule[];
}

interface FilterRule {
  field: string;
  operator: '>' | '<' | '>=' | '<=' | '=' | '!=' | 'contains' | 'not_contains';
  value: any;
  logic: 'AND' | 'OR';
}
```

### 3. Performance Metrics System
```typescript
// Real-time metrics calculation
class MetricsCalculator {
  static calculateROAS(spend: number, revenue: number): number {
    return spend > 0 ? revenue / spend : 0;
  }
  
  static calculateCPA(spend: number, conversions: number): number {
    return conversions > 0 ? spend / conversions : 0;
  }
  
  static calculateCTR(clicks: number, impressions: number): number {
    return impressions > 0 ? (clicks / impressions) * 100 : 0;
  }
  
  static calculateFrequency(impressions: number, reach: number): number {
    return reach > 0 ? impressions / reach : 0;
  }
  
  // Performance scoring (0-100)
  static calculatePerformanceScore(metrics: AdMetrics): number {
    const roasScore = Math.min(metrics.roas * 25, 100); // 4x ROAS = 100 points
    const ctrScore = Math.min(metrics.ctr * 50, 100);   // 2% CTR = 100 points
    const frequencyScore = Math.max(100 - (metrics.frequency - 1) * 20, 0); // 1-2 frequency = good
    
    return (roasScore + ctrScore + frequencyScore) / 3;
  }
}
```

## 📈 Key Features Implementation

### 1. Real-time Data Updates
```typescript
// WebSocket connection for live updates
const useRealtimeMetrics = (filters: FilterConfig) => {
  const [metrics, setMetrics] = useState<AdMetrics[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const ws = new WebSocket('/ws/dashboard/metrics');
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      setMetrics(prev => updateMetrics(prev, update));
    };
    
    // Fetch initial data
    fetchMetrics(filters).then(setMetrics).finally(() => setIsLoading(false));
    
    return () => ws.close();
  }, [filters]);
  
  return { metrics, isLoading };
};
```

### 2. Advanced Table with Infinite Scroll
```typescript
// Virtualized table for handling large datasets
const AdsTable = ({ filters }: { filters: FilterConfig }) => {
  const { data, loadMore, hasMore } = useInfiniteQuery(
    ['ads-data', filters],
    ({ pageParam = 0 }) => fetchAds(filters, pageParam),
    {
      getNextPageParam: (lastPage) => lastPage.nextPage,
    }
  );
  
  return (
    <VirtualizedList
      items={data?.pages.flatMap(page => page.items) || []}
      itemHeight={60}
      onEndReached={hasMore ? loadMore : undefined}
      renderItem={({ item, index }) => (
        <AdTableRow 
          ad={item} 
          onAction={(action, ad) => handleAdAction(action, ad)}
        />
      )}
    />
  );
};
```

### 3. Bulk Actions System
```typescript
interface BulkAction {
  type: 'pause' | 'resume' | 'delete' | 'duplicate' | 'change_budget' | 'change_bid';
  payload?: any;
}

const useBulkActions = () => {
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  
  const executeAction = async (action: BulkAction) => {
    const results = await Promise.allSettled(
      selectedItems.map(id => applyActionToAd(id, action))
    );
    
    // Show results summary
    const successful = results.filter(r => r.status === 'fulfilled').length;
    const failed = results.length - successful;
    
    showToast(`Bulk action complete: ${successful} successful, ${failed} failed`);
    setSelectedItems([]);
  };
  
  return { selectedItems, setSelectedItems, executeAction };
};
```

### 4. Smart Recommendations Engine
```typescript
class RecommendationEngine {
  static analyzePerformance(ads: AdMetrics[]): Recommendation[] {
    const recommendations: Recommendation[] = [];
    
    // Scale high performers
    const highPerformers = ads.filter(ad => 
      ad.roas > 3.0 && ad.spend > 100 && ad.performance_score > 80
    );
    if (highPerformers.length > 0) {
      recommendations.push({
        type: 'scale_budget',
        priority: 'high',
        title: 'Scale High-Performing Ads',
        description: `${highPerformers.length} ads with ROAS > 3.0 can be scaled up`,
        action: 'increase_budget',
        payload: { increase_percent: 20, ads: highPerformers.map(ad => ad.ad_id) }
      });
    }
    
    // Pause poor performers
    const poorPerformers = ads.filter(ad =>
      ad.spend > 200 && (ad.roas < 1.0 || ad.performance_score < 30)
    );
    if (poorPerformers.length > 0) {
      recommendations.push({
        type: 'pause_ads',
        priority: 'high',
        title: 'Pause Underperforming Ads',
        description: `${poorPerformers.length} ads with poor ROAS should be paused`,
        action: 'pause',
        payload: { ads: poorPerformers.map(ad => ad.ad_id) }
      });
    }
    
    return recommendations;
  }
}
```

## 📱 Mobile-First Responsive Design

### 1. Responsive Breakpoints
```scss
// Design system breakpoints
$breakpoints: (
  'mobile': 480px,
  'tablet': 768px,
  'desktop': 1024px,
  'wide': 1440px
);

// Mobile-first approach
.dashboard-container {
  padding: 1rem;
  
  @media (min-width: map-get($breakpoints, 'tablet')) {
    padding: 1.5rem;
    display: grid;
    grid-template-columns: 1fr 3fr;
    gap: 2rem;
  }
  
  @media (min-width: map-get($breakpoints, 'desktop')) {
    padding: 2rem;
    grid-template-columns: 250px 1fr;
  }
}
```

### 2. Touch-Friendly Mobile Interface
```typescript
// Mobile-specific components
const MobileDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  
  return (
    <div className="mobile-dashboard">
      {/* Swipeable tabs */}
      <TabBar activeTab={activeTab} onChange={setActiveTab} />
      
      {/* Tab content */}
      <SwipeableViews index={activeTab}>
        <OverviewTab />
        <CampaignsTab />
        <AnalyticsTab />
      </SwipeableViews>
      
      {/* Floating action button */}
      <FloatingActionButton
        actions={[
          { icon: '▶️', label: 'Start Campaigns', action: () => {} },
          { icon: '⏸️', label: 'Pause All', action: () => {} },
          { icon: '📊', label: 'Analyze', action: () => {} },
        ]}
      />
    </div>
  );
};
```

## 🔄 Integration with Automation

### 1. Automation Status Indicators
```typescript
// Show automation status for each ad/campaign
const AutomationStatusBadge = ({ entity }: { entity: AdMetrics }) => {
  const { automationRules } = useEntityAutomation(entity.ad_id);
  
  if (automationRules.length === 0) return null;
  
  const activeRules = automationRules.filter(rule => rule.enabled);
  
  return (
    <Badge 
      color={activeRules.length > 0 ? 'green' : 'gray'}
      tooltip={`${activeRules.length} active automation rules`}
    >
      🤖 {activeRules.length}
    </Badge>
  );
};
```

### 2. One-Click Automation Setup
```typescript
// Quick automation setup from dashboard
const QuickAutomationPanel = ({ selectedAds }: { selectedAds: string[] }) => {
  return (
    <Panel title="Quick Automation">
      <Button onClick={() => createScalingRule(selectedAds)}>
        📈 Auto-Scale High Performers
      </Button>
      <Button onClick={() => createPausingRule(selectedAds)}>
        ⏸️ Auto-Pause Poor Performers
      </Button>
      <Button onClick={() => createBudgetRule(selectedAds)}>
        💰 Dynamic Budget Optimization
      </Button>
    </Panel>
  );
};
```

## 🎯 Implementation Timeline

### Week 1: Foundation
- [ ] Set up data models and API endpoints
- [ ] Create basic table component with filtering
- [ ] Implement real-time data fetching

### Week 2: Core Features
- [ ] Advanced filtering system
- [ ] Bulk actions functionality
- [ ] Performance metrics calculation

### Week 3: Advanced Features  
- [ ] Analytics and charts
- [ ] Recommendations engine
- [ ] Mobile responsive design

### Week 4: Polish & Integration
- [ ] Automation integration hooks
- [ ] Performance optimization
- [ ] Testing and bug fixes

This dashboard will provide the solid foundation needed for advanced automation rules! 🚀