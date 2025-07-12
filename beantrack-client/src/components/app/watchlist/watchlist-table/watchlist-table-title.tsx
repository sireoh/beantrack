import Link from "next/link";
import React from "react";
import { EditButton } from "./edit-button-dropdown";
import { WatchlistItem } from "@/models";

const WatchlistTableTitle = ({
  item,
  type,
}: {
  item: WatchlistItem;
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
          item.episodes[item.currentEpisodeIndex] &&
          (() => {
            const episode = item.episodes[item.currentEpisodeIndex];
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
