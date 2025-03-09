import React from 'react'

const Exercices = () => {
  return (
    <div className='md:px-14 py-16 max-w-screen-2xl mx-auto'>
      <div className='text-center my-8'> 
      <h2 className='text-4xl text-neutralDGrey font-semibold md-2'>Dépôt ou Correction d'exercices</h2>
      <p>Des corrections instantanées, des conseils personnalisés : votre réussite commence ici.</p>
      <div className="my-12 flex flex-wrap justify-between items-center gap-8 w-full">
      <div className="text-center transform transition-all duration-300 ease-in-out ">
        <img src="/src/assets/illustration6.png" alt="" className="w-96 h-auto  hover:border-4 hover:border-brandPrimary hover:shadow-lg  hover:scale-120" />
        <p className="mt-2 text-lg font-semibold">Notre IA analyse, corrige et guide une </p>
        <p className="mt-2 text-lg font-semibold">révolution dans l'apprentissage .</p>
         </div>
         <div className="text-center transform transition-all duration-300 ease-in-out ">
        <img src="/src/assets/illustration7.png" alt="" className="w-96 h-auto  hover:border-4 hover:border-brandPrimary hover:shadow-lg  hover:scale-120" />
        <p className="mt-2 text-lg font-semibold">Rejoignez une communauté dynamique d'étudiants.</p>
        <p className="mt-2 text-lg font-semibold">et de professeurs passionnés par l'innovation.</p>
         </div>
         <div className="text-center transform transition-all duration-300 ease-in-out ">
        <img src="/src/assets/illustration8.png" alt="" className="w-96 h-auto  hover:border-4 hover:border-brandPrimary hover:shadow-lg  hover:scale-120" />
        <p className="mt-2 text-lg font-semibold">Votre succès académique, notre priorité.</p>
        <p className="mt-2 text-lg font-semibold"> Découvrez une nouvelle ère d'évaluation.</p>
         </div>
      </div>
      </div>
      <div className='text-center my-8'>
        <h2 className='text-4xl text-neutralDGrey font-semibold md-2'>Gérez toute vos devoirs dans un seul système</h2>
        
      </div>
    </div>
  )
}

export default Exercices
