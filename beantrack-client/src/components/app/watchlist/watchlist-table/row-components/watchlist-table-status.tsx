import { TableCell } from "@/components/ui/table";
import { cn } from "@/lib/utils";

const statusColors: Record<string, string> = {
  watching: "bg-green-600",
  completed: "bg-indigo-800",
  on_hold: "bg-yellow-400",
  dropped: "bg-red-800",
  plan_to_watch: "bg-gray-500",
};

const WatchlistTableStatus = ({ currentStatus }: { currentStatus: string }) => {
  return (
    <TableCell
      className={cn(statusColors[currentStatus], "w-[1px] p-0")}></TableCell>
  );
};

export default WatchlistTableStatus;
