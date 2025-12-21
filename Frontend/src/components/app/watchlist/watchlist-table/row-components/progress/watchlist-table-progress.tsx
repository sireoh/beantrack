"use client";

import { Button } from "@/components/ui/button";
import { Minus, Plus } from "lucide-react";
import { cn } from "@/lib/utils";
import axios from "axios";

// ---------- Temp --------------------
import { toast } from "sonner";
import { WatchlistItem } from "@/models";
import { EditProgress } from "./edit-progress-dropdown";
import { Dispatch, SetStateAction } from "react";
// ---------- End: Temp ---------------

const WatchlistTableProgress = ({
  item,
  currentProgress,
  setCurrentProgress,
}: {
  item: WatchlistItem;
  currentProgress: number;
  setCurrentProgress: Dispatch<SetStateAction<number>>;
}) => {
  const _padding = "p-0 m-0 h-auto w-auto min-h-0 min-w-0";
  const _main = cn(
    "leading-none rounded-sm text-xs light:bg-white dark:text-sky-600",
    "text-sky-800 border-1 light:border-gray-400 cursor-pointer"
  );
  const _effects =
    "hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 p-0 m-0";
  const _svgPadding =
    "px-0 has-[>svg]:px-0 [&>svg]:mx-0 [&>svg]:p-0 [&>svg]:w-4 [&>svg]:h-4";

  const handleSelect = async (action: string) => {
    // BACKEND
    try {
      const url = `/api/${item.imdb}/edit/tv_show/progress/${action}`;
      await axios.patch(url);
    } catch (error) {
      console.error(error);
      toast.error("Failed to update item.");
    }

    // FRONTEND
    if (currentProgress >= 0 && currentProgress <= item.episodes.length) {
      if (action === "increment") {
        setCurrentProgress((prev) =>
          Math.min(prev + 1, item.episodes.length - 1)
        );
      } else if (action === "decrement") {
        setCurrentProgress((prev) => Math.max(prev - 1, 0));
      }
    }

    // Toast Validation
    if (currentProgress >= 0 && currentProgress < item.episodes.length) {
      const episode =
        action === "increment"
          ? item.episodes[
              Math.min(currentProgress + 1, item.episodes.length - 1)
            ]
          : item.episodes[Math.max(currentProgress - 1, 0)];
      const code = episode.code;
      const name = episode.name;
      toast.success(
        action === "increment"
          ? `Incremented to: ${code} ${name}`
          : `Decremented to: ${code} ${name}`
      );
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
      <EditProgress
        item={item}
        currentProgress={currentProgress}
        setCurrentProgress={setCurrentProgress}
      />
    </div>
  );
};

export default WatchlistTableProgress;
