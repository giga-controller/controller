import type { Route } from "next";

export const ROUTE: Record<string, URL | Route<string>> = {
  // Main pages
  home: "/",
  chat: "/chat",
  docs: process.env.NEXT_PUBLIC_DOCS_URL as string,

  // Integration pages in docs
  Slack: `${process.env.NEXT_PUBLIC_DOCS_URL}/integrations/Slack` as string,
  Gmail: `${process.env.NEXT_PUBLIC_DOCS_URL}/integrations/Gmail` as string,
  Calendar:
    `${process.env.NEXT_PUBLIC_DOCS_URL}/integrations/Calendar` as string,
  Sheets: `${process.env.NEXT_PUBLIC_DOCS_URL}/integrations/Sheets` as string,
  Linear: `${process.env.NEXT_PUBLIC_DOCS_URL}/integrations/Linear` as string,
  X: `${process.env.NEXT_PUBLIC_DOCS_URL}/integrations/X` as string,
  Docs: `${process.env.NEXT_PUBLIC_DOCS_URL}/Docs` as string,
};
