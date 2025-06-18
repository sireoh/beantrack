import ProfilePictureDropdown from "../profile-picture/profile-picture-dropdown";
import { SearchbarMobileToggleButton } from "../search/search-mobile";
import { SearchbarDesktop } from "../search/searchbar-desktop";
import WelcomeMessage from "../welcome-message";

const NavRightAuth = () => {
  return (
    <>
      <div className="hidden lg:flex mr-2">
        <SearchbarDesktop />
        <WelcomeMessage />
        <ProfilePictureDropdown />
      </div>

      <div className="flex lg:hidden mr-2">
        <SearchbarMobileToggleButton />
        <ProfilePictureDropdown />
      </div>
    </>
  );
};

export default NavRightAuth;
