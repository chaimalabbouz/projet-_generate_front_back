import React from 'react';

interface WorkProcessCardProps {
  property1: "Hover" | "Normal";
  researchText: string;
  descriptionText: string;
}

const WorkProcessCard: React.FC<WorkProcessCardProps> = ({
  property1,
  researchText,
  descriptionText
}) => {
  const isHover = property1 === "Hover";

  return (
    <div
      className={`flex flex-col p-[32px] gap-[32px] w-[312px] h-[276px] bg-white rounded-[12px] transition-all duration-300 ${
        isHover ? 'shadow-lg' : 'shadow'
      }`}
    >
      {/* Icône placeholder - vous pouvez remplacer par une image ou emoji */}
      <div className="flex items-center justify-center w-[72px] h-[72px] bg-purple-100 rounded-[6px]">
        <span className="text-3xl">📚</span>
      </div>
      
      {/* Texte */}
      <div className="flex flex-col gap-[12px]">
        <h3 className="font-semibold text-xl text-gray-900">
          {researchText}
        </h3>
        <p className="font-normal text-base text-gray-600">
          {descriptionText}
        </p>
      </div>
    </div>
  );
};

export default WorkProcessCard;