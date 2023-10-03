import React from 'react'

export default function AdminPasswordForm() {
  return (
    <div>
      <div className="flex p-6 w-150 h-96 bg-sidebar text-black">
        
        <div className="w-8/12">
        <div className='flex'>
        <i class='bx bx-edit text-4xl mr-3 text-background'></i>
        <p className='mb-3 text-xl mt-1 font-bold text-background'>  EDIT PASSWORD </p>
        </div>
          <div className="mb-2">
              <p className="text-background font-semibold mb-1 text-lg ">Current Password: </p>
              <input className="border border-black p-1 w-full bg-transparent" type="text" name="" id="" placeholder="Current Password" />
            </div>
            <div className="mb-2">
              <p className="text-background font-semibold mb-1 text-lg ">New Password: </p>
              <input className="border border-black p-1 w-full bg-transparent" type="text" name="" id="" placeholder="New Password" />
            </div>
            <div className="">
              <p className="text-background font-semibold mb-1 text-lg ">Update Password: </p>
              <input className="border border-black p-1 w-full bg-transparent" type="text" name="" id="" placeholder="Update Password" />
            </div>
        
        </div>

        <div className="ml-16 mt-auto">
            <button className="bg-transparent font-semibold text-background border-4 border-background px-8 py-2">
                UPDATE
            </button>
        </div>

      </div>
      
    </div>
  )
}
