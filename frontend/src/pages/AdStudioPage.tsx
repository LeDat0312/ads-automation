import React from 'react';
import AdStudioCard from '../components/AdStudioCard';

const AdStudioPage: React.FC = () => {
  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      {/* Header */}
      <header className="bg-transparent shadow-lg sticky top-0 z-30">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between">
            {/* Left: Logo & Title */}
            <div className="flex items-center gap-3">
              <div className="text-3xl">🎬</div>
              <div>
                <h1 className="text-xl font-bold text-white">
                  Ad Studio
                </h1>
                <p className="text-xs text-white/80">Thu thập, quản lý video và lên lịch đăng bài</p>
              </div>
            </div>
            
            {/* Right: Home Button */}
            <div className="flex items-center gap-3">
              {/* Dashboard Link */}
              <button 
                className="px-4 py-2 border-2 border-white/30 text-white rounded-lg hover:bg-white/20 transition-colors text-sm font-medium backdrop-blur-sm"
                onClick={() => window.location.href = '/dashboard'}
              >
                🚀 Dashboard
              </button>
              
              {/* Channel Management Link */}
              <button 
                className="px-4 py-2 border-2 border-white/30 text-white rounded-lg hover:bg-white/20 transition-colors text-sm font-medium backdrop-blur-sm"
                onClick={() => window.location.href = '/settings/channels'}
              >
                📡 Quản lý kênh
              </button>
              
              {/* Home Button */}
              <button 
                className="px-4 py-2 bg-white/20 backdrop-blur-sm text-white rounded-lg hover:bg-white/30 transition-colors text-sm font-semibold border border-white/30"
                onClick={() => window.location.href = '/'}
              >
                🏠 Về Trang Chủ
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-xl shadow-lg">
          <AdStudioCard />
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-8 py-6 border-t border-white/20">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-white/80">
          <p>Ad Studio • Powered by React + Vite + FastAPI</p>
        </div>
      </footer>
    </div>
  );
};

export default AdStudioPage;
