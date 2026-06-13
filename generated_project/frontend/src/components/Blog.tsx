import React from 'react';

interface BlogProps {
  property1: "Normal" | "Hover";
  _22Oct2020: string;
  value: string;
  _246Comments: string;
  loremIpsumDolorSitConseaNullaPurusArcu: string;
  unsplashHh0OAiyeF1YUrl: string;
  onClick?: () => void;
}

const Blog: React.FC<BlogProps> = ({
  property1,
  _22Oct2020,
  value,
  _246Comments,
  loremIpsumDolorSitConseaNullaPurusArcu,
  unsplashHh0OAiyeF1YUrl,
  onClick
}) => {
  const isHover = property1 === "Hover";

  return (
    <div
      className={`w-[312px] h-[350px] flex flex-col items-center justify-center p-[0px_0px_24px_0px] gap-[24px] bg-[#ffffff] rounded-[8px] border-[1px] border-solid border-[#f0f1f3] ${isHover ? 'shadow-[0px_12px_64px_rgba(28,25,25,0.12)]' : ''}`}
      onClick={onClick}
    >
      <div
        className="w-[312px] h-[226px] bg-[#c4c4c4] border-[1px] border-solid border-[#f0f1f3]"
        style={{ backgroundImage: `url(${unsplashHh0OAiyeF1YUrl})`, backgroundSize: 'cover' }}
      />
      <div className="w-[264px] h-[76px] flex flex-col gap-[8px]">
        <div className="w-[206px] h-[20px] flex gap-[3px]">
          <p className="w-[88px] h-[20px] text-[14px] font-[400] leading-[20px] text-[#87909d]">
            {_22Oct2020}
          </p>
          <p className="w-[7px] h-[20px] text-[14px] font-[400] leading-[20px] text-[#87909d]">
            {value}
          </p>
          <p className="w-[105px] h-[20px] text-[14px] font-[400] leading-[20px] text-[#87909d]">
            {_246Comments}
          </p>
        </div>
        <p className="w-[264px] h-[48px] text-[18px] font-[500] leading-[24px] text-[#333333]">
          {loremIpsumDolorSitConseaNullaPurusArcu}
        </p>
      </div>
    </div>
  );
};

export default Blog;