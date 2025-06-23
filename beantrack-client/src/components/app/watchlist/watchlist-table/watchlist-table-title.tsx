import Link from "next/link";
import React from "react";
import { EditButton } from "./edit-button-dropdown";
import { WatchlistItem } from "@/models";

const WatchlistTableTitle = ({
  item,
  type,
}: {
  item: WatchlistItem;
  type: string;
}) => {
  return (
    <div className="flex justify-between items-center">
      <Link
        href={"https://www.imdb.com/title/" + item.imdb}
        target="_blank"
        className="text-primary font-semibold hover:underline">
        {item.title}
      </Link>

      <EditButton item={item} type={type} />
    </div>
  );
};

export default WatchlistTableTitle;
