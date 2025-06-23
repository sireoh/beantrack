import { TableBody, TableCell, TableRow } from "@/components/ui/table";
import WatchlistTableImage from "./watchlist-table-image";
import WatchlistTableTitle from "./watchlist-table-title";
import WatchlistTableProgress from "./watchlist-table-progress";
import WatchlistTableStatus from "./watchlist-table-status";
import { useEffect, useState } from "react";
import { WatchlistItem } from "@/models";

const WatchlistTableBody = ({
  screenSize,
  type,
}: {
  screenSize: string;
  type: string;
}) => {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);

  useEffect(() => {
    async function fetchWatchlist() {
      try {
        const res = await fetch("/api/tv_show", {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });

        if (!res.ok) {
          console.error("Failed to fetch TV show list");
          return;
        }

        const data = await res.json();
        console.log("Fetched watchlist:", data.watchlist || []);
        setWatchlist(data.watchlist || []);
      } catch (err) {
        console.error("Error fetching watchlist:", err);
      }
    }

    fetchWatchlist();
  }, []);

  return (
    <TableBody>
      {watchlist.map((item, index) => (
        <TableRow key={item.id + item.image}>
          {/* Watchlist Table Status */}
          <WatchlistTableStatus status={item.status} />

          {/* Watchlist Table Number */}
          {screenSize == "desktop" && (
            <TableCell className="text-center w-[1px] px-2">
              <span className="text-sm">{index + 1}</span>
            </TableCell>
          )}

          {/* Watchlist Table Image */}
          <TableCell className="w-[1px] p-0">
            <WatchlistTableImage
              image={item.image}
              title={item.title}
              type={type}
            />
          </TableCell>

          {/* Watchlist Table Title */}
          <TableCell className="max-w-[180px] sm:max-w-none whitespace-nowrap overflow-hidden text-ellipsis">
            <WatchlistTableTitle item={item} />
          </TableCell>

          {/* Watchlist Table Score: Desktop/Tablet Only*/}
          {screenSize == "desktop" && (
            <TableCell className="text-center w-[1px] p-0">
              <span className="text-sm">{item.score}</span>
            </TableCell>
          )}

          {/* Watchlist Table Progress */}
          <TableCell className="text-center">
            <WatchlistTableProgress item={item} />
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  );
};

export default WatchlistTableBody;
