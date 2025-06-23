"use client";

import { Table } from "@/components/ui/table";
import WatchlistTableHeader from "./watchlist-table-header";
import WatchlistTableBody from "./watchlist-table-body";
import useIsMobile, { ScreenSize } from "@/hooks/is-mobile";

const WatchlistTable = ({
  type,
  status,
}: {
  type: string;
  status: string | undefined;
}) => {
  const isMobile = useIsMobile(ScreenSize.TABLET);

  if (isMobile === null) return null; // optional: wait for screen size to be determined

  return (
    <Table className="light:bg-white">
      <WatchlistTableHeader
        type={type}
        screenSize={isMobile ? "mobile" : "desktop"}
      />
      <WatchlistTableBody
        screenSize={isMobile ? "mobile" : "desktop"}
        type={type}
        status={status}
      />
    </Table>
  );
};

export default WatchlistTable;
