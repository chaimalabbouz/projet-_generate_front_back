import React from 'react';
import Social from './Social';

interface SocialMediaCardProps {
  property1: "Hover" | "Normal";
  onClick?: () => void;
}

const SocialMediaCard: React.FC<SocialMediaCardProps> = ({ property1, onClick }) => {
  const isHover = property1 === "Hover";

  return (
    <div
      className={`flex flex-col items-center justify-center w-[48px] h-[48px] p-[15px] rounded-[4px] border border-solid border-[#ffffff] ${
        isHover
          ? 'bg-[#a53dff] shadow-[0px_12px_64px_rgba(28,25,25,0.12)]'
          : 'bg-[#ffffff]'
      }`}
      onClick={onClick}
    >
      <Social property1="Facebook" />
    </div>
  );
};

export default SocialMediaCard;