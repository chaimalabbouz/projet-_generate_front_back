import React from 'react';

interface PaginationProps {
  // No props needed based on the payload
}

const Pagination: React.FC<PaginationProps> = () => {
  return (
    <div className="flex flex-row items-center gap-[12px] w-[70px] h-[8px]">
      <div className="w-[30px] h-[8px] bg-[#210c33] rounded-[100px]"></div>
      <div className="w-[8px] h-[8px] bg-[#c3c7ce] rounded-full"></div>
      <div className="w-[8px] h-[8px] bg-[#c3c7ce] rounded-full"></div>
    </div>
  );
};

export default Pagination;