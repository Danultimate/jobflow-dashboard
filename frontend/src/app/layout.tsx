import "./globals.css";
import type { Metadata } from "next";

import { Navbar } from "@/components/navbar";

export const metadata: Metadata = {
  title: "JobFlow Dashboard",
  description: "Track and automate job applications with local AI.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main className="container-shell">{children}</main>
      </body>
    </html>
  );
}
