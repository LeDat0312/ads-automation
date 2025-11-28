/**
 * Channel Management Types
 * Types cho Facebook Pages, Channel Groups và Auto Comment
 */

export interface FacebookPage {
  id: string;
  user_id: number;
  page_id: string;
  page_name: string;
  page_avatar: string | null;
  category: string | null;
  connected_at: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
  item_id?: string; // For pages in groups - item_id to remove from group
}

export interface ChannelGroup {
  id: string;
  user_id: number;
  name: string;
  color: string;
  created_at: string;
  updated_at: string;
  pages: FacebookPage[];
}

export interface ChannelGroupItem {
  id: string;
  group_id: string;
  page_id: string;
}

export interface AutoCommentSchedule {
  id: string;
  user_id: number;
  group_id: string;
  post_id: string;
  comment_text: string;
  media_url: string | null;
  scheduled_at: string;
  posted_at: string | null;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  error_message: string | null;
  retry_count: number;
  max_retries: number;
  created_at: string;
  updated_at: string;
}

export interface ChannelGroupCreate {
  name: string;
  color: string;
}

export interface ChannelGroupUpdate {
  name?: string;
  color?: string;
}

export interface ChannelGroupItemCreate {
  page_id: string;
}

export interface AutoCommentScheduleCreate {
  group_id: string;
  post_id: string;
  comment_text: string;
  media_url?: string | null;
  scheduled_at: string;
}

export interface SyncPagesResponse {
  message: string;
  synced: number;
  updated: number;
  total: number;
}

