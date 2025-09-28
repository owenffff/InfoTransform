import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Information Transformer",
  description: "Transform any file type into structured, actionable data using AI-powered analysis",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
