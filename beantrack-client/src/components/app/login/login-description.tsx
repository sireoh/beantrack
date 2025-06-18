import LinkWithTooltip from "../link-with-tooltip";
import Link from "next/link";
import { DescriptionList } from "./description-list";
import DeveloperSocials from "../developer-socials";

const _s = (
  <Link
    href="https://discordapp.com/users/342431329297629184"
    className="font-black text-orange-500 dark:text-orange-400">
    @sireoh
  </Link>
);

const _mal = (
  <LinkWithTooltip
    href="https://myanimelist.net/"
    title="MAL"
    tooltipMessage="My Anime List aka. MAL is an anime archival website that helps plan, track inform users about the anime they have watched."
    color="text-sky-800 dark:text-sky-600"
  />
);

const LoginDescription = () => {
  return (
    <>
      {/* Signup Description */}
      <div className="hidden lg:flex items-center justify-center p-8">
        <div className="w-full max-w-md space-y-6">
          <h5 className="text-2xl font-semibold">Welcome to BeanTrack!</h5>
          <p className="font-medium">
            BeanTrack is a private members-only TVShow and Movie tracking
            platform. Please contact {_s} on Discord to request an account.
          </p>
          <p>
            This website was first built on August 8, 2024 by Vincent Fung
            because he wanted his own version {_mal}, but for TV Shows and
            Movies.
          </p>
          <DescriptionList />
          <DeveloperSocials />
        </div>
      </div>
    </>
  );
};

export default LoginDescription;
