import ItemCard from "@/components/app/item-card/item-card";
import { TVMazeResults, TVMazeTVShowModel } from "@/models";

export function TVShowsResultsGrid({ results }: { results: TVMazeResults }) {
  if (!results) return null;

  return (
    <>
      {results.map(({ show }) => (
        <ItemCard
          key={show.externals?.imdb ?? show.name}
          imdb={show.externals?.imdb}
          title={__formatTitleWithYear(show)}
          image={show.image?.original ?? "/images/item-card-no-image.png"}
          score={show.rating?.average ?? "No Rating"}
          description={show.summary ?? "No description available."}
        />
      ))}
    </>
  );
}

export function __formatTitleWithYear({
  name,
  premiered,
  ended,
}: TVMazeTVShowModel): string {
  const startYear = premiered?.split("-")[0] ?? "N/A";
  const endYear = ended?.split("-")[0] ?? "";

  if (startYear === endYear) return `${name} (${startYear})`;

  return `${name} (${startYear}${endYear ? `–${endYear}` : ""})`;
}
