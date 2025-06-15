import Link from "next/link";
import React from "react";
import { MockDataProps } from "./watchlist-table-body";
import { WatchlistTableTitleEditButton } from "./watchlist-table-title-edit-button";

const WatchlistTableTitle = ({ href, title }: MockDataProps) => {
  return (
    <div className="flex justify-between items-center">
      <Link
        href={href}
        target="_blank"
        className="text-primary font-semibold hover:underline">
        {title}
      </Link>

      <WatchlistTableTitleEditButton />
    </div>
  );
};

export default WatchlistTableTitle;
