import api from "./base";

export type FacebookAccountType = "fanpage" | "ads" | "both";

export interface FacebookAccount {
  id: number;
  name: string;
  token_type: FacebookAccountType;
  note?: string;
  is_active: boolean;
  masked_token: string;
  last_verified_at?: string;
  created_at: string;
}

export async function listFacebookAccounts(params?: { type?: "fanpage" | "ads" | "both" }) {
  return api.get<FacebookAccount[]>("/api/facebook-accounts", { params });
}

export async function createFacebookAccount(payload: {
  name: string;
  token_type: FacebookAccountType;
  access_token: string;
  note?: string;
}) {
  return api.post("/api/facebook-accounts", payload);
}

export async function updateFacebookAccount(id: number, payload: {
  name?: string;
  token_type?: FacebookAccountType;
  access_token?: string;
  note?: string;
  is_active?: boolean;
}) {
  return api.patch(`/api/facebook-accounts/${id}`, payload);
}

export async function deleteFacebookAccount(id: number) {
  return api.delete(`/api/facebook-accounts/${id}`);
}

export async function verifyFacebookAccount(id: number) {
  return api.post(`/api/facebook-accounts/${id}/verify`);
}
