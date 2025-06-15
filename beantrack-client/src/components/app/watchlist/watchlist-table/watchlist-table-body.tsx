import { TableBody, TableCell, TableRow } from "@/components/ui/table";
import WatchlistTableImage from "./watchlist-table-image";
import WatchlistTableTitle from "./watchlist-table-title";
import WatchlistTableProgress from "./watchlist-table-progress";
import res from "@/lib/mock-data/beantrack-mock-data.json";
import WatchlistTableStatus from "./watchlist-table-status";

export interface MockDataInsideProps {
  id: string;
  status: string;
  image: string;
  title: string;
  imdb: string;
  score: Float16Array;
  type: string;
  currentEpisode: number;
  totalEpisodes: number;
}

export interface MockDataOutsideProps {
  _id: {
    data: MockDataInsideProps[];
  };
}

const WatchlistTableBody = ({ screenSize }: { screenSize: string }) => {
  return (
    <TableBody>
      {res.data.map((item, index) => (
        <TableRow key={item.id}>
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
            <WatchlistTableImage image={item.image} title={item.title} />
          </TableCell>

          {/* Watchlist Table Title */}
          <TableCell className="max-w-[180px] sm:max-w-none whitespace-nowrap overflow-hidden text-ellipsis">
            <WatchlistTableTitle imdb={item.imdb} title={item.title} />
          </TableCell>

          {/* Watchlist Table Score: Desktop/Tablet Only*/}
          {screenSize == "desktop" && (
            <TableCell className="text-center w-[1px] p-0">
              <span className="text-sm">{item.score}</span>
            </TableCell>
          )}

          {/* Watchlist Table Progress */}
          <TableCell className="text-center">
            <WatchlistTableProgress
              currentEpisode={item.currentEpisode}
              totalEpisodes={item.totalEpisodes}
            />
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  );
};

export default WatchlistTableBody;
