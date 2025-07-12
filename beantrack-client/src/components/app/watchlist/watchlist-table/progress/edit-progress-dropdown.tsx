"use client";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  TvMinimalPlay,
  SquareCheckBig,
  OctagonPause,
  BookmarkX,
  NotebookPen,
  Trash2,
} from "lucide-react";
import { Fragment } from "react";
import { Episode, WatchlistItem } from "@/models";
import { handleChangeProgress } from "@/utils/handle-change-progress";

export function EditProgress({ item }: { item: WatchlistItem }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <span className="cursor-pointer">
          {item.status == "completed"
            ? item.episodes.length
            : `${item.currentEpisodeIndex + 1}/${item.episodes.length}`}
        </span>
      </DropdownMenuTrigger>
      <EditButtonDropdownContent episodes={item.episodes} />
    </DropdownMenu>
  );
}

function EditButtonDropdownContent({ episodes }: { episodes: Episode[] }) {
  return (
    <DropdownMenuContent className="w-48 max-h-64 overflow-y-auto">
      {episodes.map((episode, index) => (
        <DropdownMenuItem
          key={episode.code + episode.name}
          onSelect={() => handleChangeProgress(index)}
          className="cursor-pointer">
          {episode.code} {episode.name}
        </DropdownMenuItem>
      ))}
    </DropdownMenuContent>
  );
}
