/**
 * Root Layout
 * Global layout wrapper with fonts, providers, and metadata
 * Note: Dashboard and auth pages have their own layouts without Navbar/Footer
 */
import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/lib/providers/query-provider";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: {
    default: "Sunona - Voice AI Platform",
    template: "%s | Sunona",
  },
  description:
    "Build, deploy, and scale voice AI agents in minutes. Enterprise-grade platform with 40+ integrations for STT, TTS, LLM, and telephony providers.",
  keywords: [
    "voice AI",
    "AI agents",
    "speech to text",
    "text to speech",
    "conversational AI",
    "phone automation",
    "customer support AI",
    "call center AI",
  ],
  authors: [{ name: "Sunona AI" }],
  creator: "Sunona AI",
  publisher: "Sunona AI",
  metadataBase: new URL("https://sunona.ai"),
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://sunona.ai",
    siteName: "Sunona",
    title: "Sunona - Voice AI Platform",
    description:
      "Build, deploy, and scale voice AI agents in minutes. Enterprise-grade platform with 40+ integrations.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Sunona Voice AI Platform",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Sunona - Voice AI Platform",
    description:
      "Build, deploy, and scale voice AI agents in minutes. Enterprise-grade platform with 40+ integrations.",
    images: ["/og-image.png"],
    creator: "@sunona_ai",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon-16x16.png",
    apple: "/apple-touch-icon.png",
  },
  manifest: "/site.webmanifest",
};

export const viewport: Viewport = {
  themeColor: "#00D4AA",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable}`}
      suppressHydrationWarning
    >
      <body
        className="min-h-screen bg-black text-white antialiased"
        suppressHydrationWarning
      >
        <QueryProvider>
          {children}
        </QueryProvider>
      </body>
    </html>
  );
}

