"use client";

import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { TvMinimalPlay, SquareCheckBig, NotebookPen } from "lucide-react";
import { WatchlistItem } from "@/models";

const ItemCardAddButtonDropdown = ({ item }: { item: WatchlistItem }) => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button size="icon" variant="outline" className="size-6">
          <Plus />
        </Button>
      </DropdownMenuTrigger>
      <ItemCardAddButtonDropdownContent />
    </DropdownMenu>
  );
};

function ItemCardAddButtonDropdownContent() {
  const actions = [
    {
      label: "Currently Watching",
      action: "watching",
      icon: <TvMinimalPlay />,
    },
    { label: "Completed", action: "completed", icon: <SquareCheckBig /> },
    { label: "Plan to Watch", action: "plan_to_watch", icon: <NotebookPen /> },
  ];

  const handleSelect = async (action: string) => {
    console.log("[ItemCardAddButtonDropdownContent] handleSelect: ", action);
  };

  return (
    <DropdownMenuContent className="w-48">
      {actions.map(({ label, action, icon }) => (
        <DropdownMenuItem
          key={action}
          onSelect={() => handleSelect(action)}
          className="cursor-pointer">
          {icon}
          {label}
        </DropdownMenuItem>
      ))}
    </DropdownMenuContent>
  );
}

export default ItemCardAddButtonDropdown;
