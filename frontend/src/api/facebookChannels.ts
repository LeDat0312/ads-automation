import api from "./base";

export interface FacebookPageSummary {
  id: string;
  name: string;
  picture_url?: string;
  category?: string;
  access_token?: string;
  
  // Permission flags
  tasks: string[];
  is_admin: boolean;
  can_publish: boolean;
  can_moderate: boolean;
  warning_message?: string;
}

export async function getPagesOfFacebookAccount(id: number) {
  return api.get<FacebookPageSummary[]>(`/api/facebook-accounts/${id}/pages`);
}

export async function connectPagesFromSavedAccount(payload: {
  facebook_account_id: number;
  page_ids: string[];
}) {
  return api.post(`/api/channels/facebook/from-saved-account`, payload);
}

export async function connectPageManualV2(payload: {
  page_id: string;
  facebook_account_id?: number;
  page_name_override?: string;
}) {
  return api.post<{
    channel: any;
    is_admin: boolean;
    can_publish: boolean;
    can_moderate: boolean;
    warning_message?: string;
  }>(`/api/channels/facebook/manual-v2`, payload);
}
