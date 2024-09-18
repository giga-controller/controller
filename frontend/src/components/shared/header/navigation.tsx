import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ROUTE } from "@/constants/route";

export default function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="flex itens-center space-x-4">
      <Link
        href={ROUTE.home}
        className={`px-3 py-2 rounded-md text-sm font-medium ${pathname === "/" ? "bg-black dark:bg-white text-white dark:text-black" : "text-black-300 hover:bg-gray-700 hover:text-white"}`}
      >
        Home
      </Link>
      {/* <Link
        href={ROUTE.chat}
        className={`px-3 py-2 rounded-md text-sm font-medium ${pathname === "/chat" ? "bg-black dark:bg-white text-white dark:text-black" : "text-black-300 hover:bg-gray-700 hover:text-white"}`}
      >
        Chat
      </Link> */}
      <Link
        href={ROUTE.docs}
        className={`px-3 py-2 rounded-md text-sm font-medium ${pathname === "/docs" ? "bg-black dark:bg-white text-white dark:text-black" : "text-black-300 hover:bg-gray-700 hover:text-white"}`}
        target="_blank"
        rel="noopener noreferrer"
      >
        Docs
      </Link>
    </nav>
  );
}
