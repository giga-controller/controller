"use client";

import { dark } from "@clerk/themes";
import { useTheme } from "next-themes";
import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  const { resolvedTheme } = useTheme();

  return (
    <SignUp
      signInUrl="/sign-in"
      appearance={{
        baseTheme: resolvedTheme === "dark" ? dark : undefined,
      }}
    />
  );
}
