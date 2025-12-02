/**
 * PreviewPanel.tsx
 * Wrapper component for static preview system
 * Routes to Feed or Reels preview based on mode
 */

import { FacebookFeedStaticPreview } from './FacebookFeedStaticPreview';
import { FacebookReelsStaticPreview } from './FacebookReelsStaticPreview';
import { PreviewMode, PreviewDevice, PreviewData } from '../../types/preview';

interface PreviewPanelProps {
  mode: PreviewMode;
  device: PreviewDevice;
  data: PreviewData;
}

export function PreviewPanel({ mode, device, data }: PreviewPanelProps) {
  // Route to appropriate static preview component
  const renderPreview = () => {
    if (mode === 'reel' || mode === 'story') {
      return <FacebookReelsStaticPreview data={data} variant={device} />;
    } else {
      // mode === 'feed'
      return <FacebookFeedStaticPreview data={data} variant={device} />;
    }
  };

  return (
    <div className="flex items-center justify-center p-6 bg-gray-50 rounded-xl min-h-[600px]">
      {renderPreview()}
    </div>
  );
}
