import Link from "next/link";
import Image from "next/image";
import { WatchlistItem } from "@/models";

const WatchlistTableImage = ({
  image,
  title,
}: Pick<WatchlistItem, "image" | "title">) => {
  const _url = `https://static.tvmaze.com/uploads/images/original_untouched${image}.jpg`;

  return (
    <div className="flex justify-center items-center">
      <Link href="#" className="link sort">
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
