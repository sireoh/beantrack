import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "next-themes";
import { Navbar } from "@/components/app/navbar/navbar";
import { MobileSearchbar } from "@/components/app/search/search-mobile";
import ThemedToast from "@/components/app/global/themed-toast";
import { DeletionDialog } from "@/components/app/global/deletion-dialog";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "BeanTrack",
  description: "version 2.0",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange>
          <div className="min-h-screen flex flex-col">
            {/* Navbar */}
            <Navbar />

            <DeletionDialog />

            {/* Toast Notifications */}
            <ThemedToast />

            {/* Search Mobile Dropdown */}
            <div className="lg:hidden pt-15">
              <MobileSearchbar />
            </div>

            {/* Main Children */}
            <main className="flex-1 light:bg-gray-200 lg:pt-15">
              <section className="py-4">
                <div className="container mx-auto px-4">{children}</div>
              </section>
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
