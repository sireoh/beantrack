import React from "react";

const WelcomeMessage = () => {
  return (
    <span className="text-white">
      Hello&nbsp;
      <span className="text-red-500 font-bold">
        {process.env.NEXT_PUBLIC_USERNAME}
      </span>
      !
    </span>
  );
};

export default WelcomeMessage;
