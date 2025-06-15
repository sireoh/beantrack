"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function WatchlistTableTitleEditButton() {
  const _padding = "py-0.5 px-1 m-0 h-auto w-auto min-h-0 min-w-0";
  const _main =
    "leading-none rounded-sm text-xs light:bg-white dark:text-sky-600 text-sky-800 border-1 light:border-gray-400";
  const _effects = "hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700";

  return (
    <Button variant="ghost" className={cn(_padding, _main, _effects)}>
      edit
    </Button>
  );
}
