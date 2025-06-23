"use client";

import { usePathname } from "next/navigation";
import WatchlistTemplate from "@/components/app/watchlist/watchlist-template";

export default function Page() {
  const pathname = usePathname();
  const status = pathname?.split("/")?.[3];

  return <WatchlistTemplate type="movie" status={status} />;
}
