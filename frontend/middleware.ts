import { NextRequest, NextResponse } from "next/server";

const AUTH_COOKIE_NAME = "jobflow_token";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isPublicPath = pathname === "/login" || pathname.startsWith("/_next");
  if (isPublicPath) {
    return NextResponse.next();
  }

  const token = request.cookies.get(AUTH_COOKIE_NAME)?.value;
  if (!token) {
    const loginUrl = new URL("/login", request.url);
    return NextResponse.redirect(loginUrl);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|favicon.ico).*)"],
};
