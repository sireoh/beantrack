import Image from "next/image";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import ItemCardDescription from "./item-card-description";
import ItemCardAddButtonDropdown from "./item-card-add-button-dropdown";

export default function ItemCard({
  title = "Squid Game",
  image = "https://static.tvmaze.com/uploads/images/original_untouched/528/1321349.jpg",
  score = 8.4,
  description = "After a failed business venture, the debt-ridden chauffeur Seong Gi Hun lives his life gambling away the money he mooches off his elderly mother while failing to provide for her and his estranged daughter. When his mom is fat. After a failed business venture, the debt-ridden chauffeur Seong Gi Hun lives his life gambling away the money he mooches off his elderly mother while failing to provide for her and his estranged daughter. When his mom is fat.",
}: {
  title?: string;
  image?: string;
  score?: number;
  description?: string;
}) {
  return (
    <Card className="flex flex-row rounded-sm p-2 gap-x-2">
      <div className="w-[90px] flex-shrink-0">
        <Link href="/40257-round-six">
          <Image src={image} alt="Squid Game" width={90} height={128} />
        </Link>
      </div>

      <CardContent className="flex flex-col p-0">
        <div className="flex justify-between items-start">
          <div className="flex items-center justify-between gap-x-4">
            <h2 className="text-xl font-semibold text-primary">
              <Link href="/40257-round-six">{title}</Link>
            </h2>
            <span className="text-sm font-medium">{score}</span>
            <ItemCardAddButtonDropdown />
          </div>
        </div>

        <ItemCardDescription description={description} />
      </CardContent>
    </Card>
  );
}
