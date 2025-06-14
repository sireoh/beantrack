import { Button } from "@/components/ui/button";
import { Searchbar, SearchbarMobile } from "../app/searchbar";
import WelcomeMessage from "../app/welcome-message";
import ProfilePictureDropdown from "../app/profile-picture-dropdown";

interface MenuItem {
  title: string;
  url: string;
  description?: string;
  icon?: React.ReactNode;
  items?: MenuItem[];
}

interface NavbarProps {
  logo?: {
    url: string;
    src: string;
    alt: string;
    title: string;
  };
  menu?: MenuItem[];
  navbarRight?: {
    login: {
      title: string;
      url: string;
    };
  };
}

const Navbar = ({
  logo = {
    url: "/",
    src: "images/peapod.png",
    alt: "logo",
    title: "BeanTrack",
  },
  navbarRight = {
    login: { title: "Login", url: "/login" },
  },
}: NavbarProps) => {
  return (
    <section className="py-4">
      {/* Desktop Menu */}
      <nav className="hidden lg:flex items-center justify-between">
        {/* NavbarLeft: Logo */}
        <div className="flex items-center gap-2">
          <a href={logo.url} className="flex items-center gap-2">
            <img src={logo.src} className="max-h-8" alt={logo.alt} />
            <span className="text-lg font-semibold tracking-tighter">
              {logo.title}
            </span>
          </a>
        </div>

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
        <div className="flex items-center justify-between">
          {/* NavbarLeft: Logo */}
          <a href={logo.url} className="flex items-center gap-2">
            <img src={logo.src} className="max-h-8" alt={logo.alt} />
            <span className="text-lg font-semibold tracking-tighter">
              {logo.title}
            </span>
          </a>

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
        </div>
      </div>
    </section>
  );
};

export { Navbar };
