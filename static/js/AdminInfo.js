import React, { useState } from 'react'
import men from '../assets/men.jpg'
export default function AdminInfo({onDataFromChild}) {
    const [isBan,setIsBan] = useState(false)
    const [isSuspend,setIsSuspend] = useState(false)

    const sendDataToParent = () => {
        onDataFromChild(false); 
      };
  return (
    <>
    <div className='w-140 h-80 mt-36 ml-24 bg-sidebar border border-gray-600 z-10 absolute'>
            <div className='flex'>
                <p className='text-lg font-bold p-2 text-background'>MORE DETAILS</p>
                <i onClick={sendDataToParent} className='bx bx-x text-5xl font-light ml-auto text-red-500 cursor-pointer'></i>
            </div>
            <div className='flex px-3'>
                <div className='flex flex-col items-center'>
                     <img src={men} alt="pic" className='h-48 w-48' />
                     <p className='mt-1 font-semibold'>Chris Wong</p>
                </div>

                <div className='ml-10 font-medium'>
                    <p className='mb-3'>Email:</p>
                    <p className='mb-3'>Gender:</p>
                    <p className='mb-3'>Staff ID:</p>
                    <p className='mb-3'>Phone No. :</p>
                    
                    {isBan || isSuspend && <p className=''>Status:</p>}
                    
                </div>

                <div className='ml-10 font-semibold'>
                    <p className='mb-3'>chriswong123@gmail.com</p>
                    <p className='mb-3'>Male</p>
                    <p className='mb-3'>ChrisW</p>
                    <p className='mb-3'>91234567</p>
                    
                    {isBan && <p className='text-red-500 font-bold'>BANNED</p>}
                    {isBan ? '': isSuspend ? <p>Suspend for 150 days</p>:''}
                </div>
            </div>
            {!isBan ? 
           <div className='flex justify-end mr-4 mb-6'>
           <button
                 onClick={()=>{setIsBan(true)}}
                 className="border border-black mr-4 w-28 h-10 font-semibold text-red-700 hover:bg-red-200"
               >
                 BAN
           </button>

           <button
                 onClick={()=> isSuspend?setIsSuspend(false):setIsSuspend(true)}
                 className="border border-black w-28 h-10 font-semibold text-black hover:bg-gray-200"
               >
                 {isSuspend ? 'UN-SUSPEND': 'SUSPEND'}
           </button>

           </div> : <p className='text-red-500 font-semibold text-lg ml-16 mt-4'>Admin has been banned. (Failure to comply our guidlines)</p>  
          }
           
    </div>
    </>
  )
}
