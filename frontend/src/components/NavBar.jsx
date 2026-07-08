import React from 'react'

export default function NavBar(){
  return (
    <header className="floating-navbar fixed top-4 left-1/2 -translate-x-1/2 w-[92%] max-w-6xl rounded-xl z-40 shadow-md">
      <nav className="flex items-center justify-between px-6 py-3">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-md bg-accent flex items-center justify-center text-black font-bold">A</div>
          <div className="text-white font-semibold">PredictMyCollege</div>
        </div>
        <ul className="flex items-center gap-6 text-gray-300">
          <li className="hover:text-white"><a href="#">Home</a></li>
          <li className="hover:text-white"><a href="#">Analyzer</a></li>
          <li className="hover:text-white"><a href="#">Dashboard</a></li>
          <li><button className="px-3 py-1 rounded-md bg-[var(--accent)] text-black font-medium">Sign In</button></li>
        </ul>
      </nav>
    </header>
  )
}
