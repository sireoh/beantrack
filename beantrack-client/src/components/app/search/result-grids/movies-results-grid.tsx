import ItemCard from "../../item-card/item-card";
import { OMDBResults } from "@/models";

export function MoviesResultsGrid({ results }: { results: OMDBResults }) {
  if (!results) return null;

  const _s = [...(results.Search ?? [])].sort((a, b) => {
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
          title={item.Title}
          Year={item.Year}
          image={
            item.Poster !== "N/A"
              ? item.Poster
              : "/images/item-card-no-image.png"
          }
          isAdded={item.isAdded}
        />
      ))}
    </>
  );
}
