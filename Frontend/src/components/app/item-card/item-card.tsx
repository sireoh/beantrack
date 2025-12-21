import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import ItemCardDescription from "./item-card-description";
import ItemCardAddButtonDropdown from "./item-card-add-button-dropdown";
import SafeImage from "./safe-image";
import ItemCardTitle from "./item-card-title";
import { useStore } from "@/store";
import ItemCardEditButtonDropdown from "./item-card-edit-button-dropdown";

export interface ItemCardDataModel {
  id?: number;
  imdb: string;
  title: string;
  Year?: string;
  premiered?: string;
  ended?: string;
  image: string;
  score?: number;
  description?: string;
  isAdded?: boolean;
}

export default function ItemCard({
  id,
  imdb,
  title,
  Year,
  premiered,
  ended,
  image,
  score,
  description,
  isAdded,
}: ItemCardDataModel) {
  const search = useStore((state) => state.search);
  const _href = `https://www.imdb.com/title/${imdb}`;

  const itemCardData: ItemCardDataModel = {
    id: id,
    imdb: imdb,
    title: title,
    image: image,
    score: score,
    isAdded: isAdded,
  };

  return (
    <Card className="flex flex-row rounded-sm p-2 gap-x-2">
      <div className="w-[90px] flex-shrink-0">
        <Link href={_href}>
          <SafeImage src={image} alt={title} />
        </Link>
      </div>

      <CardContent className="flex flex-col p-0">
        <div className="flex justify-between items-start">
          <div className="flex items-center justify-between gap-x-4">
            <h2 className="text-xl font-semibold text-primary">
              <ItemCardTitle
                title={title}
                link={_href}
                Year={Year}
                premiered={premiered}
                ended={ended}
                isTV={search.currentType == "tv"}
              />
            </h2>
            {score && <span className="text-sm font-medium">{score}</span>}
            {isAdded ? (
              <ItemCardEditButtonDropdown
                item={itemCardData}
                type={search.currentType}
              />
            ) : (
              <ItemCardAddButtonDropdown itemCardData={itemCardData} />
            )}
          </div>
        </div>
        {description && <ItemCardDescription description={description} />}
      </CardContent>
    </Card>
  );
}
