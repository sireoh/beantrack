import React from "react";

const WelcomeMessage = () => {
  return (
    <>
      Hello
      <span className="text-blue-500 dark:text-blue-400">
        {process.env.NEXT_PUBLIC_USERNAME}!
      </span>
    </>
  );
};

export default WelcomeMessage;
