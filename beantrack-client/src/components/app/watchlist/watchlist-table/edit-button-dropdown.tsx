"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
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
import { WatchlistItem } from "@/models";
import { handleStatusUpdateAndDelete } from "@/utils/handle-status-update-and-delete";

export function EditButton({
  item,
  type,
}: {
  item: WatchlistItem;
  type: string;
}) {
  const _padding = "py-0.5 px-1 m-0 h-auto w-auto min-h-0 min-w-0";
  const _main =
    "leading-none rounded-sm text-xs light:bg-white dark:text-sky-600 text-sky-800 border-1 light:border-gray-400 cursor-pointer";
  const _effects = "hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700";

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className={cn(_padding, _main, _effects)}>
          edit
        </Button>
      </DropdownMenuTrigger>
      <EditButtonDropdownContent item={item} type={type} />
    </DropdownMenu>
  );
}

function EditButtonDropdownContent({
  item,
  type,
}: {
  item: WatchlistItem;
  type: string;
}) {
  const actions = [
    {
      label: "Currently Watching",
      action: "watching",
      icon: <TvMinimalPlay />,
    },
    { label: "Completed", action: "completed", icon: <SquareCheckBig /> },
    { label: "On Hold", action: "on_hold", icon: <OctagonPause /> },
    { label: "Dropped", action: "dropped", icon: <BookmarkX /> },
    { label: "Plan to Watch", action: "plan_to_watch", icon: <NotebookPen /> },
    { label: "Delete", action: "delete", icon: <Trash2 /> },
  ];

  return (
    <DropdownMenuContent className="w-48">
      {actions.map(({ label, action, icon }) =>
        action !== "delete" ? (
          <DropdownMenuItem
            key={action}
            onSelect={() => handleStatusUpdateAndDelete(action, type, item)}
            className="cursor-pointer">
            {icon}
            {label}
          </DropdownMenuItem>
        ) : (
          <Fragment key={action}>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onSelect={() => handleStatusUpdateAndDelete(action, type, item)}
              className="cursor-pointer">
              {icon}
              {label}
            </DropdownMenuItem>
          </Fragment>
        )
      )}
    </DropdownMenuContent>
  );
}
