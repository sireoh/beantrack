import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { useStore } from "@/store";
import { SearchState } from "@/store/slices/search-slice";
import { Clapperboard, Tv } from "lucide-react";
import React from "react";

const options = [
  { label: "TV Shows", type: "tv", icon: <Tv /> },
  { label: "Movies", type: "movies", icon: <Clapperboard /> },
];

export default function SearchTypeSwitchDropdown() {
  const search = useStore((state) => state.search);
  const _padding = "py-0.5 px-1 m-0 h-auto w-auto min-h-0 min-w-0";
  const _main =
    "bg-white leading-none rounded-none text-xs light:bg-white dark:text-sky-600 text-sky-800 border-1 light:border-gray-400";
  const _effects =
    "hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 cursor-pointer";
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button className={cn(_padding, _main, _effects)}>
          {search.currentType === "tv" ? (
            <>
              {options[0].icon}
              {options[0].label}
            </>
          ) : (
            <>
              {options[1].icon}
              {options[1].label}
            </>
          )}
        </Button>
      </DropdownMenuTrigger>
      <TVMovieTypeSwitchDropdownContent searchState={search} />
    </DropdownMenu>
  );
}

function TVMovieTypeSwitchDropdownContent({
  searchState,
}: {
  searchState: SearchState;
}) {
  function updateCurrentType(new_type: string) {
    searchState.updateCurrentType(new_type);
  }
  return (
    <DropdownMenuContent className="w-48">
      {options.map(({ label, type, icon }) => (
        <DropdownMenuItem
          key={type}
          onSelect={() => updateCurrentType(type)}
          className="cursor-pointer">
          {icon}
          {label}
        </DropdownMenuItem>
      ))}
    </DropdownMenuContent>
  );
}
