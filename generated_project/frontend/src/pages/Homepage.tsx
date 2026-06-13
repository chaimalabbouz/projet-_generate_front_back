import React, { useEffect, useState } from 'react';
import AddressCard from '../components/AddressCard';
import Blog from '../components/Blog';
import Button from '../components/Button';
import Logo from '../components/Logo';
import Pagination from '../components/Pagination';
import Project from '../components/Project';
import SocialMediaCard from '../components/SocialMediaCard';
import WhatIDoCard from '../components/WhatIDoCard';
import WorkProcessCard from '../components/WorkProcessCard';

export default function Homepage() {
  const [scale, setScale] = useState(1);

  useEffect(() => {
    const updateScale = () => {
      const screenWidth = window.innerWidth;
      const designWidth = 1920;
      const newScale = Math.min(1, screenWidth / designWidth);
      setScale(newScale);
    };

    updateScale();
    window.addEventListener('resize', updateScale);
    return () => window.removeEventListener('resize', updateScale);
  }, []);

  return (
    <div
      className="w-full overflow-x-hidden flex justify-center bg-[#ffffff]"
      style={{ minHeight: `${8368 * scale}px` }}
    >
      <div
        className="relative flex-shrink-0"
        style={{
          width: `1920px`,
          height: `8368px`,
          transform: `scale(${scale})`,
          transformOrigin: 'top center',
        }}
      >
        {/* Section: BG */}
        <div id="figma-135-1114">
        <div className="relative">
          <div className="w-[1481px] h-[1481px] absolute top-[1671px] left-[388px]"></div>
          <div className="w-[1481px] h-[1482px] absolute top-[7452px] left-[388px]"></div>
          <div className="w-[581.52px] h-[466.22px] absolute top-[2269px] left-[61px]"></div>
          <div className="w-[581.52px] h-[466.22px] absolute top-[9056px] left-[0px]"></div>
          
          
        </div>
        </div>

        {/* Section: Frame 40 */}
        <div id="figma-135-727">
        <div className="flex flex-row justify-between gap-[385px] px-[300px] py-[20px] w-[1920px] h-fit bg-[#ffffff]">
          <div id="figma-135-728" className="w-fit h-fit">
          <Logo b="B" brooklyn="Brooklyn" />
        </div>
          <div className="flex flex-row w-fit h-fit">
            <div className="flex flex-row justify-center items-center gap-[10px] px-[24px] py-[12px] w-fit h-fit">
              <span className="font-['Work Sans'] text-[16px] font-medium text-[#333333] text-left leading-[24px] w-[46px] h-[24px]">Home</span>
            </div>
            <div className="flex flex-row justify-center items-center gap-[10px] px-[24px] py-[12px] w-fit h-fit">
              <span className="font-['Work Sans'] text-[16px] font-medium text-[#333333] text-left leading-[24px] w-[47px] h-[24px]">About</span>
            </div>
            <div className="flex flex-row justify-center items-center gap-[10px] px-[24px] py-[12px] w-fit h-fit">
              <span className="font-['Work Sans'] text-[16px] font-medium text-[#333333] text-left leading-[24px] w-[62px] h-[24px]">Process</span>
            </div>
            <div className="flex flex-row justify-center items-center gap-[10px] px-[24px] py-[12px] w-fit h-fit">
              <span className="font-['Work Sans'] text-[16px] font-medium text-[#333333] text-left leading-[24px] w-[68px] h-[24px]">Portfolio</span>
            </div>
            <div className="flex flex-row justify-center items-center gap-[10px] px-[24px] py-[12px] w-fit h-fit">
              <span className="font-['Work Sans'] text-[16px] font-medium text-[#333333] text-left leading-[24px] w-[34px] h-[24px]">Blog</span>
            </div>
            <div className="flex flex-row justify-center items-center gap-[10px] px-[24px] py-[12px] w-fit h-fit">
              <span className="font-['Work Sans'] text-[16px] font-medium text-[#333333] text-left leading-[24px] w-[66px] h-[24px]">Services</span>
            </div>
            <div id="figma-135-742" className="w-fit h-fit">
          <Button property1="Normal" button="Contact" />
        </div>
          </div>
        </div>
        </div>

        {/* Section: unsplash:wKOKidNT14w */}
        <div id="figma-135-710">
        <img src="/src/assets/c78149f6f59250b6b8cb1b0e75f260c837bd67f9.png" alt="unsplash:wKOKidNT14w" className="w-[536px] h-[636px] bg-[#ffffff] rounded-[25px] shadow-[0px_24px_116px_rgba(43,56,76,0.09)]" />
        </div>

        {/* Section: Frame 15 */}
        <div id="figma-135-704">
        <div className="flex flex-col gap-[24px] w-fit h-fit">
          <div className="flex flex-col gap-[16px] w-fit h-fit">
            <div className="flex flex-col w-fit h-fit">
              <span className="font-['Work Sans'] text-[72px] font-semibold text-[#132238] text-left leading-[84px] w-[579px] h-[168px]">Hello, I’m
        Brooklyn Gilbert</span>
            </div>
          </div>
          <span className="font-['Work Sans'] text-[18px] font-normal text-[#556070] text-left leading-[24px] w-[648px] h-[72px]">I'm a Freelance UI/UX Designer and Developer based in London, England. I strives to build immersive and beautiful web applications through carefully crafted code and user-centric design.</span>
          <div id="figma-135-709" className="w-fit h-fit">
          <Button  property1="Normal" button="Say Hello!" />
        </div>
        </div>
        </div>

        {/* Section: Rectangle 32 */}
        <div id="figma-135-702">
        <div className="w-[133px] h-[6px] bg-[#ffc8c8]"></div>
        </div>

        {/* Section: Rectangle 33 */}
        <div id="figma-135-703">
        <div className="w-[92px] h-[6px] bg-[#ffc8c8]"></div>
        </div>

        {/* Section: Frame 1 */}
        <div id="figma-135-711">
        <div className="flex flex-row justify-center items-center gap-[12px] w-fit h-fit bg-[rgba(237,216,255,0.5)] rounded-[6px] border-[1px] border-[#ffffff]">
          <div className="flex flex-col gap-[8px] w-fit h-fit">
            <span className="font-['Work Sans'] text-[32px] font-semibold text-[#424e60] text-center leading-[40px] w-[200px] h-[40px]">15 Y.</span>
            <span className="font-['Work Sans'] text-[16px] font-normal text-[#697484] text-center leading-[24px] w-[200px] h-[24px]">Experience</span>
          </div>
          <div className="w-[0px] h-[106px] border-[3px] border-[#ffffff]"></div>
          <div className="flex flex-col gap-[8px] w-fit h-fit">
            <span className="font-['Work Sans'] text-[32px] font-semibold text-[#424e60] text-center leading-[40px] w-[200px] h-[40px]">250+</span>
            <span className="font-['Work Sans'] text-[16px] font-normal text-[#697484] text-center leading-[24px] w-[200px] h-[24px]">Project Completed</span>
          </div>
          <div className="w-[0px] h-[106px] border-[3px] border-[#ffffff]"></div>
          <div className="flex flex-col gap-[8px] w-fit h-fit">
            <span className="font-['Work Sans'] text-[32px] font-semibold text-[#424e60] text-center leading-[40px] w-[200px] h-[40px]">58</span>
            <span className="font-['Work Sans'] text-[16px] font-normal text-[#697484] text-center leading-[24px] w-[200px] h-[24px]">Happy Client</span>
          </div>
        </div>
        </div>

        {/* Section: Frame 288 */}
        <div id="figma-231-1338">
        <div className="flex flex-col w-fit h-fit">
          <div className="h-[1608px] relative">
            <div className="flex flex-col gap-[10px] pl-[300px] pr-[300px] pt-[248px] pb-[140px] w-fit h-fit bg-[#f0f1f3] absolute top-[620px] left-[0px]">
              <div className="flex flex-row items-center gap-[143px] w-fit h-fit">
                <div className="flex flex-col gap-[24px] w-fit h-fit">
                  <span className="font-['Work Sans'] text-[48px] font-semibold text-[#132238] text-left leading-[56px] w-[323px] h-[56px]">Work Process</span>
                  <div className="flex flex-col gap-[16px] w-fit h-fit">
                    <span className="font-['Work Sans'] text-[18px] font-normal text-[#697484] text-left leading-[24px] w-[529px] h-[96px]">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla purus arcu, varius eget velit non, laoreet imperdiet orci. Mauris ultrices eget lorem ac vestibulum. Suspendis imperdiet,</span>
                    <span className="font-['Work Sans'] text-[18px] font-normal text-[#697484] text-left leading-[24px] w-[529px] h-[48px]">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla purus arcu, varius eget velit non.</span>
                  </div>
                </div>
                <div className="w-[648px] h-[600px] relative rounded-[12px]">
                  <div id="figma-135-788" className="w-fit h-fit absolute top-[300px] left-[0px]">
          <WorkProcessCard property1="Hover" researchText="2. Design" descriptionText="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla purus arcu." />
        </div>
                  <div id="figma-135-790" className="w-fit h-fit absolute top-[24px] left-[336px]">
          <WorkProcessCard property1="Hover" researchText="2. Analyze" descriptionText="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla purus arcu." />
        </div>
                  <div id="figma-135-791" className="w-fit h-fit absolute top-[324px] left-[336px]">
          <WorkProcessCard property1="Hover" researchText="4. Launch" descriptionText="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla purus arcu." />
        </div>
                  <div id="figma-135-787" className="w-fit h-fit absolute top-[0px] left-[0px]">
          <WorkProcessCard property1="Hover" researchText="1. Research" descriptionText="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla purus arcu." />
        </div>
                </div>
              </div>
            </div>
            <div className="flex flex-row justify-center items-center gap-[136px] p-[112px] w-fit h-fit bg-[#ffffff] absolute top-[0px] left-[300px] z-[11] rounded-[16px] shadow-[0px_36px_105px_rgba(43,56,76,0.1)]">
              <div className="relative">
                <div className="w-[424px] h-[468px] absolute top-[0px] left-[0px] rounded-[10px]">
                  <img src="/src/assets/3b89fbcc5d09a9dcfed718b9441002088571183e.png" alt="Rectangle 30" className="w-[424px] h-[468px] bg-[#f0f1f3] absolute top-[0px] left-[0px] rounded-[10px] border-[1px] border-[#f0f1f3]" />
                </div>
                <div id="figma-135-769" className="w-fit h-fit absolute top-[432px] left-[80px]">
          <SocialMediaCard property1="Normal" />
        </div>
              </div>
              <div className="flex flex-col gap-[32px] w-fit h-fit">
                <span className="font-['Work Sans'] text-[38px] font-semibold text-[#132238] text-left leading-[50px] w-[536px] h-[100px]">I am Professional User Experience Designer</span>
                <div className="flex flex-col gap-[16px] w-fit h-fit">
                  <span className="font-['Work Sans'] text-[18px] font-normal text-[#556070] text-left leading-[24px] w-[536px] h-[72px]">I design and develop services for customers specializing creating stylish, modern websites, web services and online stores. My passion is to design digital user experiences.</span>
                  <span className="font-['Work Sans'] text-[18px] font-normal text-[#556070] text-left leading-[24px] w-[536px] h-[48px]">I design and develop services for customers specializing creating stylish, modern websites, web services.</span>
                </div>
                <div className="flex flex-row gap-[16px] w-fit h-fit">
                  <div id="figma-135-776" className="w-fit h-fit">
          <Button property1="Normal" button="My Project" />
        </div>
                  <div id="figma-135-777" className="w-fit h-fit">
          <Button  property1="Normal" button="Download CV" />
        </div>
                </div>
              </div>
            </div>
          </div>
          <div className="flex flex-col justify-end items-center gap-[50px] py-[100px] w-fit h-fit">
            <div className="flex flex-col gap-[70px] w-fit h-fit">
              <div className="flex flex-col justify-between items-center gap-[24px] px-[300px] w-[1920px] h-[128px]">
                <span className="font-['Work Sans'] text-[48px] font-semibold text-[#132238] text-left leading-[56px] w-[205px] h-[56px]">Portfolio</span>
                <span className="font-['Work Sans'] text-[18px] font-normal text-[#87909d] text-center leading-[24px] w-[577px] h-[48px]">There are many variations of passages of Lorem Ipsum available,
        but the majority have suffered alteration.</span>
              </div>
              <div className="flex flex-col justify-center items-center gap-[24px] px-[300px] w-fit h-fit">
                <div className="flex flex-row gap-[24px] w-fit h-fit">
                  <div id="figma-135-799" className="w-fit h-fit">
          <Project property1="Normal" uIUXDESIGN="UI-UX DESIGN" productAdminDashboard="Product Admin Dashboard" vivamusEleifendConvallisAnteNonPharetraLiberoMolestieLaoreetDonecIdImperdietLacus="Vivamus eleifend convallis ante, non pharetra libero molestie laoreet. Donec id imperdiet lacus." button="Case Study" unsplash9anj7QWy2gUrl="/src/assets/8f107a905f0e2c2a0cc5bae15845adf0de3205ca.png" />
        </div>
                  <div id="figma-135-800" className="w-fit h-fit">
          <Project  property1="Normal" uIUXDESIGN="UI-UX DESIGN" productAdminDashboard="Product Admin Dashboard" vivamusEleifendConvallisAnteNonPharetraLiberoMolestieLaoreetDonecIdImperdietLacus="Vivamus eleifend convallis ante, non pharetra libero molestie laoreet. Donec id imperdiet lacus." button="Case Study" unsplash9anj7QWy2gUrl="/src/assets/f9342afb7c1cf7f650c9ef0b35c8f6585d27e980.png" />
        </div>
                  <div id="figma-135-801" className="w-fit h-fit">
          <Project  property1="Normal" uIUXDESIGN="UI-UX DESIGN" productAdminDashboard="Product Admin Dashboard" vivamusEleifendConvallisAnteNonPharetraLiberoMolestieLaoreetDonecIdImperdietLacus="Vivamus eleifend convallis ante, non pharetra libero molestie laoreet. Donec id imperdiet lacus." button="Case Study" unsplash9anj7QWy2gUrl="/src/assets/2da37f82fa800f0711d0ad48045ab742c6f8daf5.png" />
        </div>
                </div>
                <div className="flex flex-row gap-[24px] w-fit h-fit">
                  <div id="figma-135-803" className="w-fit h-fit">
          <Project property1="Normal"  uIUXDESIGN="UI-UX DESIGN" productAdminDashboard="Product Admin Dashboard" vivamusEleifendConvallisAnteNonPharetraLiberoMolestieLaoreetDonecIdImperdietLacus="Vivamus eleifend convallis ante, non pharetra libero molestie laoreet. Donec id imperdiet lacus." button="Case Study" unsplash9anj7QWy2gUrl="/src/assets/ead171064222333091f36ac1c03c25f06480e9df.png" />
        </div>
                  <div id="figma-135-804" className="w-fit h-fit">
          <Project  property1="Normal"  uIUXDESIGN="UI-UX DESIGN" productAdminDashboard="Product Admin Dashboard" vivamusEleifendConvallisAnteNonPharetraLiberoMolestieLaoreetDonecIdImperdietLacus="Vivamus eleifend convallis ante, non pharetra libero molestie laoreet. Donec id imperdiet lacus." button="Case Study" unsplash9anj7QWy2gUrl="/src/assets/01120caf35209da234d0ce9c533b0ea0cacd38d4.png" />
        </div>
                  <div id="figma-135-805" className="w-fit h-fit">
          <Project property1="Normal" uIUXDESIGN="UI-UX DESIGN" productAdminDashboard="Product Admin Dashboard" vivamusEleifendConvallisAnteNonPharetraLiberoMolestieLaoreetDonecIdImperdietLacus="Vivamus eleifend convallis ante, non pharetra libero molestie laoreet. Donec id imperdiet lacus." button="Case Study" unsplash9anj7QWy2gUrl="/src/assets/3da3ab315a91b5f2dd6f1061e5b0be3e60938f12.png" />
        </div>
                </div>
              </div>
            </div>
            <div id="figma-135-806" className="w-fit h-fit">
          <Button property1="Normal" button="More Project" />
        </div>
          </div>
          <div className="flex flex-col justify-center items-center gap-[32px] px-[650px] py-[100px] w-fit h-fit bg-[#132238]">
            <span className="font-['Work Sans'] text-[48px] font-semibold text-[#ffffff] text-center leading-[56px] w-[621px] h-[112px]">Do you have Project Idia?
        Let's discuss your project!</span>
            <span className="font-['Work Sans'] text-[18px] font-normal text-[#a5acb5] text-center leading-[24px] w-[581px] h-[48px]">There are many variations of passages of Lorem Ipsum available,
        but the majority have suffered alteration.</span>
            <div id="figma-135-811" className="w-fit h-fit">
          <Button property1="Normal" letSWorkTogether="Let’s work Together" />
        </div>
          </div>
          <div className="flex flex-col justify-end items-center gap-[24px] py-[100px] w-fit h-fit">
            <div className="flex flex-col justify-center items-center gap-[70px] px-[300px] w-fit h-fit">
              <div className="flex flex-col items-center gap-[24px] w-fit h-fit">
                <span className="font-['Poppins'] text-[48px] font-semibold text-[#132238] text-left leading-[56px] w-[108px] h-[56px]">Blog</span>
                <span className="font-['Public Sans'] text-[18px] font-normal text-[#87909d] text-center leading-[26px] w-[540px] h-[52px]">There are many variations of passages of Lorem Ipsum available,
        but the majority have suffered alteration.</span>
              </div>
              <div className="flex flex-row justify-center items-center gap-[24px] w-fit h-fit">
                <div id="figma-135-818" className="w-fit h-fit">
          <Blog  property1="Hover" _22Oct2020="22 Oct, 2020" value="/" _246Comments="246 Comments" loremIpsumDolorSitConseaNullaPurusArcu="Lorem ipsum dolor sit consea. Nulla purus arcu" unsplashHh0OAiyeF1YUrl="/src/assets/46c1b0b7047e0794dd8853d66cdde08771fd30d1.png" />
        </div>
                <div id="figma-135-819" className="w-fit h-fit">
          <Blog property1="Hover" _22Oct2020="22 Oct, 2020" value="/" _246Comments="246 Comments" loremIpsumDolorSitConseaNullaPurusArcu="Lorem ipsum dolor sit consea. Nulla purus arcu" unsplashHh0OAiyeF1YUrl="/src/assets/6256b708bb0c4a6fd8a44b369112956ce0963c34.png" />
        </div>
                <div id="figma-135-820" className="w-fit h-fit">
          <Blog  property1="Hover" _22Oct2020="22 Oct, 2020" value="/" _246Comments="246 Comments" loremIpsumDolorSitConseaNullaPurusArcu="Lorem ipsum dolor sit consea. Nulla purus arcu" unsplashHh0OAiyeF1YUrl="/src/assets/e2b8fe341e5180e7839d7d0d049b6900cd354219.png" />
        </div>
                <div id="figma-135-821" className="w-fit h-fit">
          <Blog property1="Hover" _22Oct2020="22 Oct, 2020" value="/" _246Comments="246 Comments" loremIpsumDolorSitConseaNullaPurusArcu="Lorem ipsum dolor sit consea. Nulla purus arcu" unsplashHh0OAiyeF1YUrl="/src/assets/d85394fd2c31f590ee6e19eb4d05f39feb09abd5.png" />
        </div>
              </div>
            </div>
            <div id="figma-135-822" className="w-fit h-fit">
          <Pagination />
        </div>
          </div>
          <div className="flex flex-row items-center gap-[143px] px-[300px] py-[150px] w-fit h-fit bg-[#f0f1f3]">
            <div className="flex flex-col gap-[50px] w-fit h-fit">
              <div className="flex flex-col gap-[24px] w-fit h-fit">
                <span className="font-['Work Sans'] text-[48px] font-semibold text-[#333333] text-left leading-[56px] w-[254px] h-[56px]">What I do?</span>
                <div className="flex flex-col gap-[16px] w-fit h-fit">
                  <span className="font-['Work Sans'] text-[18px] font-normal text-[#87909d] text-left leading-[24px] w-[529px] h-[96px]">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla purus arcu, varius eget velit non, laoreet imperdiet orci. Mauris ultrices eget lorem ac vestibulum. Suspendis imperdiet,</span>
                  <span className="font-['Work Sans'] text-[18px] font-normal text-[#87909d] text-left leading-[24px] w-[529px] h-[48px]">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla purus arcu, varius eget velit non.</span>
                </div>
              </div>
              <div id="figma-135-830" className="w-fit h-fit">
          <Button property1="Normal" button="Say Hello!" />
        </div>
            </div>
            <div className="flex flex-col gap-[24px] w-fit h-fit">
              <div id="figma-135-832" className="w-fit h-fit">
          <WhatIDoCard  property1="Normal" userExperienceUX="User Experience (UX)" loremIpsumDolorSitAmetConsecteturAdipiscingElitNullaPurusArcuVariusEgetVelitNonLaoreetImperdietOrciMaurisUltricesEgetLoremAcVestibulum="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla purus arcu, varius eget velit non, laoreet imperdiet orci. Mauris ultrices eget lorem ac vestibulum." />
        </div>
              <div id="figma-135-833" className="w-fit h-fit">
          <WhatIDoCard  property1="Normal" userExperienceUX="User Interface (UI)" loremIpsumDolorSitAmetConsecteturAdipiscingElitNullaPurusArcuVariusEgetVelitNonLaoreetImperdietOrciMaurisUltricesEgetLoremAcVestibulum="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla purus arcu, varius eget velit non, laoreet imperdiet orci. Mauris ultrices eget lorem ac vestibulum." />
        </div>
              <div id="figma-135-834" className="w-fit h-fit">
          <WhatIDoCard property1="Normal" userExperienceUX="Web Development" loremIpsumDolorSitAmetConsecteturAdipiscingElitNullaPurusArcuVariusEgetVelitNonLaoreetImperdietOrciMaurisUltricesEgetLoremAcVestibulum="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla purus arcu, varius eget velit non, laoreet imperdiet orci. Mauris ultrices eget lorem ac vestibulum." />
        </div>
            </div>
          </div>
          <div className="flex flex-col items-center gap-[24px] px-[300px] py-[100px] w-fit h-fit">
            <div className="flex flex-col justify-center items-center gap-[24px] w-fit h-fit">
              <span className="font-['Work Sans'] text-[48px] font-semibold text-[#132238] text-center leading-[56px] w-[327px] h-[56px]">Happy Clients</span>
              <span className="font-['Work Sans'] text-[18px] font-normal text-[#87909d] text-center leading-[24px] w-[577px] h-[48px]">There are many variations of passages of Lorem Ipsum available,
        but the majority have suffered alteration.</span>
            </div>
            <div className="flex flex-row gap-[24px] w-fit h-fit">
              <div className="grid grid-cols-2 w-[200px] h-[200px]">
                <div className="w-[35px] h-[35px] bg-[#b8bcc2]"></div>
                <div className="w-[5px] h-[34px] bg-[#b8bcc2]"></div>
                <div className="w-[23px] h-[23px] bg-[#b8bcc2]"></div>
                <div className="w-[23px] h-[23px] bg-[#b8bcc2]"></div>
                <div className="w-[22px] h-[33px] bg-[#b8bcc2]"></div>
                <div className="w-[21px] h-[23px] bg-[#b8bcc2]"></div>
              </div>
              <div className="w-[200px] h-[200px] relative">
                <div className="w-[140px] h-[35px] bg-[#b8bcc2] absolute top-[82px] left-[30px]"></div>
              </div>
              <div className="w-[200px] h-[200px] relative">
                <div className="w-[37px] h-[37px] bg-[#006699] absolute top-[82px] left-[133px]"></div>
                <div className="w-[63px] h-[25px] bg-[#000000] absolute top-[88px] left-[30px]"></div>
                <div className="w-[37px] h-[24px] bg-[#000000] absolute top-[89px] left-[91px]"></div>
                <div className="w-[26px] h-[25px] bg-[#ffffff] absolute top-[88px] left-[138px]"></div>
              </div>
              <div className="w-[200px] h-[200px] relative">
                <div className="w-[140px] h-[25px] bg-[#b8bcc2] absolute top-[94px] left-[30px]"></div>
                <div className="grid grid-cols-2 absolute top-[119.3px] left-[50px]">
                  <div className="w-[13.87px] h-[13.59px] bg-[#b8bcc2]"></div>
                  <div className="w-[67.55px] h-[15.13px] bg-[#b8bcc2]"></div>
                </div>
              </div>
              <div className="w-[200px] h-[200px] relative">
                <div className="w-[140px] h-[28px] bg-[#b8bcc2] absolute top-[86px] left-[30px]"></div>
              </div>
              <div className="w-[200px] h-[200px] relative">
                <div className="w-[140px] h-[42px] bg-[#b8bcc2] absolute top-[79px] left-[30px]"></div>
              </div>
            </div>
          </div>
          <div className="flex flex-col items-center gap-[50px] pl-[524px] pr-[524px] pb-[100px] w-fit h-fit">
            <div className="flex flex-col justify-center items-center gap-[70px] w-fit h-fit">
              <div className="flex flex-col items-center gap-[24px] w-fit h-fit">
                <span className="font-['Work Sans'] text-[48px] font-semibold text-[#333333] text-center leading-[56px] w-[274px] h-[56px]">Testimonial</span>
                <span className="font-['Work Sans'] text-[18px] font-normal text-[#87909d] text-center leading-[24px] w-[577px] h-[48px]">There are many variations of passages of Lorem Ipsum available,
        but the majority have suffered alteration.</span>
              </div>
              <div className="flex flex-col justify-center items-center gap-[24px] w-fit h-fit">
                <span className="font-['Work Sans'] text-[18px] font-medium text-[#2b384c] text-center leading-[24px] w-[872px] h-[96px]">“Nulla efficitur nisl sit amet velit malesuada dapibus. Duis mollis felis turpis, nec semper odio convallis at. Curabitur imperdiet semper arcu, a finibus arcu suscipit in. Donec quis placerat nibh. Maecenas est purus, eleifend ac cursus sed, tincidunt ut sapien.
        Morbi ornare elit at libero suscipit porta.”</span>
                <div className="flex flex-col justify-center items-center gap-[8px] w-fit h-fit">
                  <div className="flex flex-row justify-center items-center gap-[24px] w-fit h-fit">
                    <span className="font-['Poppins'] text-[18px] font-medium text-[#000000] text-left leading-[26px] w-[131px] h-[26px]">Esther Howard</span>
                  </div>
                  <span className="font-['Poppins'] text-[16px] font-light text-[#000000] text-left leading-[24px] w-[268px] h-[24px]">Managing Director, ABC company</span>
                </div>
              </div>
            </div>
            <div id="figma-135-874" className="w-fit h-fit">
          <Pagination />
        </div>
          </div>
          <div className="h-[990px] relative">
            <div className="absolute top-[660px] left-[0px]">
              <div className="w-[1920px] h-[330px] bg-[#2b384c] absolute top-[0px] left-[0px]"></div>
              <div className="flex flex-row justify-center items-center gap-[182px] px-[300px] w-fit h-[120px] bg-[#2b384c] absolute top-[160px] left-[0px]">
                <div id="figma-135-747" className="w-fit h-fit">
          <Logo b="B" brooklyn="Brooklyn" />
        </div>
                <div className="flex flex-row w-fit h-fit">
                  <div className="flex flex-row justify-center items-center gap-[10px] p-[12px] w-fit h-fit">
                    <span className="font-['Work Sans'] text-[16px] font-normal text-[#f0f1f3] text-left leading-[24px] w-[46px] h-[24px]">Home</span>
                  </div>
                  <div className="flex flex-row justify-center items-center gap-[10px] p-[12px] w-fit h-fit">
                    <span className="font-['Work Sans'] text-[16px] font-normal text-[#f0f1f3] text-left leading-[24px] w-[47px] h-[24px]">About</span>
                  </div>
                  <div className="flex flex-row justify-center items-center gap-[10px] p-[12px] w-fit h-fit">
                    <span className="font-['Work Sans'] text-[16px] font-normal text-[#f0f1f3] text-left leading-[24px] w-[66px] h-[24px]">Services</span>
                  </div>
                  <div className="flex flex-row justify-center items-center gap-[10px] p-[12px] w-fit h-fit">
                    <span className="font-['Work Sans'] text-[16px] font-normal text-[#f0f1f3] text-left leading-[24px] w-[61px] h-[24px]">Process</span>
                  </div>
                  <div className="flex flex-row justify-center items-center gap-[10px] p-[12px] w-fit h-fit">
                    <span className="font-['Work Sans'] text-[16px] font-normal text-[#f0f1f3] text-left leading-[24px] w-[67px] h-[24px]">Portfolio</span>
                  </div>
                  <div className="flex flex-row justify-center items-center gap-[10px] p-[12px] w-fit h-fit">
                    <span className="font-['Work Sans'] text-[16px] font-normal text-[#f0f1f3] text-left leading-[24px] w-[34px] h-[24px]">Blog</span>
                  </div>
                  <div className="flex flex-row justify-center items-center gap-[10px] p-[12px] w-fit h-fit">
                    <span className="font-['Work Sans'] text-[16px] font-normal text-[#f0f1f3] text-left leading-[24px] w-[62px] h-[24px]">Contact</span>
                  </div>
                </div>
                <span className="font-['Work Sans'] text-[16px] font-normal text-[#ffffff] text-left leading-[24px] w-[186px] h-[24px]">Copyright © 2022 Picto.</span>
              </div>
            </div>
            <div className="flex flex-row justify-between items-center gap-[24px] p-[88px] w-[1320px] h-fit bg-[#ffffff] absolute top-[0px] left-[300px] z-[11] rounded-[15px] shadow-[0px_59px_124px_rgba(0,0,0,0.12)]">
              <div className="flex flex-col gap-[35px] w-fit h-fit">
                <div className="flex flex-col gap-[16px] w-[481px] h-fit">
                  <span className="font-['Work Sans'] text-[38px] font-semibold text-[#132238] text-left leading-[50px] w-[481px] h-[50px]">Let’s discuss your Project</span>
                  <span className="font-['Work Sans'] text-[18px] font-normal text-[#87909d] text-left leading-[24px] w-[481px] h-[48px]">There are many variations of passages of Lorem Ipsu available. but the majority have suffered alte.</span>
                </div>
                <div className="flex flex-col gap-[12px] w-fit h-fit">
                  <div id="figma-135-881" className="w-[336px] h-fit">
          <AddressCard  property1="Normal" address="Address:" newMexico31134="New Mexico 31134" />
        </div>
                  <div id="figma-135-882" className="w-[336px] h-fit">
          <AddressCard  property1="Normal" address="My Email:" newMexico31134="mymail@mail.com" />
        </div>
                  <div id="figma-135-883" className="w-[336px] h-fit">
          <AddressCard property1="Normal" address="Call Me Now:" newMexico31134="00-1234 00000" />
        </div>
                </div>
                <div className="flex flex-row gap-[12px] w-fit h-fit">
                  <div id="figma-135-885" className="w-fit h-fit">
          <SocialMediaCard property1="Normal" />
        </div>
                  <div id="figma-135-886" className="w-fit h-fit">
          <SocialMediaCard property1="Normal" />
        </div>
                  <div id="figma-135-887" className="w-fit h-fit">
          <SocialMediaCard property1="Normal" />
        </div>
                  <div id="figma-135-888" className="w-fit h-fit">
          <SocialMediaCard property1="Normal" />
        </div>
                  <div id="figma-135-889" className="w-fit h-fit">
          <SocialMediaCard property1="Normal" />
        </div>
                </div>
              </div>
              <div className="flex flex-col gap-[50px] w-fit h-fit">
                <span className="font-['Work Sans'] text-[18px] font-normal text-[#87909d] text-left leading-[24px] w-[560px] h-[48px]">There are many variations of passages of Lorem Ipsu available,
but the majority have suffered alte.</span>
                <div className="flex flex-col gap-[50px] w-fit h-fit">

                  <div className="flex flex-col gap-[24px] w-fit h-fit">
                    <div className="flex flex-col gap-[14px] w-fit h-fit">
                      <span className="font-['Work Sans'] text-[18px] font-normal text-[#a53dff] text-center leading-[24px] w-[61px] h-[24px]">Name*</span>
                      <input 
                        type="text"
                        placeholder="Votre nom"
                        className="w-[560px] p-3 border-[1.5px] border-[#a53dff] rounded-md bg-white focus:outline-none focus:border-[#a53dff] focus:ring-1 focus:ring-[#a53dff]"
                        style={{ fontSize: '16px' }}
                      />
                    </div>
                    <div className="flex flex-col gap-[14px] w-fit h-fit">
                      <span className="font-['Work Sans'] text-[18px] font-normal text-[#697484] text-center leading-[24px] w-[59px] h-[24px]">Email*</span>
                      <input 
                        type="email"
                        placeholder="votre@email.com"
                        className="w-[560px] p-3 border-[1.5px] border-[#e6e8eb] rounded-md bg-white focus:outline-none focus:border-[#a53dff] focus:ring-1 focus:ring-[#a53dff]"
                        style={{ fontSize: '16px' }}
                      />
                    </div>
                    <div className="flex flex-col gap-[14px] w-fit h-fit">
                      <span className="font-['Work Sans'] text-[18px] font-normal text-[#697484] text-center leading-[24px] w-[76px] h-[24px]">Location</span>
                      <input 
                        type="text"
                        placeholder="Votre localisation"
                        className="w-[560px] p-3 border-[1.5px] border-[#e6e8eb] rounded-md bg-white focus:outline-none focus:border-[#a53dff] focus:ring-1 focus:ring-[#a53dff]"
                        style={{ fontSize: '16px' }}
                      />
                    </div>
                    <div className="flex flex-row gap-[24px] w-fit h-fit">
                      <div className="flex flex-col gap-[14px] w-fit h-fit">
                        <span className="font-['Work Sans'] text-[18px] font-normal text-[#697484] text-center leading-[24px] w-[73px] h-[24px]">Budget*</span>
                        <input 
                          type="text"
                          placeholder="Votre budget"
                          className="w-[200px] p-3 border-[1.5px] border-[#e6e8eb] rounded-md bg-white focus:outline-none focus:border-[#a53dff] focus:ring-1 focus:ring-[#a53dff]"
                          style={{ fontSize: '16px' }}
                        />
                      </div>
                      <div className="flex flex-col gap-[14px] w-fit h-fit">
                        <span className="font-['Work Sans'] text-[18px] font-normal text-[#697484] text-center leading-[24px] w-[78px] h-[24px]">Subject*</span>
                        <input 
                          type="text"
                          placeholder="Sujet"
                          className="w-[336px] p-3 border-[1.5px] border-[#e6e8eb] rounded-md bg-white focus:outline-none focus:border-[#a53dff] focus:ring-1 focus:ring-[#a53dff]"
                          style={{ fontSize: '16px' }}
                        />
                      </div>
                    </div>
 
                    <div className="flex flex-col gap-[14px] w-fit h-fit">
                      <span className="font-['Work Sans'] text-[18px] font-normal text-[#697484] text-center leading-[24px] w-[86px] h-[24px]">Message*</span>
                      <textarea 
                        placeholder="Votre message..."
                        rows={4}
                        className="w-[560px] p-3 border-[1.5px] border-[#e6e8eb] rounded-md bg-white focus:outline-none focus:border-[#a53dff] focus:ring-1 focus:ring-[#a53dff] resize-y"
                        style={{ fontSize: '16px' }}
                      />
                    </div>
                  </div>
                  <div id="figma-135-913" className="w-fit h-fit">
          <Button property1="Normal" letSWorkTogether="Submit" />
        </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        </div>

        {/* Section: Text */}
        <div id="figma-135-743">
        <span className="font-['Poppins'] text-[20px] font-semibold text-[#000000] text-left leading-[24px] w-[0px] h-[24px]"> </span>
        </div>

        

        
        {/* Section: Icon */}
        <div id="figma-135-723">
        <div className="flex flex-row gap-[10px] p-[16px] w-fit h-fit bg-[#ffffff] rounded-[4px]">
          <div className="grid grid-cols-2 w-[24px] h-[24px]">
            <div className="w-[24px] h-[24px]"></div>
            <div className="w-[16.5px] h-[16.99px] border-[1.5px] border-[#363a3d]"></div>
          </div>
        </div>
        </div>

        {/* Section: Icon */}
        <div id="figma-135-725">
        <div className="flex flex-row gap-[10px] p-[16px] w-fit h-fit bg-[#ffffff] rounded-[5px]">
          <div className="grid grid-cols-3 w-[24px] h-[24px]">
            <div className="w-[24px] h-[24px]"></div>
            <div className="w-[5.31px] h-[5.31px] border-[1.5px] border-[#1b1d1f]"></div>
            <div className="w-[3.19px] h-[3.19px] border-[1.5px] border-[#1b1d1f]"></div>
            <div className="w-[17.22px] h-[17.22px] border-[1.5px] border-[#1b1d1f]"></div>
          </div>
        </div>
        </div>


      </div>
    </div>
  );
}