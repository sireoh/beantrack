import Image from "next/image";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import ItemCardDescription from "./item-card-description";
import ItemCardAddButtonDropdown from "./item-card-add-button-dropdown";

export interface itemCardDataModel {
  imdb: string;
  title: string;
  image: string;
  score?: number;
  description?: string;
}

export default function ItemCard({
  imdb,
  title,
  image,
  score,
  description,
}: itemCardDataModel) {
  const itemCardData: itemCardDataModel = {
    imdb: imdb,
    title: title,
    image: image,
    score: score,
    description: description,
  };

  return (
    <Card className="flex flex-row rounded-sm p-2 gap-x-2">
      <div className="w-[90px] flex-shrink-0">
        <Link href="/40257-round-six">
          <Image src={image} alt={title} width={90} height={128} />
        </Link>
      </div>

      <CardContent className="flex flex-col p-0">
        <div className="flex justify-between items-start">
          <div className="flex items-center justify-between gap-x-4">
            <h2 className="text-xl font-semibold text-primary">
              <Link href="/40257-round-six">{title}</Link>
            </h2>
            {score && <span className="text-sm font-medium">{score}</span>}
            <ItemCardAddButtonDropdown itemCardData={itemCardData} />
          </div>
        </div>

        {description && <ItemCardDescription description={description} />}
      </CardContent>
    </Card>
  );
}
