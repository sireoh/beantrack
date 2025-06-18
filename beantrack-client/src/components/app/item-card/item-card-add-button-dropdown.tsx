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
import { ItemCardDataModel } from "./item-card";
import { useStore } from "@/store";
import { OMDBResultsByIMDB } from "@/models";
import { fetchMovieByIMDB } from "@/utils/search-movie-by-imdb";

const ItemCardAddButtonDropdown = ({
  itemCardData,
}: {
  itemCardData: ItemCardDataModel;
}) => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button size="icon" variant="outline" className="size-6">
          <Plus />
        </Button>
      </DropdownMenuTrigger>
      <ItemCardAddButtonDropdownContent itemCardData={itemCardData} />
    </DropdownMenu>
  );
};

function ItemCardAddButtonDropdownContent({
  itemCardData,
}: {
  itemCardData: ItemCardDataModel;
}) {
  const search = useStore((state) => state.search);

  async function _m(action: string) {
    const results = await fetchMovieByIMDB(itemCardData.imdb);
    __handleMovieSelect(itemCardData, action, results);
  }

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
    search.currentType == "tv"
      ? __handleTVSelect(itemCardData, action)
      : _m(action);
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

function __handleTVSelect(itemCardData: ItemCardDataModel, action: string) {
  const truncatedImage =
    itemCardData.image.match(/original_untouched\/(.*?)\.jpg/)?.[1] ??
    itemCardData.image; // fallback in case match fails

  console.log("[ItemCardAddButtonDropdownContent] handleSelect: ", {
    ...itemCardData,
    image: truncatedImage,
    action,
  });
}

function __handleMovieSelect(
  itemCardData: ItemCardDataModel,
  action: string,
  results: OMDBResultsByIMDB
) {
  const truncatedImage =
    itemCardData.image.match(/\/(MV5B[^\/]+)\.jpg/)?.[1] ?? itemCardData.image;

  console.log("[ItemCardAddButtonDropdownContent] handleSelect: ", {
    ...itemCardData,
    image: truncatedImage,
    action,
    score: results.imdbRating,
  });
}

export default ItemCardAddButtonDropdown;
