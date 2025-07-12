"use client";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Episode, WatchlistItem } from "@/models";
import { handleChangeProgress } from "@/utils/handle-change-progress";
import { Dispatch, SetStateAction } from "react";

export function EditProgress({
  item,
  currentProgress,
  setCurrentProgress,
}: {
  item: WatchlistItem;
  currentProgress: number;
  setCurrentProgress: Dispatch<SetStateAction<number>>;
}) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <span className="cursor-pointer">
          {item.status == "completed"
            ? item.episodes.length
            : `${currentProgress + 1}/${item.episodes.length}`}
        </span>
      </DropdownMenuTrigger>
      <EditButtonDropdownContent
        item={item}
        episodes={item.episodes}
        setCurrentProgress={setCurrentProgress}
      />
    </DropdownMenu>
  );
}

function EditButtonDropdownContent({
  item,
  episodes,
  setCurrentProgress,
}: {
  item: WatchlistItem;
  episodes: Episode[];
  setCurrentProgress: Dispatch<SetStateAction<number>>;
}) {
  return (
    <DropdownMenuContent className="w-48 max-h-64 overflow-y-auto">
      {episodes.map((episode, index) => (
        <DropdownMenuItem
          key={episode.code + episode.name}
          onSelect={() => handleChangeProgress(item, index, setCurrentProgress)}
          className="cursor-pointer">
          {episode.code} {episode.name}
        </DropdownMenuItem>
      ))}
    </DropdownMenuContent>
  );
}
