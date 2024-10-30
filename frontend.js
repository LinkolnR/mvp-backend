import React from "react";

/* Don't forget to download the CSS file too 
OR remove the following line if you're already using Tailwind */

import "./style.css";

export const MyPlugin = () => {
  return (
    <div id="webcrumbs"> 
        	<div className="w-[900px] bg-white p-6 rounded-lg shadow-lg">
    	  <div className="flex justify-between items-center">
    	    <h1 className="text-2xl font-title text-neutral-950">Food Waste Dashboard</h1>
    	    <div className="flex items-center bg-purple-500 text-white rounded-full px-4 py-2">
    	      <span className='material-symbols-outlined mr-2'>trending_up</span>
    	      Chicken Waste From overproduction has been increasing for 7 Days.
    	    </div>
    	  </div>
    	  <div className="flex justify-between space-x-4 mt-6">
    	    {/* Waste Value */}
    	    <div className="w-[260px] bg-gray-50 rounded-md p-4 shadow">
    	      <div className="flex justify-between items-center">
    	        <p className="text-neutral-500">Waste Value</p>
    	        <p className="text-neutral-500 text-xs">12%</p>
    	      </div>
    	      <p className="text-2xl text-neutral-950 font-semibold">$1,724.96</p>
    	    </div>
    	    {/* Waste Weight */}
    	    <div className="w-[260px] bg-gray-50 rounded-md p-4 shadow">
    	      <div className="flex justify-between items-center">
    	        <p className="text-neutral-500">Waste Weight</p>
    	        <p className="text-neutral-500 text-xs">8%</p>
    	      </div>
    	      <p className="text-2xl text-neutral-950 font-semibold">2,421.93 LB</p>
    	    </div>
    	    {/* Waste Transactions */}
    	    <div className="w-[260px] bg-gray-50 rounded-md p-4 shadow">
    	      <div className="flex justify-between items-center">
    	        <p className="text-neutral-500">Waste Transactions</p>
    	        <p className="text-neutral-500 text-xs">8%</p>
    	      </div>
    	      <p className="text-2xl text-neutral-950 font-semibold">1,800</p>
    	    </div>
    	  </div>
    	  <div className="flex justify-between space-x-6 mt-6">
    	    {/* Top Wasted Foods */}
    	    <div className="w-[420px] bg-gray-50 rounded-md p-6 shadow">
    	      <h2 className="text-sm text-neutral-950 font-semibold mb-4">Top Wasted Foods</h2>
    	      <div className="space-y-2">
    	        {[
    	          { name: 'Vegetables', value: 550 },
    	          { name: 'Fruit', value: 500 },
    	          { name: 'Fish', value: 450 },
    	          { name: 'Eggs', value: 400 },
    	          { name: 'Hot Cereal', value: 350 },
    	          { name: 'Pasta', value: 300 },
    	          { name: 'Chicken', value: 600 },
    	        ].map(item => (
    	          <div key={item.name}>
    	            <span className="text-neutral-500">{item.name}</span>
    	            <div className="bg-purple-200 h-2 rounded-full mt-1">
    	              <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${item.value / 6}%` }}>
    	</div>
    	            </div>
    	          </div>
    	        ))}
    	      </div>
    	    </div>
    	    {/* Top Loss Reasons */}
    	    <div className="w-[420px] bg-gray-50 rounded-md p-6 shadow">
    	      <h2 className="text-sm text-neutral-950 font-semibold mb-4">Top Loss Reasons</h2>
    	      <div className="relative">
    	        <img
    	          src="https://tools-api.webcrumbs.org/image-placeholder/400/280/chart/1"
    	          className="object-cover w-[400px] h-[280px] rounded-md"
    	          alt="chart"
    	        />
    	      </div>
    	    </div>
    	  </div>
    	  {/* Photo Stream */}
    	  <div className="mt-8">
    	    <h2 className="text-xl font-title text-neutral-950">Photo Stream</h2>
    	    <p className="text-sm text-neutral-500 mb-4">Your Most Recent Transaction Photos</p>
    	    <div className="flex justify-between space-x-3">
    	      {[
    	        { id: 1, src: 'https://tools-api.webcrumbs.org/image-placeholder/180/120/food1/2' },
    	        { id: 2, src: 'https://tools-api.webcrumbs.org/image-placeholder/180/120/food2/2' },
    	        { id: 3, src: 'https://tools-api.webcrumbs.org/image-placeholder/180/120/food3/2' },
    	        { id: 4, src: 'https://tools-api.webcrumbs.org/image-placeholder/180/120/food4/2' },
    	      ].map(item => (
    	        <img
    	          key={item.id}
    	          src={item.src}
    	          alt={`photo-${item.id}`}
    	          className="object-cover w-[180px] h-[120px] rounded-md"
    	        />
    	      ))}
    	    </div>
    	  </div>
    	</div> 
        </div>
  )
}

