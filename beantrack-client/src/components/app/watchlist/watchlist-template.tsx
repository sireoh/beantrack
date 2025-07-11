"use client";

import { useStore } from "@/store";
import { WatchlistStatusTabs } from "./watchlist-status-tabs";
import WatchlistTable from "./watchlist-table/watchlist-table";

const WatchlistTemplate = ({
  type,
  status,
}: {
  type: string;
  status?: string | undefined;
}) => {
  const { user, loading } = useStore((state) => state.session);

  return (
    <>
      {/* Title */}
      <h1 className="mdl-style-header text-lg font-bold">
        Welcome to&nbsp;
        <span className="text-sky-400">
          {loading ? "..." : user?.username || "Guest"}
        </span>
        &apos;s {type === "tv" ? "TV" : "Movie"} List
      </h1>
      {/* End Title */}

      {/* Watchlist Status Tabs: Desktop */}
      <div className="hidden lg:flex">
        <WatchlistStatusTabs type={type} screenSize="desktop" />
      </div>
      {/* End Watchlist Status Tabs: Desktop */}

      {/* Watchlist Status Tabs: Mobile */}
      <div className="block lg:hidden">
        <WatchlistStatusTabs type={type} screenSize="mobile" />
      </div>
      {/* End Watchlist Status Tabs: Mobile */}

      {/* Watchlist Table: Desktop */}
      <div className="hidden lg:flex">
        <WatchlistTable type={type} status={status} />
      </div>
      {/* End Watchlist Status Tabs: Desktop */}

      {/* Watchlist Table: Mobile */}
      <div className="block lg:hidden">
        <WatchlistTable type={type} status={status} />
      </div>
      {/* End Watchlist Status Tabs: Mobile */}
    </>
  );
};

export default WatchlistTemplate;
