import React from 'react';

interface ButtonProps {
  property1: "Right Icon Hover" | "Normal" | "Hover" | "Left Icon Normal" | "Left Icon Hover" | "Right Icon Normal" | "Border Normal Button" | "Letf Icon Border Button" | "Border Hover Button" | "Left Icon Border Hover Button" | "Right Icon Bordar normal" | "Right Icon Bordar Hover";
  button?: string;
  letSWorkTogether?: string;
  downloadCV?: string;
  onClick?: () => void;
}

const Button: React.FC<ButtonProps> = ({
  property1,
  button = "Button",
  letSWorkTogether = "Let’s work Together",
  downloadCV = "Download CV",
  onClick
}) => {
  const renderContent = () => {
    switch (property1) {
      case "Normal":
      case "Hover":
      case "Border Normal Button":
      case "Border Hover Button":
        return (
          <span className="text-white font-work-sans font-semibold text-[16px] leading-[24px]">
            {button}
          </span>
        );
      case "Right Icon Normal":
      case "Right Icon Hover":
      case "Right Icon Bordar normal":
      case "Right Icon Bordar Hover":
        return (
          <>
            <span className="text-white font-work-sans font-semibold text-[16px] leading-[24px]">
              {letSWorkTogether}
            </span>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 18L15 12L9 6" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </>
        );
      case "Left Icon Normal":
      case "Left Icon Hover":
      case "Letf Icon Border Button":
      case "Left Icon Border Hover Button":
        return (
          <>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 12H21M3 12L9 6M3 12L9 18" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span className="text-white font-work-sans font-semibold text-[16px] leading-[24px]">
              {downloadCV}
            </span>
          </>
        );
      default:
        return null;
    }
  };

  const getRootStyles = () => {
    switch (property1) {
      case "Normal":
      case "Hover":
        return "bg-[#a53dff]";
      case "Right Icon Normal":
      case "Right Icon Hover":
        return "bg-[#a53dff]";
      case "Left Icon Normal":
      case "Left Icon Hover":
        return "bg-[#a53dff]";
      case "Border Normal Button":
      case "Border Hover Button":
        return "bg-white border border-[#a53dff]";
      case "Letf Icon Border Button":
      case "Left Icon Border Hover Button":
        return "bg-white border border-[#a53dff]";
      case "Right Icon Bordar normal":
      case "Right Icon Bordar Hover":
        return "bg-white border border-[#a53dff]";
      default:
        return "";
    }
  };

  const getTextColor = () => {
    switch (property1) {
      case "Border Normal Button":
      case "Border Hover Button":
      case "Letf Icon Border Button":
      case "Left Icon Border Hover Button":
      case "Right Icon Bordar normal":
      case "Right Icon Bordar Hover":
        return "text-[#a53dff]";
      default:
        return "text-white";
    }
  };

  return (
    <button
      className={`flex items-center justify-center gap-[12px] p-[12px_24px] rounded-[4px] ${getRootStyles()}`}
      onClick={onClick}
    >
      {renderContent()}
    </button>
  );
};

export default Button;