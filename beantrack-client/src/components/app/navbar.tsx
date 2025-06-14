import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuList,
} from "@/components/ui/navigation-menu";
import { Searchbar } from "./searchbar";

const Navbar = () => {
  return (
    <NavigationMenu>
      <NavigationMenuList>
        <NavigationMenuItem>🍐 BeanTrack</NavigationMenuItem>
        <NavigationMenuItem>
          <Searchbar />
        </NavigationMenuItem>
        <NavigationMenuItem>
          Hello{" "}
          <span className="text-blue-500 dark:text-blue-400">
            {process.env.NEXT_PUBLIC_USERNAME}
          </span>
          !
        </NavigationMenuItem>
      </NavigationMenuList>
    </NavigationMenu>
  );
};

export default Navbar;
