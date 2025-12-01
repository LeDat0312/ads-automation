import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import PrivacyPage from './pages/PrivacyPage';
import TermsPage from './pages/TermsPage';
import AdStudioPage from './pages/AdStudioPage';
import SettingsLayout from './components/SettingsLayout';
import ChannelsSettingsPage from './pages/Settings/ChannelsSettingsPage';
import ChannelGroupsSettingsPage from './pages/Settings/ChannelGroupsSettingsPage';
import PostingSettingsPage from './pages/Settings/PostingSettingsPage';
import FacebookViaPage from './pages/Settings/FacebookViaPage';

const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Main Dashboard */}
        <Route path="/dashboard" element={<App />} />
        
        {/* Ad Studio - Separate page for TikTok/FB video collection & scheduling */}
        <Route path="/ad-studio" element={<AdStudioPage />} />
        
        {/* Legal Pages */}
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/terms" element={<TermsPage />} />
        
        {/* Settings Routes - Channel Management */}
        <Route path="/settings" element={<SettingsLayout />}>
          <Route path="channels" element={<ChannelsSettingsPage />} />
          <Route path="channel-groups" element={<ChannelGroupsSettingsPage />} />
          <Route path="posting" element={<PostingSettingsPage />} />
          <Route path="facebook-via" element={<FacebookViaPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;

