"use client";

import { Table } from "@/components/ui/table";
import WatchlistTableHeader from "./watchlist-table-header";
import WatchlistTableBody from "./row-components/watchlist-table-body";
import useIsMobile, { ScreenSize } from "@/hooks/is-mobile";
import { useStore } from "@/store";
import { useEffect } from "react";
import { fetchWatchlist } from "@/utils/fetch-watchlist";

const WatchlistTable = ({
  type,
  status,
}: {
  type: string;
  status: string | undefined;
}) => {
  const { tvlist, movieslist, updateTVList, updateMoviesList } = useStore(
    (state) => state.watchlists
  );
  useEffect(() => {
    fetchWatchlist(type, updateTVList, updateMoviesList, status);
  }, [status, type, updateMoviesList, updateTVList]);
  const isMobile = useIsMobile(ScreenSize.TABLET);
  if (isMobile === null) return null;

  return (
    <Table className="light:bg-white">
      <WatchlistTableHeader
        type={type}
        screenSize={isMobile ? "mobile" : "desktop"}
      />
      <WatchlistTableBody
        screenSize={isMobile ? "mobile" : "desktop"}
        type={type}
        watchlist={type === "tv" ? tvlist : movieslist}
      />
    </Table>
  );
};

export default WatchlistTable;
