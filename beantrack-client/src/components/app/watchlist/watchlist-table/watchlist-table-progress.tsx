"use client";

import { Button } from "@/components/ui/button";
import React from "react";
import { Minus, Plus } from "lucide-react";
import { cn } from "@/lib/utils";
import axios from "axios";

// ---------- Temp --------------------
import { toast } from "sonner";
import { WatchlistItem } from "@/models";
// ---------- End: Temp ---------------

const WatchlistTableProgress = ({ item }: { item: WatchlistItem }) => {
  const _padding = "p-0 m-0 h-auto w-auto min-h-0 min-w-0";
  const _main =
    "leading-none rounded-sm text-xs light:bg-white dark:text-sky-600 text-sky-800 border-1 light:border-gray-400";
  const _effects =
    "hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 p-0 m-0";
  const _svgPadding =
    "px-0 has-[>svg]:px-0 [&>svg]:mx-0 [&>svg]:p-0 [&>svg]:w-4 [&>svg]:h-4";

  const handleSelect = async (action: string) => {
    try {
      const url = `/api/${item.imdb}/edit/tv_show/progress/${action}`;
      await axios.patch(url);
      toast.success(`Updated to "${action}"`);
    } catch (error) {
      console.error(error);
      toast.error("Failed to update item.");
    }
  };

  return (
    <div className="grid align-items-center justify-center">
      {/* Watchlist Table Progress */}
      <div className="flex gap-5">
        <Button
          variant="ghost"
          onClick={() => handleSelect("decrement")}
          className={cn(_padding, _main, _effects, _svgPadding)}>
          <Minus />
        </Button>

        <Button
          variant="ghost"
          onClick={() => handleSelect("increment")}
          className={cn(_padding, _main, _effects, _svgPadding)}>
          <Plus />
        </Button>
      </div>
      <span>
        {item.status == "completed"
          ? item.episodes.length
          : `${item.currentEpisodeIndex}/${item.episodes.length}`}
      </span>
    </div>
  );
};

export default WatchlistTableProgress;
