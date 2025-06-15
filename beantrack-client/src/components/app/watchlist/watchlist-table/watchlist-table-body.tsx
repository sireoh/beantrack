import { TableBody, TableCell, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import WatchlistTableImage from "./watchlist-table-image";
import WatchlistTableTitle from "./watchlist-table-title";
import WatchlistTableProgress from "./watchlist-table-progress";

export interface MockDataProps {
  id: string;
  title: string;
  href: string;
  episodesSeen: number;
  totalEpisodes: number;
}

const mockdata: MockDataProps[] = [
  {
    id: "32925",
    title: "Hotel del Luna",
    href: "/32925-hotel-del-luna",
    episodesSeen: 0,
    totalEpisodes: 16,
  },
  {
    id: "750681",
    title: "Light Shop",
    href: "/750681-shop-of-the-lamp",
    episodesSeen: 0,
    totalEpisodes: 8,
  },
  {
    id: "34063",
    title: "Melting Me Softly",
    href: "/34063-let-me-melt",
    episodesSeen: 0,
    totalEpisodes: 16,
  },
  {
    id: "725367",
    title: "Queen of Tears",
    href: "/725367-untitled-park-ji-eun-project",
    episodesSeen: 6,
    totalEpisodes: 16,
  },
];

const WatchlistTableBody = () => {
  return (
    <TableBody>
      {mockdata.map((item) => (
        <TableRow key={item.id}>
          {/* Watchlist Table Status */}
          <TableCell className="bg-fuchsia-500 w-[1px] p-0"></TableCell>

          {/* Watchlist Table Number */}
          <TableCell className="text-end w-[1px] px-0">
            <span className="text-sm">1</span>
          </TableCell>

          {/* Watchlist Table Image */}
          <TableCell className="w-[1px] px-0">
            <WatchlistTableImage />
          </TableCell>

          {/* Watchlist Table Title */}
          <TableCell className="">
            <WatchlistTableTitle {...item} />
          </TableCell>

          {/* Watchlist Table Score */}
          <TableCell className="text-center w-[1px] px-0">
            <span className="text-sm">1</span>
          </TableCell>

          {/* Watchlist Table Progress */}
          <TableCell className="text-center">
            <WatchlistTableProgress {...item} />
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  );
};

export default WatchlistTableBody;
