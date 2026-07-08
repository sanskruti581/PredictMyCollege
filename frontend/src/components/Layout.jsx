import React from 'react'
import NavBar from './NavBar'
import GridOverlay from './GridOverlay'

export default function Layout({children}){
  return (
    <div className="min-h-screen relative overflow-hidden">
      <NavBar />
      <GridOverlay />
      <main className="relative z-10">{children}</main>
    </div>
  )
}
