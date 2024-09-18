import type { Metadata } from "next";
import { Inter } from "next/font/google";
import {
  ClerkLoaded,
  ClerkLoading,
  ClerkProvider,
  SignedIn,
} from "@clerk/nextjs";
import "@/styles/globals.css";
import { ThemeProvider } from "@/components/shared/theme/provider";
import PageLoader from "@/components/shared/page-loading-indicator";
import { QueryProvider } from "@/components/shared/query-provider";
import { Toaster } from "@/components/ui/toaster";
import HeaderButtons from "@/components/shared/header/buttons";
import { PHProvider } from "@/app/providers";
import dynamic from "next/dynamic";

const PostHogPageView = dynamic(() => import("@/app/PostHogPageView"), {
  ssr: false,
});

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Controller",
  description:
    "Controller seeks to build application connectors powered by natural language inputs.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en">
        <head>
          <link rel="icon" href="/favicon.ico" sizes="any" />
          <link
            rel="icon"
            href="/icon?<generated>"
            type="image/<generated>"
            sizes="<generated>"
          />
          <link
            rel="apple-touch-icon"
            href="/apple-icon?<generated>"
            type="image/<generated>"
            sizes="<generated>"
          />
        </head>
        <PHProvider>
          <body className={inter.className}>
            <PostHogPageView />
            <ThemeProvider
              attribute="class"
              defaultTheme="system"
              enableSystem
              disableTransitionOnChange
            >
              <ClerkLoading>
                <PageLoader />
              </ClerkLoading>
              <ClerkLoaded>
                <div className={`flex flex-col w-full p-8`}>
                  <SignedIn>
                    <HeaderButtons />
                  </SignedIn>
                </div>
                <QueryProvider>
                  {children}
                  <Toaster />
                </QueryProvider>
              </ClerkLoaded>
            </ThemeProvider>
          </body>
        </PHProvider>
      </html>
    </ClerkProvider>
  );
}
