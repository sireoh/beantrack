import { useState } from "react";
import { TableCell, TableRow } from "@/components/ui/table";
import { WatchlistItem } from "@/models";
import WatchlistTableStatus from "./row-components/watchlist-table-status";
import WatchlistTableImage from "./row-components/watchlist-table-image";
import WatchlistTableTitle from "./row-components/watchlist-table-title";
import WatchlistTableProgress from "./row-components/progress/watchlist-table-progress";

export const WatchlistTableRow = ({
  item,
  index,
  screenSize,
  type,
}: {
  item: WatchlistItem;
  index: number;
  screenSize: string;
  type: string;
}) => {
  const [currentProgress, setCurrentProgress] = useState(
    item.currentEpisodeIndex
  );

  const [currentStatus, setCurrentStatus] = useState(item.status);

  return (
    <TableRow key={item.id + item.image}>
      {/* Status */}
      <WatchlistTableStatus currentStatus={currentStatus} />

      {/* Number */}
      {screenSize === "desktop" && (
        <TableCell className="text-center w-[1px] px-2">
          <span className="text-sm">{index + 1}</span>
        </TableCell>
      )}

      {/* Image */}
      <TableCell className="w-[1px] p-0">
        <WatchlistTableImage
          image={item.image}
          title={item.title}
          type={type}
          imdb={item.imdb}
        />
      </TableCell>

      {/* Title */}
      <TableCell className="max-w-[180px] sm:max-w-none whitespace-nowrap overflow-hidden text-ellipsis">
        <WatchlistTableTitle
          item={item}
          currentProgress={currentProgress}
          setCurrentStatus={setCurrentStatus}
          type={type}
        />
      </TableCell>

      {/* Score */}
      {screenSize === "desktop" && (
        <TableCell className="text-center w-[1px] p-0">
          <span className="text-sm">{item.score}</span>
        </TableCell>
      )}

      {/* Progress */}
      {type === "tv" && (
        <TableCell className="text-center">
          <WatchlistTableProgress
            item={item}
            currentProgress={currentProgress}
            setCurrentProgress={setCurrentProgress}
          />
        </TableCell>
      )}
    </TableRow>
  );
};

export default WatchlistTableRow;
