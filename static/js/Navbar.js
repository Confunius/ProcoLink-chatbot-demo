import React from "react";
import logo from "../assets/logo.png";
export default function Navbar() {
  return (
    <div className="h-20 text-white bg-nav flex items-center px-4">
      <img src={logo} alt="" className="h-12 w-12 mr-5" />
      <div className="font-bold mt-2">ECOFASHION HUB ADMIN</div>
      <div className="relative">
      <input
        type="text"
        placeholder="CUSTOMER RECORDS"
        className="h-12 w-96 bg-transparent px-2 placeholder-background border-4 border-white ml-6 focus:border-white"
      /><i class='bx bx-search text-4xl absolute right-2 top-2 z-20'></i>
      </div>
      <div className="ml-auto flex">
        <i className="bx bx-user-circle mr-2 text-4xl text-black"></i>
        <div className="font-bold mt-2">ADMIN</div>
        <i className="bx bx-chevron-down text-2xl mt-2 text-black"></i>
      </div>
    </div>
  );
}
