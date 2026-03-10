import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Oil Intelligence Index",
  description:
    "OSINT-powered Buy/Sell indicator for global oil markets. Real-time intelligence aggregation and scoring.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
