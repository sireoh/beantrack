import { TableHead, TableHeader, TableRow } from "@/components/ui/table";

const WatchlistTableHeader = () => {
  return (
    <TableHeader>
      <TableRow className="bg-sky-800 hover:bg-sky-800">
        {/* Watchlist Table Status */}
        <TableHead className="w-[1px] p-0">&nbsp;</TableHead>

        {/* Watchlist Table Number */}
        <TableHead className="text-end w-[1px] p-0 text-white">#</TableHead>

        {/* Watchlist Table Others */}
        <TableHead className="text-center w-[1px] p-0 text-white">
          Image
        </TableHead>
        <TableHead className="w-[300px] text-left text-white">Title</TableHead>
        <TableHead className="text-center w-[1px] p-0 text-white">
          Score
        </TableHead>
        <TableHead className="text-center w-[1px] p-0 text-white">
          Progress
        </TableHead>
      </TableRow>
    </TableHeader>
  );
};

export default WatchlistTableHeader;
