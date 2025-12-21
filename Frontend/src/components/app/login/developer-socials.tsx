import React from "react";
import {
  FaGithub,
  FaXTwitter,
  FaInstagram,
  FaLinkedin,
  FaBluesky,
  FaBriefcase,
} from "react-icons/fa6";

type Social = {
  name: string;
  href: string;
  icon: React.ElementType;
};

const socials: Social[] = [
  {
    name: "GitHub",
    href: "https://Fagithub.com/sireoh",
    icon: FaGithub,
  },
  {
    name: "LinkedIn",
    href: "https://www.linkedin.com/in/vincent-fung-123324231/",
    icon: FaLinkedin,
  },
  {
    name: "Portfolio Website",
    href: "http://vincef.cc/",
    icon: FaBriefcase,
  },
  {
    name: "Instagram",
    href: "https://www.instagram.com/sireohseo/",
    icon: FaInstagram,
  },
  {
    name: "Twitter",
    href: "https://x.com/kimerura/",
    icon: FaXTwitter,
  },
  {
    name: "Origami",
    href: "https://bsky.app/profile/kiseo.bsky.social",
    icon: FaBluesky,
  },
];

const DeveloperSocials = () => {
  return (
    <div className="flex space-x-4">
      {socials.map((social) => {
        const Icon = social.icon;
        return (
          <a
            key={social.name}
            href={social.href}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={social.name}>
            <Icon
              size={32}
              strokeWidth={3}
              className="mt-1 lg:mt-3 text-sky-800 dark:text-sky-600 transition-transform hover:scale-110"
            />
          </a>
        );
      })}
    </div>
  );
};

export default DeveloperSocials;
