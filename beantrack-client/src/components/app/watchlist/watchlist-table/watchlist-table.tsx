"use client";

import { Table } from "@/components/ui/table";
import WatchlistTableHeader from "./watchlist-table-header";
import WatchlistTableBody from "./watchlist-table-body";

const WatchlistTable = () => {
  return (
    <Table className="light:bg-white">
      <WatchlistTableHeader />
      <WatchlistTableBody />
    </Table>
  );
};

export default WatchlistTable;
