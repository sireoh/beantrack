import { TableHead, TableHeader, TableRow } from "@/components/ui/table";

const WatchlistTableHeader = ({
  type,
  screenSize,
}: {
  type: string;
  screenSize: string;
}) => {
  return (
    <TableHeader>
      <TableRow className="bg-sky-800 hover:bg-sky-800">
        {/* Watchlist Table Status */}
        <TableHead className="w-[px] px-0.25">&nbsp;</TableHead>

        {/* Watchlist Table Number: Desktop Only*/}
        {screenSize == "desktop" && (
          <TableHead className="text-center w-[1px] p-0 text-white">
            #
          </TableHead>
        )}

        {/* Watchlist Table Others */}
        <TableHead className="text-center w-[60px] p-0 text-white">
          Image
        </TableHead>
        <TableHead className="lg:w-auto text-left text-white">
          {type == "tv" ? "TV Show" : "Movie"} Title
        </TableHead>

        {/* Score: Desktop Only */}
        {screenSize == "desktop" && (
          <TableHead className="text-center w-[1px] p-0 text-white">
            Score
          </TableHead>
        )}

        {type == "tv" && (
          <TableHead className="text-center w-[1px] p-0 text-white">
            Progress
          </TableHead>
        )}
      </TableRow>
    </TableHeader>
  );
};

export default WatchlistTableHeader;
