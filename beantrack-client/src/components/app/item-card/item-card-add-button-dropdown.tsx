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
import { OMDBResultsByIMDB, TVMazeEpisodeModel } from "@/models";
import { fetchMovieByIMDB } from "@/utils/fetch-movie-by-imdb";
import { fetchTVShowByTVMazeID } from "@/utils/fetch-tv-show-by-tv-maze-id";
import { handleTVSelect } from "@/utils/handle-tv-select";

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

  async function _t(action: string) {
    const results: TVMazeEpisodeModel[] = await fetchTVShowByTVMazeID(
      itemCardData.id!
    );
    handleTVSelect(itemCardData, action, results);
  }

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
    search.currentType == "tv" ? _t(action) : _m(action);
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

function __handleMovieSelect(
  itemCardData: ItemCardDataModel,
  action: string,
  results: OMDBResultsByIMDB
) {
  const truncatedImage =
    itemCardData.image.match(/\/(MV5B[^\/]+)\.jpg/)?.[1] ?? itemCardData.image;
}

export default ItemCardAddButtonDropdown;
