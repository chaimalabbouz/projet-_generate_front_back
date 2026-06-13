import React from 'react';

interface AddressCardProps {
  property1: 'Hover' | 'Normal';
  address: string;
  newMexico31134: string;
}

const AddressCard: React.FC<AddressCardProps> = ({
  property1,
  address,
  newMexico31134,
}) => {
  const isHover = property1 === 'Hover';

  return (
    <div
      className={`flex items-center p-[24px] w-[336px] h-[96px] bg-[#ffffff] rounded-[10px] border border-solid border-[#ffffff] ${
        isHover ? 'shadow-[0_12px_64px_rgba(28,25,25,0.12)]' : ''
      }`}
    >
      <div
        className={`flex items-center justify-center w-[48px] h-[48px] p-[12px] rounded-[4px] border border-solid border-[#ffffff] ${
          isHover ? 'bg-[#a53dff]' : 'bg-[#edd8ff] bg-opacity-50'
        }`}
      >
        <svg 
          width="24" 
          height="24" 
          viewBox="0 0 24 24" 
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
        >
          <path 
            d="M12 12C13.6569 12 15 10.6569 15 9C15 7.34315 13.6569 6 12 6C10.3431 6 9 7.34315 9 9C9 10.6569 10.3431 12 12 12Z" 
            stroke={isHover ? "white" : "#a53dff"} 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
          />
          <path 
            d="M12 22C16 18 20 14.4183 20 10C20 5.58172 16.4183 2 12 2C7.58172 2 4 5.58172 4 10C4 14.4183 8 18 12 22Z" 
            stroke={isHover ? "white" : "#a53dff"} 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
          />
        </svg>
      </div>
      <div className="flex flex-col ml-[13px]">
        <span className="text-[14px] font-normal leading-[20px] text-[#424e60]">
          {address}
        </span>
        <span className="text-[16px] font-medium leading-[24px] text-[#132238]">
          {newMexico31134}
        </span>
      </div>
    </div>
  );
};

export default AddressCard;