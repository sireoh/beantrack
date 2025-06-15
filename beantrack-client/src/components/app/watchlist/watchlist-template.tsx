import React from "react";
import { WatchlistStatusTabs } from "./watchlist-status-tabs";
import WatchlistTable from "./watchlist-table/watchlist-table";

const WatchlistTemplate = ({ type }: { type: string }) => {
  return (
    <>
      {/* Title */}
      <h1 className="mdl-style-header text-lg font-bold">
        Welcome to&nbsp;
        <span className="text-sky-400">{process.env.NEXT_PUBLIC_USERNAME}</span>
        's {type == "tv" ? "TV" : "Movie"} List
      </h1>
      {/* End Title */}

      {/* Watchlist Status Tabs: Desktop */}
      <div className="hidden lg:flex">
        <WatchlistStatusTabs
          type={type == "tv" ? "tv" : "movie"}
          screenSize="desktop"
        />
      </div>
      {/* End Watchlist Status Tabs: Desktop */}

      {/* Watchlist Status Tabs: Mobile */}
      <div className="block lg:hidden">
        <WatchlistStatusTabs
          type={type == "tv" ? "tv" : "movie"}
          screenSize="mobile"
        />
      </div>
      {/* End Watchlist Status Tabs: Mobile */}

      {/* Watchlist Table: Desktop */}
      <div className="hidden lg:flex">
        <WatchlistTable />
      </div>
      {/* End Watchlist Status Tabs: Desktop */}

      {/* Watchlist Table: Mobile */}
      <div className="block lg:hidden">
        <WatchlistTable />
      </div>
      {/* End Watchlist Status Tabs: Mobile */}
    </>
  );
};

export default WatchlistTemplate;
