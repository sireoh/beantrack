import ItemCard from "@/components/app/item-card/item-card";
import { TVMazeResults } from "@/models";

export function TVShowsResultsGrid({ results }: { results: TVMazeResults }) {
  if (!results) return null;

  return (
    <>
      {results.map(({ show }) => (
        <ItemCard
          key={show.externals?.imdb ?? show.name}
          id={show.id}
          imdb={show.externals?.imdb}
          title={show.name}
          premiered={show.premiered}
          ended={show.ended}
          image={show.image?.original ?? "/images/item-card-no-image.png"}
          score={show.rating?.average ?? "No Rating"}
          description={show.summary ?? "No description available."}
        />
      ))}
    </>
  );
}
