import { api, withAuth } from "@/lib/api";

export type ShippingProfile = {
  phone_number: string;
  address_line_1: string;
  address_line_2: string | null;
  city: string;
  state_or_region: string;
  postal_code: string;
  country: string;
};

export async function getShippingProfile(token: string) {
  const response = await api.get<ShippingProfile>("/account/profile", withAuth(token));
  return response.data;
}

export async function saveShippingProfile(token: string, profile: ShippingProfile) {
  const response = await api.put<ShippingProfile>("/account/profile", profile, withAuth(token));
  return response.data;
}
