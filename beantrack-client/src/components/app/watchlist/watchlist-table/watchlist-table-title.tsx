import Link from "next/link";
import React from "react";
import { WatchlistTableTitleEditButton } from "./watchlist-table-title-edit-button";
import { MockDataInsideProps } from "./watchlist-table-body";

const WatchlistTableTitle = ({
  imdb,
  title,
}: Pick<MockDataInsideProps, "imdb" | "title">) => {
  return (
    <div className="flex justify-between items-center">
      <Link
        href={"https://www.imdb.com/title/" + imdb}
        target="_blank"
        className="text-primary font-semibold hover:underline">
        {title}
      </Link>

      <WatchlistTableTitleEditButton />
    </div>
  );
};

export default WatchlistTableTitle;
