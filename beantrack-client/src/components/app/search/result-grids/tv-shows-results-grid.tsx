import ItemCard from "@/components/app/item-card/item-card";
import { TVMazeResults } from "@/models";

export function TVShowsResultsGrid({ results }: { results: TVMazeResults }) {
  if (!results) return null;

  return (
    <>
      {results
        .filter((item) => !!item.show.externals?.imdb)
        .map(({ show }) => (
          <ItemCard
            key={show.externals?.imdb ?? show.name}
            imdb={show.externals?.imdb}
            title={show.name}
            image={show.image?.original ?? "/images/item-card-no-image.png"}
            score={show.rating?.average ?? "No Rating"}
            description={show.summary ?? "No description available."}
          />
        ))}
    </>
  );
}
