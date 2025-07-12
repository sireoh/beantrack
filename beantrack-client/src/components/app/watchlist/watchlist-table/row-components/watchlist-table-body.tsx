import { TableBody } from "@/components/ui/table";
import { WatchlistItem } from "@/models";
import WatchlistTableRow from "../watchlist-row";

const WatchlistTableBody = ({
  screenSize,
  type,
  watchlist,
}: {
  screenSize: string;
  status?: string;
  type: string;
  watchlist: WatchlistItem[];
}) => {
  return (
    <TableBody>
      {watchlist.map((item, index) => (
        <WatchlistTableRow
          key={item.id + item.image}
          item={item}
          index={index}
          screenSize={screenSize}
          type={type}
        />
      ))}
    </TableBody>
  );
};

export default WatchlistTableBody;
