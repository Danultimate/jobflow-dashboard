import { AUTH_COOKIE_NAME } from "@/lib/auth-cookie";

export function getBrowserAuthToken(): string {
  if (typeof document === "undefined") {
    return "";
  }
  const pair = document.cookie
    .split("; ")
    .find((cookie) => cookie.startsWith(`${AUTH_COOKIE_NAME}=`));
  return pair ? decodeURIComponent(pair.split("=")[1]) : "";
}
