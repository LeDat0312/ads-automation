import api from "./base";

export interface FacebookPageSummary {
  id: string;
  name: string;
  picture_url?: string;
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
  display_name?: string;
}) {
  return api.post(`/api/channels/facebook/manual-v2`, payload);
}
