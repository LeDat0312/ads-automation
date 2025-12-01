import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

interface SettingsLayoutProps {
  children?: React.ReactNode;
}

const SettingsLayout: React.FC<SettingsLayoutProps> = ({ children }) => {
  const menuItems = [
    {
      path: '/settings/channels',
      label: 'Kênh đã kết nối',
      icon: '📡',
    },
    {
      path: '/settings/facebook-via',
      label: 'Quản lý Via Facebook',
      icon: '🔑',
    },
    {
      path: '/settings/channel-groups',
      label: 'Nhóm kênh',
      icon: '👥',
    },
    {
      path: '/settings/posting',
      label: 'Cài đặt đăng bài & bình luận',
      icon: '⚙️',
    },
  ];

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      {/* Header */}
      <header className="bg-transparent shadow-lg sticky top-0 z-30">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between">
            {/* Left: Logo & Title */}
            <div className="flex items-center gap-3">
              <div className="text-3xl">⚙️</div>
              <div>
                <h1 className="text-xl font-bold text-white">
                  Quản lý kênh
                </h1>
                <p className="text-xs text-white/80">Cài đặt và quản lý kênh của bạn</p>
              </div>
            </div>
            
            {/* Right: Home Button */}
            <div className="flex items-center gap-3">
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
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="flex flex-col lg:flex-row">
            {/* Sidebar */}
            <aside className="w-full lg:w-64 border-b lg:border-b-0 lg:border-r border-gray-200 bg-slate-50">
              <nav className="p-4 space-y-1">
                {menuItems.map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) => `
                      flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all
                      ${
                        isActive
                          ? 'bg-indigo-600 text-white shadow-md'
                          : 'text-gray-700 hover:bg-gray-100'
                      }
                    `}
                  >
                    <span className="text-xl">{item.icon}</span>
                    <span>{item.label}</span>
                  </NavLink>
                ))}
              </nav>
            </aside>

            {/* Content Area */}
            <div className="flex-1 p-6">
              {children || <Outlet />}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-8 py-6 border-t border-white/20">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-white/80">
          <p>Quản lý kênh • Powered by React + Vite + FastAPI</p>
        </div>
      </footer>
    </div>
  );
};

export default SettingsLayout;

