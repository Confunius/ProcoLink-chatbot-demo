import React from "react";

export default function AdminFrom() {
  return (
    <div>
      <div className="flex p-6 h-96 bg-sidebar text-black">
        <div className="w-8/12">
          <div className="flex">
            <div className="mr-10 mb-4">
              <p className="text-background font-semibold mb-1 text-lg ">First Name: </p>
              <input className="border border-black p-1 bg-transparent" type="text" name="" id="" placeholder="First Name" />
            </div>

            <div className="">
              <p className="text-background font-semibold mb-1 text-lg ">Last Name: </p>
              <input className="border border-black p-1 bg-transparent" type="text" name="" id="" placeholder="Last Name" />
            </div>
          </div>

            <div className="mb-2">
              <p className="text-background font-semibold mb-1 text-lg ">Email: </p>
              <input className="border border-black p-1 w-full bg-transparent" type="text" name="" id="" placeholder="Email" />
            </div>
            <div className="mb-2">
              <p className="text-background font-semibold mb-1 text-lg ">Staff ID/Username: </p>
              <input className="border border-black p-1 w-full bg-transparent" type="text" name="" id="" placeholder="Staff ID / Username" />
            </div>
            <div className="mb-2">
              <p className="text-background font-semibold mb-1 text-lg ">Phone Number: </p>
              <input className="border border-black p-1 w-full bg-transparent" type="text" name="" id="" placeholder="Phone Number" />
            </div>
        
        </div>

        <div className="ml-36 mt-auto">
            <button className="bg-transparent font-semibold text-background border-4 border-background px-8 py-2">
                SAVE
            </button>
        </div>

      </div>
      
    </div>
  );
}
