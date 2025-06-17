import ItemCard from "@/components/app/item-card/item-card";

export default function Home() {
  return (
    <div className="col-lg-8 col-md-8">
      <div className="m-t nav-active-border b-primary grid lg:grid-cols-2 gap-4">
        <ItemCard />
        <ItemCard />
        <ItemCard />
        <ItemCard />
        <ItemCard />
        <ItemCard />
        <ItemCard />
      </div>
    </div>
  );
}
