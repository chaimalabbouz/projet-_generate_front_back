import React from 'react';

interface WhatIDoCardProps {
  property1: "Hover" | "Normal";
  userExperienceUX: string;
  loremIpsumDolorSitAmetConsecteturAdipiscingElitNullaPurusArcuVariusEgetVelitNonLaoreetImperdietOrciMaurisUltricesEgetLoremAcVestibulum: string;
}

const WhatIDoCard: React.FC<WhatIDoCardProps> = ({
  property1,
  userExperienceUX,
  loremIpsumDolorSitAmetConsecteturAdipiscingElitNullaPurusArcuVariusEgetVelitNonLaoreetImperdietOrciMaurisUltricesEgetLoremAcVestibulum,
}) => {
  const isHover = property1 === "Hover";

  return (
    <div
      className={`w-[648px] h-[176px] p-[32px] flex flex-col items-center justify-between bg-[#ffffff] rounded-[6px] border border-solid border-[#000000] ${
        isHover ? 'shadow-[0_32px_96px_rgba(28,25,25,0.16)]' : ''
      }`}
    >
      {isHover && (
        <div className="absolute left-0 w-[5px] h-[176px] bg-[#a53dff]" />
      )}
      <h3 className="w-[584px] h-[24px] text-[24px] font-[600] leading-[24px] text-[#132238]">
        {userExperienceUX}
      </h3>
      <p className="w-[584px] h-[72px] text-[16px] font-[400] leading-[24px] text-[#424e60]">
        {loremIpsumDolorSitAmetConsecteturAdipiscingElitNullaPurusArcuVariusEgetVelitNonLaoreetImperdietOrciMaurisUltricesEgetLoremAcVestibulum}
      </p>
    </div>
  );
};

export default WhatIDoCard;