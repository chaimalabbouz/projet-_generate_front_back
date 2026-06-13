import React from 'react';

interface SocialProps {
  property1: "Behance" | "Dribbble" | "Facebook" | "Instagram" | "Linkdin";
}

const Social: React.FC<SocialProps> = ({ property1 }) => {
  const renderIcon = () => {
    switch (property1) {
      case "Behance":
        return (
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 10C12.21 10 14 8.21 14 6C14 3.79 12.21 2 10 2C7.79 2 6 3.79 6 6C6 8.21 7.79 10 10 10ZM10 12C7.79 12 6 13.79 6 16V18H14V16C14 13.79 12.21 12 10 12Z" stroke="#697484" strokeWidth="0.07513006031513214" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        );
      case "Dribbble":
        return (
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 10C12.21 10 14 8.21 14 6C14 3.79 12.21 2 10 2C7.79 2 6 3.79 6 6C6 8.21 7.79 10 10 10ZM10 12C7.79 12 6 13.79 6 16V18H14V16C14 13.79 12.21 12 10 12Z" stroke="#697484" strokeWidth="0.009693052619695663" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        );
      case "Facebook":
        return (
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 10C12.21 10 14 8.21 14 6C14 3.79 12.21 2 10 2C7.79 2 6 3.79 6 6C6 8.21 7.79 10 10 10ZM10 12C7.79 12 6 13.79 6 16V18H14V16C14 13.79 12.21 12 10 12Z" stroke="#697484" strokeWidth="0.026061775162816048" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        );
      case "Instagram":
        return (
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 10C12.21 10 14 8.21 14 6C14 3.79 12.21 2 10 2C7.79 2 6 3.79 6 6C6 8.21 7.79 10 10 10ZM10 12C7.79 12 6 13.79 6 16V18H14V16C14 13.79 12.21 12 10 12Z" stroke="#697484" strokeWidth="0.0279999990016222" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        );
      case "Linkdin":
        return (
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 10C12.21 10 14 8.21 14 6C14 3.79 12.21 2 10 2C7.79 2 6 3.79 6 6C6 8.21 7.79 10 10 10ZM10 12C7.79 12 6 13.79 6 16V18H14V16C14 13.79 12.21 12 10 12Z" stroke="#697484" strokeWidth="0.04753820598125458" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className="w-[20px] h-[20px]">
      {renderIcon()}
    </div>
  );
};

export default Social;