import { cookies } from "next/headers";

import { AUTH_COOKIE_NAME } from "@/lib/auth-cookie";

export function getServerAuthToken(): string | null {
  const token = cookies().get(AUTH_COOKIE_NAME)?.value;
  return token || null;
}
