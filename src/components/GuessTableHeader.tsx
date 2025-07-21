'use client';

export default function GuessTableHeader() {
  return (
    <div className="grid grid-cols-6 gap-2 mb-4">
      <div className="bg-gray-800 text-white p-3 rounded text-center">
        <div className="font-bold text-sm">PLAYER</div>
      </div>
      <div className="bg-gray-800 text-white p-3 rounded text-center">
        <div className="font-bold text-sm">TEAM</div>
      </div>
      <div className="bg-gray-800 text-white p-3 rounded text-center">
        <div className="font-bold text-sm">POSITION</div>
      </div>
      <div className="bg-gray-800 text-white p-3 rounded text-center">
        <div className="font-bold text-sm">NATIONALITY</div>
      </div>
      <div className="bg-gray-800 text-white p-3 rounded text-center">
        <div className="font-bold text-sm">AGE</div>
      </div>
      <div className="bg-gray-800 text-white p-3 rounded text-center">
        <div className="font-bold text-sm">HEIGHT</div>
      </div>
    </div>
  );
}