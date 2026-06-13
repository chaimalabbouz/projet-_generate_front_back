import React from 'react';
import Button from './Button';

interface ProjectProps {
  property1: "Hover" | "Normal";
  uIUXDESIGN: string;
  productAdminDashboard: string;
  vivamusEleifendConvallisAnteNonPharetraLiberoMolestieLaoreetDonecIdImperdietLacus: string;
  button: string;
  unsplash9anj7QWy2gUrl: string;
}

const Project: React.FC<ProjectProps> = ({
  property1,
  uIUXDESIGN,
  productAdminDashboard,
  vivamusEleifendConvallisAnteNonPharetraLiberoMolestieLaoreetDonecIdImperdietLacus,
  button,
  unsplash9anj7QWy2gUrl,
}) => {
  return (
    <div className="w-[424px] h-[476px] flex flex-col items-center justify-center bg-[#ffffff] rounded-[8px] border border-[#e6e8eb] border-solid p-[0px_0px_32px_0px] gap-[32px]">
      <div className="w-[424px] h-[248px] rounded-t-[8px]">
        <img
          src={unsplash9anj7QWy2gUrl}
          alt="Project"
          className="w-full h-full object-cover"
        />
      </div>
      <div className="w-[360px] h-[164px] flex flex-col gap-[20px]">
        <div className="w-[360px] h-[96px] flex flex-col gap-[12px]">
          <div className="w-[232px] h-[44px] flex flex-col gap-[4px]">
            <p className="text-[12px] font-[500] leading-[16px] text-[#87909d]">
              {uIUXDESIGN}
            </p>
            <h3 className="text-[18px] font-[600] leading-[24px] text-[#132238]">
              {productAdminDashboard}
            </h3>
          </div>
          <p className="text-[14px] font-[400] leading-[20px] text-[#556070]">
            {vivamusEleifendConvallisAnteNonPharetraLiberoMolestieLaoreetDonecIdImperdietLacus}
          </p>
        </div>
        <Button property1={property1} button={button} />
      </div>
    </div>
  );
};

export default Project;