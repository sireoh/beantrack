import { Button } from "@/components/ui/button";
import { Searchbar } from "../../app/searchbar";
import WelcomeMessage from "../../app/welcome-message";
import ProfilePictureDropdown from "../../app/profile-picture-dropdown";
import { SearchbarMobile } from "../../app/search-mobile";
import NavbarTitle, { NavbarTitleProps } from "./navbar-title";

interface MenuItem {
  title: string;
  url: string;
  description?: string;
  icon?: React.ReactNode;
  items?: MenuItem[];
}

interface NavbarProps {
  navbarTitle?: NavbarTitleProps;
  navbarRight?: {
    login: {
      title: string;
      url: string;
    };
  };
}

const Navbar = ({
  navbarTitle = {
    url: "/",
    src: "/images/peapod.png",
    alt: "logo",
    title: "BeanTrack",
  },
  navbarRight = {
    login: { title: "Login", url: "/login" },
  },
}: NavbarProps) => {
  return (
    <section className="py-4 bg-sky-800">
      {/* Desktop Menu */}
      <nav className="hidden lg:flex items-center justify-between">
        {/* NavbarLeft: Title and Logo */}
        <NavbarTitle {...navbarTitle} />

        {/* Right Side: Authenticated or Login */}
        <div className="flex items-center gap-4">
          {process.env.NEXT_PUBLIC_AUTHENTICATED === "true" ? (
            <>
              <Searchbar />
              <WelcomeMessage />
              <ProfilePictureDropdown />
            </>
          ) : (
            <Button asChild variant="outline" size="sm">
              <a href={navbarRight.login.url}>{navbarRight.login.title}</a>
            </Button>
          )}
        </div>
      </nav>

      {/* Mobile Menu */}
      <div className="block lg:hidden">
        <nav className="flex items-center justify-between">
          {/* NavbarLeft: Title and Logo */}
          <NavbarTitle {...navbarTitle} />

          {/* Right Side: Authenticated or Login */}
          <div className="flex items-center gap-4">
            {process.env.NEXT_PUBLIC_AUTHENTICATED === "true" ? (
              <>
                <SearchbarMobile />
                <ProfilePictureDropdown />
              </>
            ) : (
              <Button asChild variant="outline" size="sm">
                <a href={navbarRight.login.url}>{navbarRight.login.title}</a>
              </Button>
            )}
          </div>
        </nav>
      </div>
    </section>
  );
};

export { Navbar };
