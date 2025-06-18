import { JSX } from "react";
import LinkWithTooltip from "../link-with-tooltip";

const _omdb = (
  <LinkWithTooltip
    href="https://www.omdbapi.com/"
    title="OMDb"
    tooltipMessage="The OMDb API is a RESTful web service to obtain movie information, all content and images on the site are contributed and maintained by our users."
    color="text-fuchsia-800 dark:text-fuchsia-600"
  />
);

const _cloudinary = (
  <LinkWithTooltip
    href="https://cloudinary.com/"
    title="Cloudinary"
    tooltipMessage="Cloudinary was founded in 2012 to solve tedious media management challenges. They provide a powerful service to manage, transform, and deliver digital media in modern applications."
    color="text-sky-800 dark:text-sky-600"
  />
);

const _tvmaze = (
  <LinkWithTooltip
    href="https://www.tvmaze.com/"
    title="TVmaze"
    tooltipMessage="The TVmaze API is a free, fast, and clean REST API that returns JSON and conforms to the HATEOAS and HAL principles, making it easy to add TV info to websites and apps."
    color="text-teal-800 dark:text-teal-600"
  />
);

const _list_data: (string | JSX.Element)[] = [
  "Create your own personalized watchlist",
  "Uses MongoDB as the main database",
  "Next.js framework for the client, Python FastAPI for the server",
  <>{_cloudinary} is used for storing profile pictures</>,
  <>
    Features the {_omdb} API for Movies, and the {_tvmaze} API for TV Shows
  </>,
];

export const DescriptionList = () => {
  return (
    <ul className="list-disc list-inside space-y-1 text-sm">
      {_list_data.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ul>
  );
};
