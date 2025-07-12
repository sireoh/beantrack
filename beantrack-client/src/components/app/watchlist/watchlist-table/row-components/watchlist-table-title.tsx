import Link from "next/link";
import React, { SetStateAction } from "react";
import { EditButton } from "./edit-button-dropdown";
import { WatchlistItem } from "@/models";

const WatchlistTableTitle = ({
  item,
  currentProgress,
  type,
}: {
  item: WatchlistItem;
  currentProgress: number;
  type: string;
}) => {
  return (
    <div className="flex justify-between items-center">
      <div>
        <Link
          href={"https://www.imdb.com/title/" + item.imdb}
          target="_blank"
          className="text-primary font-semibold hover:underline">
          {item.title}
        </Link>
        {item.episodes &&
          item.episodes[currentProgress] &&
          (() => {
            const episode = item.episodes[currentProgress];
            const lastEpisode = item.episodes[item.episodes.length - 1];
            const code = episode.code;
            const name = episode.name;

            if (item.status === "completed") {
              return (
                <p className="text-sm text-muted-foreground">{`${lastEpisode.code} ${lastEpisode.name}`}</p>
              );
            }

            return (
              <p className="text-sm text-muted-foreground">{`${code} ${name}`}</p>
            );
          })()}
      </div>

      <EditButton item={item} type={type} />
    </div>
  );
};

export default WatchlistTableTitle;
