import React from 'react';
import "../App.css"
import { Carousel } from 'flowbite-react';
import illustration from '/src/assets/illustration.png'
import illustration2 from '/src/assets/illustration2.png'
import illustration3 from '/src/assets/illustration3.png'

const Accueil = () => {
  return (
    <div className="bg-neutralSilver">
      <div className="px-4 lg:px-14 max-w-screen-2xl mx-auto min-h-screen h-screen">
        <Carousel className=' w-full  mx-auto'>
          <div className="my-28 md:my-8 py-12 flex flex-col md:flex-row-reverse items-center justify-between gap-12 ">
            <div>
                <img src={illustration} alt="" />
            </div>
            <div className='md:w-1/2'>
            <h1 className='text-5xl font-semibold mb-4 text-neutralDGrey md:w-3/4'>Bienvenue sur notre Platforme <span className=' text-brandPrimary leading-snug'> D'évaluation Intelligente  </span></h1>
                <p className='text-neutralGrey text-base mb-8'>
                Une solution innovante pour évaluer et améliorer les performances académiques.
            
                </p>
                <button className='btn-primary'>
                    Commencer

                </button>
            </div>
          </div>
          <div className="my-28 md:my-8 py-12 flex flex-col md:flex-row-reverse items-center justify-between gap-12 ">
            <div>
                <img src={illustration2} alt="" />
            </div>
            <div className='md:w-1/2'>
            <h1 className='text-5xl font-semibold mb-4 text-neutralDGrey md:w-3/4'>Ensemble, construisons un avenir où <span className=' text-brandPrimary leading-snug'>Chaque étudiant peut exceller.  </span></h1>
                <p className='text-neutralGrey text-base mb-8'>
                Une solution innovante pour évaluer et améliorer les performances académiques.
            
                </p>
                <button className='btn-primary'>
                    Commencer

                </button>
            </div>
          </div>
          <div className="my-28 md:my-8 py-12 flex flex-col md:flex-row-reverse items-center justify-between gap-12 ">
            <div>
                <img src={illustration3} alt="" />
            </div>
            <div className='md:w-1/2'>
            <h1 className='text-5xl font-semibold mb-4 text-neutralDGrey md:w-3/4'>L'avenir de l'éducation commence ici. <span className=' text-brandPrimary leading-snug'> Rejoignez la révolution intelligente. </span></h1>
                <p className='text-neutralGrey text-base mb-8'>
                Une solution innovante pour évaluer et améliorer les performances académiques.
            
                </p>
                <button className='btn-primary'>
                    Commencer

                </button>
            </div>
          </div>
        </Carousel>
      </div>
    </div>
  );
};

export default Accueil;
