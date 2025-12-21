import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import Link from "next/link";

const LinkWithTooltip = ({
  href,
  title,
  tooltipMessage,
  color,
}: {
  href: string;
  title: string;
  tooltipMessage: string;
  color: string;
}) => {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Link href={href} target="_blank" className={cn("font-black", color)}>
            {title}
          </Link>
        </TooltipTrigger>
        <TooltipContent>{tooltipMessage}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

export default LinkWithTooltip;
