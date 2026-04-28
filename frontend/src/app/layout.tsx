import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "LeadForge AI — Intelligent Lead Generation",
  description:
    "AI-powered B2B lead generation platform. Discover, enrich, score and outreach — all automated.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark scroll-smooth">
      <body
        className={`${inter.variable} font-sans bg-gray-950 text-gray-100 antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
