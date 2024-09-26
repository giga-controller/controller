import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

// Define public routes
const isPublicRoute = createRouteMatcher([
  "/(.*)",
  "/chat(.*)",
  "/sign-in(.*)",
  "/sign-up(.*)",
]);

export default clerkMiddleware((auth, req) => {
  const { pathname } = req.nextUrl;
  const { userId } = auth();

  // Allow access to public routes
  if (!isPublicRoute(req)) {
    auth().protect();
  }

  if (!userId && pathname === "/") {
    return NextResponse.redirect(new URL("/sign-in", req.url));
  }
  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!.*\\..*|_next).*)", "/", "/(api|trpc)(.*)"],
};
