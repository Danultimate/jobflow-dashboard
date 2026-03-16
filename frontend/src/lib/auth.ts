import { cookies } from "next/headers";

export const AUTH_COOKIE_NAME = "jobflow_token";

export function getServerAuthToken(): string | null {
  const token = cookies().get(AUTH_COOKIE_NAME)?.value;
  return token || null;
}
