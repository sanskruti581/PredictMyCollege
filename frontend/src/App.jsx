import React from 'react'
import Layout from './components/Layout'
import Hero from './components/Hero'
import ResultsMatrix from './components/ResultsMatrix'
import CapFormBuilder from './components/CapFormBuilder'
import OptionFormExport from './components/OptionFormExport'
import { useState } from 'react'

export default function App(){
  const [prediction, setPrediction] = useState(null)
  const [choiceList, setChoiceList] = useState([])

  function handleHeroResult(res){
    setPrediction(res)
  }

  function addChoice(item){
    // prevent duplicates by choice_code
    if(!item || !item.choice_code) return
    if(choiceList.find(c=>c.choice_code === item.choice_code)) return
    setChoiceList(prev => [...prev, item])
  }

  function moveUp(idx){
    if(idx<=0) return
    setChoiceList(prev=>{
      const copy = [...prev]
      const tmp = copy[idx-1]
      copy[idx-1] = copy[idx]
      copy[idx] = tmp
      return copy
    })
  }

  function moveDown(idx){
    setChoiceList(prev=>{
      if(idx>=prev.length-1) return prev
      const copy = [...prev]
      const tmp = copy[idx+1]
      copy[idx+1] = copy[idx]
      copy[idx] = tmp
      return copy
    })
  }

  function removeChoice(idx){
    setChoiceList(prev=> prev.filter((_,i)=>i!==idx))
  }

  return (
    <Layout>
      <Hero onResult={handleHeroResult} />

      <div className="max-w-6xl mx-auto px-6">
        <ResultsMatrix result={prediction} onAdd={addChoice} />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CapFormBuilder choiceList={choiceList} onMoveUp={moveUp} onMoveDown={moveDown} onRemove={removeChoice} />
          <OptionFormExport choiceList={choiceList} />
        </div>
      </div>
    </Layout>
  )
}
