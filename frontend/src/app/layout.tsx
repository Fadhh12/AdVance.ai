import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

// DESIGN_SYSTEM.md §4: condensed grotesk for display/headline (broadcast lower-third
// feel), neutral Inter for body/UI. Never use Space Grotesk for body text or Inter
// for display headlines — keep the pairing distinct.
const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "adVance.AI",
  description:
    "Upload foto atau ide, AI generate, edit, dan siapkan video untuk Instagram, TikTok, dan YouTube.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="id"
      className={`${spaceGrotesk.variable} ${inter.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-canvas text-ink">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
