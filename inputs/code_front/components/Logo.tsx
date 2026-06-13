import React from 'react';

interface LogoProps {
  b: string;
  brooklyn: string;
}

const Logo: React.FC<LogoProps> = ({ b, brooklyn }) => {
  return (
    <div className="flex items-center justify-center gap-[12px] w-[208px] h-[56px]">
      <div className="flex flex-col items-center justify-center gap-[10px] w-[56px] h-[56px] bg-[#a53dff] rounded-[1000px] px-[20px] py-0">
        <span className="font-poppins font-medium text-[24px] leading-[56px] text-[#ffffff]">
          {b}
        </span>
      </div>
      <span className="font-work-sans font-semibold text-[32px] leading-[40px] text-[#132238]">
        {brooklyn}
      </span>
    </div>
  );
};

export default Logo;