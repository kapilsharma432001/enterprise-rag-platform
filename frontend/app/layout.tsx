import type { Metadata } from "next";
import { Geist, Geist_Mono, Inter } from "next/font/google";
import "./global.css";
import { TenantProvider } from "../context/TenantContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Enterprise RAG Platform",
  description: "Multi-Tenant RAG System",
};

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={inter.className}>
          {/* We wrap the 'children' with the Provider */}
          <TenantProvider>
            <div className="min-h-screen bg-gray-50 text-gray-900">
            {children}
            </div>
          </TenantProvider>
      </body>
    </html>
  );
}
