import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface CompetitorAd {
  id: string;
  title: string;
  description: string;
  image_url?: string;
  video_url?: string;
  page_name?: string;
  page_id?: string;
  ad_url?: string;
  scraped_at: string;
}

interface SearchResult {
  success: boolean;
  data?: CompetitorAd[];
  message?: string;
}

const CompetitorResearch: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'search' | 'scrape' | 'competitor' | 'analytics'>('search');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<CompetitorAd[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  // Search state
  const [keyword, setKeyword] = useState('');
  const [searchLimit, setSearchLimit] = useState(20);
  
  // Scrape state
  const [adUrl, setAdUrl] = useState('');
  
  // Competitor state
  const [pageId, setPageId] = useState('');
  const [competitorLimit, setCompetitorLimit] = useState(50);
  
  // Analytics state
  const [selectedAds, setSelectedAds] = useState<Set<string>>(new Set());
  const [analyticsData, setAnalyticsData] = useState<any[]>([]);

  useEffect(() => {
    // Check API key status
    checkApiKeyStatus();
  }, []);

  const checkApiKeyStatus = async () => {
    try {
      const response = await axios.get('/settings/scrapegraphai/status');
      if (response.data.status === 'NOT_SET') {
        setError('ScrapeGraphAI API key chưa được cấu hình. Vui lòng vào Settings để cấu hình.');
      }
    } catch (err) {
      console.error('Error checking API key:', err);
    }
  };

  const handleSearch = async () => {
    if (!keyword.trim()) {
      setError('Vui lòng nhập từ khóa');
      return;
    }

    setLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await axios.post<SearchResult>('/competitor/search/ads', {
        keyword: keyword.trim(),
        limit: searchLimit,
        use_cache: true,
      });

      if (response.data.success && response.data.data) {
        setResults(response.data.data);
        setActiveTab('analytics');
      } else {
        setError(response.data.message || 'Không tìm thấy kết quả');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Lỗi khi tìm kiếm');
    } finally {
      setLoading(false);
    }
  };

  const handleScrapeAd = async () => {
    if (!adUrl.trim()) {
      setError('Vui lòng nhập URL quảng cáo');
      return;
    }

    setLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await axios.post('/competitor/scrape/ad', {
        ad_url: adUrl.trim(),
        use_cache: true,
      });

      if (response.data.success && response.data.data) {
        setResults([response.data.data]);
        setActiveTab('analytics');
      } else {
        setError(response.data.message || 'Không thể scrape quảng cáo');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Lỗi khi scrape');
    } finally {
      setLoading(false);
    }
  };

  const handleScrapeCompetitor = async () => {
    if (!pageId.trim()) {
      setError('Vui lòng nhập Page ID');
      return;
    }

    setLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await axios.post('/competitor/scrape/competitor', {
        page_id: pageId.trim(),
        limit: competitorLimit,
        use_cache: true,
      });

      if (response.data.success && response.data.data) {
        setResults(response.data.data);
        setActiveTab('analytics');
      } else {
        setError(response.data.message || 'Không thể scrape ads của đối thủ');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Lỗi khi scrape');
    } finally {
      setLoading(false);
    }
  };

  const toggleAdSelection = (adId: string) => {
    const newSelected = new Set(selectedAds);
    if (newSelected.has(adId)) {
      newSelected.delete(adId);
    } else {
      newSelected.add(adId);
    }
    setSelectedAds(newSelected);
  };

  const exportSelectedAds = () => {
    const selected = results.filter(ad => selectedAds.has(ad.id));
    const dataStr = JSON.stringify(selected, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `competitor-ads-${new Date().toISOString()}.json`;
    link.click();
  };

  const exportToCSV = () => {
    const headers = ['ID', 'Title', 'Description', 'Page Name', 'Page ID', 'Ad URL', 'Scraped At'];
    const rows = results.map(ad => [
      ad.id,
      ad.title || '',
      ad.description || '',
      ad.page_name || '',
      ad.page_id || '',
      ad.ad_url || '',
      ad.scraped_at,
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(',')),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `competitor-ads-${new Date().toISOString()}.csv`;
    link.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-500 via-pink-500 to-blue-500 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-2xl shadow-2xl p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">🔍 Nghiên Cứu Đối Thủ</h1>
          <p className="text-gray-600">Scrape và phân tích quảng cáo của đối thủ với ScrapeGraphAI</p>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 mb-6 rounded">
            <p className="font-bold">⚠️ Lỗi</p>
            <p>{error}</p>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-2xl shadow-xl mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('search')}
              className={`px-6 py-4 font-semibold transition-colors ${
                activeTab === 'search'
                  ? 'border-b-2 border-purple-500 text-purple-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              🔎 Tìm kiếm
            </button>
            <button
              onClick={() => setActiveTab('scrape')}
              className={`px-6 py-4 font-semibold transition-colors ${
                activeTab === 'scrape'
                  ? 'border-b-2 border-purple-500 text-purple-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              📄 Scrape Ad
            </button>
            <button
              onClick={() => setActiveTab('competitor')}
              className={`px-6 py-4 font-semibold transition-colors ${
                activeTab === 'competitor'
                  ? 'border-b-2 border-purple-500 text-purple-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              👤 Đối thủ
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-6 py-4 font-semibold transition-colors ${
                activeTab === 'analytics'
                  ? 'border-b-2 border-purple-500 text-purple-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              📊 Phân tích ({results.length})
            </button>
          </div>
        </div>

        {/* Search Tab */}
        {activeTab === 'search' && (
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h2 className="text-2xl font-bold mb-4">🔎 Tìm kiếm quảng cáo theo keyword</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Từ khóa
                </label>
                <input
                  type="text"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Ví dụ: điện thoại, laptop, quần áo..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Số lượng kết quả (1-100)
                </label>
                <input
                  type="number"
                  value={searchLimit}
                  onChange={(e) => setSearchLimit(Math.min(100, Math.max(1, parseInt(e.target.value) || 20)))}
                  min="1"
                  max="100"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <button
                onClick={handleSearch}
                disabled={loading}
                className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Đang tìm kiếm...' : '🔍 Tìm kiếm'}
              </button>
            </div>
          </div>
        )}

        {/* Scrape Tab */}
        {activeTab === 'scrape' && (
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h2 className="text-2xl font-bold mb-4">📄 Scrape quảng cáo cụ thể</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  URL quảng cáo Facebook
                </label>
                <input
                  type="text"
                  value={adUrl}
                  onChange={(e) => setAdUrl(e.target.value)}
                  placeholder="https://www.facebook.com/ads/library/?id=..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <button
                onClick={handleScrapeAd}
                disabled={loading}
                className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 transition-colors"
              >
                {loading ? 'Đang scrape...' : '📄 Scrape'}
              </button>
            </div>
          </div>
        )}

        {/* Competitor Tab */}
        {activeTab === 'competitor' && (
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h2 className="text-2xl font-bold mb-4">👤 Scrape ads của đối thủ</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Facebook Page ID
                </label>
                <input
                  type="text"
                  value={pageId}
                  onChange={(e) => setPageId(e.target.value)}
                  placeholder="123456789012345"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Số lượng ads (1-100)
                </label>
                <input
                  type="number"
                  value={competitorLimit}
                  onChange={(e) => setCompetitorLimit(Math.min(100, Math.max(1, parseInt(e.target.value) || 50)))}
                  min="1"
                  max="100"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <button
                onClick={handleScrapeCompetitor}
                disabled={loading}
                className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 transition-colors"
              >
                {loading ? 'Đang scrape...' : '👤 Scrape đối thủ'}
              </button>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">📊 Kết quả phân tích ({results.length} ads)</h2>
              <div className="flex gap-2">
                {selectedAds.size > 0 && (
                  <button
                    onClick={exportSelectedAds}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    📥 Export {selectedAds.size} ads (JSON)
                  </button>
                )}
                <button
                  onClick={exportToCSV}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  📊 Export CSV
                </button>
              </div>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
                <p className="mt-4 text-gray-600">Đang tải...</p>
              </div>
            ) : results.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <p>Chưa có kết quả. Hãy tìm kiếm hoặc scrape ads để bắt đầu.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {results.map((ad) => (
                  <div
                    key={ad.id}
                    className={`border-2 rounded-lg p-4 transition-all ${
                      selectedAds.has(ad.id)
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <input
                        type="checkbox"
                        checked={selectedAds.has(ad.id)}
                        onChange={() => toggleAdSelection(ad.id)}
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg mb-2">{ad.title || 'Không có tiêu đề'}</h3>
                        <p className="text-gray-600 mb-2">{ad.description || 'Không có mô tả'}</p>
                        <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                          {ad.page_name && <span>📄 {ad.page_name}</span>}
                          {ad.page_id && <span>🆔 {ad.page_id}</span>}
                          {ad.scraped_at && <span>🕒 {new Date(ad.scraped_at).toLocaleString('vi-VN')}</span>}
                        </div>
                        {ad.image_url && (
                          <img src={ad.image_url} alt={ad.title} className="mt-4 max-w-md rounded-lg" />
                        )}
                        {ad.ad_url && (
                          <a
                            href={ad.ad_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-2 inline-block text-purple-600 hover:underline"
                          >
                            🔗 Xem quảng cáo gốc
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CompetitorResearch;

