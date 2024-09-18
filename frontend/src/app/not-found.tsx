"use client";

import Link from "next/link";
import { ROUTE } from "@/constants/route";

import "@/styles/globals.css";

export default function NotFound() {
  return (
    <div className="flex flex-col w-full p-8">
      <div className="p-20">
        <h1 className="text-3xl">
          Oops! Page not found. We are testing in production :(
        </h1>
        <p className="mt-4 text-2xl">
          Maybe return to the{" "}
          <Link
            href={ROUTE.home}
            className="font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-600"
          >
            home page
          </Link>
          ?
        </p>
      </div>
    </div>
  );
}
