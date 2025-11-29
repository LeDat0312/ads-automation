import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import PrivacyPage from './pages/PrivacyPage';
import TermsPage from './pages/TermsPage';
import AdStudioPage from './pages/AdStudioPage';
import PagesList from './pages/Channels/PagesList';
import ChannelGroups from './pages/Channels/ChannelGroups';
import SettingsLayout from './components/SettingsLayout';
import ChannelsSettingsPage from './pages/Settings/ChannelsSettingsPage';
import ChannelGroupsSettingsPage from './pages/Settings/ChannelGroupsSettingsPage';
import PostingSettingsPage from './pages/Settings/PostingSettingsPage';

const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/dashboard" element={<App />} />
        <Route path="/ad-studio" element={<AdStudioPage />} />
        <Route path="/channels/pages" element={<PagesList />} />
        <Route path="/channels/groups" element={<ChannelGroups />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/terms" element={<TermsPage />} />
        
        {/* Settings Routes */}
        <Route path="/settings" element={<SettingsLayout />}>
          <Route path="channels" element={<ChannelsSettingsPage />} />
          <Route path="channel-groups" element={<ChannelGroupsSettingsPage />} />
          <Route path="posting" element={<PostingSettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;

