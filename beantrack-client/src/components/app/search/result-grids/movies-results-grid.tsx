import useIsMobile, { ScreenSize } from "@/hooks/is-mobile";
import ItemCard from "../../item-card/item-card";
import { OMDBResults } from "@/models";

export function MoviesResultsGrid({ results }: { results: OMDBResults }) {
  const isMobile = useIsMobile(ScreenSize.MOBILE);

  const MAX_LENGTH = isMobile === null ? 0 : isMobile ? 45 : Infinity;

  if (!results) return null;

  const _s = [...(results.Search ?? [])]
    .filter((item) => !!item.imdbID)
    .sort((a, b) => {
      if (a.Type === "movie" && b.Type !== "movie") return -1;
      if (a.Type !== "movie" && b.Type === "movie") return 1;
      return 0;
    });

  return (
    <>
      {_s.map((item) => (
        <ItemCard
          key={item.imdbID}
          imdb={item.imdbID}
          title={__truncateLongTitle(item.Title, item.Year, MAX_LENGTH)}
          image={
            item.Poster !== "N/A"
              ? item.Poster
              : "/images/item-card-no-image.png"
          }
        />
      ))}
    </>
  );
}

function __truncateLongTitle(
  title: string,
  year: string,
  maxCharacters: number
): string {
  const yearPart = ` (${year})`;
  const maxTitleLength = maxCharacters - yearPart.length;

  if (title.length <= maxTitleLength) {
    return `${title}${yearPart}`;
  }

  const truncatedTitle = title.slice(0, maxTitleLength - 3).trimEnd(); // -3 for "..."
  return `${truncatedTitle} ...${yearPart}`;
}
