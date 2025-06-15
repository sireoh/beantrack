"use client";

import { Table } from "@/components/ui/table";
import WatchlistTableHeader from "./watchlist-table-header";
import WatchlistTableBody from "./watchlist-table-body";
import { useEffect, useState } from "react";

enum ScreenSize {
  MOBILE = 768, // < 768px → mobile
  TABLET = 1024, // < 1024px → tablet
  DESKTOP = Infinity, // ≥ 1024px → desktop
}

const WatchlistTable = ({
  type,
  breakpoint = ScreenSize.TABLET,
}: {
  type: string;
  breakpoint: number;
}) => {
  const [isMobile, setIsMobile] = useState<boolean | null>(null);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < breakpoint);
    };

    handleResize(); // run once after mount

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [breakpoint]);

  // Optional: Render nothing until we know screen size
  if (isMobile === null) return null;

  return (
    <Table className="light:bg-white">
      <WatchlistTableHeader
        type={type}
        screenSize={isMobile ? "mobile" : "desktop"}
      />
      <WatchlistTableBody screenSize={isMobile ? "mobile" : "desktop"} />
    </Table>
  );
};

export default WatchlistTable;
