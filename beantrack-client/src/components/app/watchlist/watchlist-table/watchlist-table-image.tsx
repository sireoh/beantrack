import Link from "next/link";
import Image from "next/image";

const WatchlistTableImage = ({
  image,
  title,
  type,
  imdb,
}: {
  image: string;
  title: string;
  type: string;
  imdb: string;
}) => {
  const _url =
    type == "tv"
      ? `https://static.tvmaze.com/uploads/images/original_untouched/${image}.jpg`
      : `https://m.media-amazon.com/images/${image}.jpg`;

  const _href = `https://www.imdb.com/title/${imdb}`;

  return (
    <div className="flex justify-center items-center">
      <Link href={_href} className="link sort">
        <Image
          src={_url}
          alt={title}
          width={60}
          height={68}
          className="hover-info image"
        />
      </Link>
    </div>
  );
};

export default WatchlistTableImage;
