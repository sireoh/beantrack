"use client";

import { WatchlistStatusTabs } from "./watchlist-status-tabs";
import WatchlistTable from "./watchlist-table/watchlist-table";
import { useAuth } from "@/hooks/use-auth";

const WatchlistTemplate = ({ type }: { type: string }) => {
  const { user, loading } = useAuth();

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
        <WatchlistTable type={type} />
      </div>
      {/* End Watchlist Status Tabs: Desktop */}

      {/* Watchlist Table: Mobile */}
      <div className="block lg:hidden">
        <WatchlistTable type={type} />
      </div>
      {/* End Watchlist Status Tabs: Mobile */}
    </>
  );
};

export default WatchlistTemplate;
