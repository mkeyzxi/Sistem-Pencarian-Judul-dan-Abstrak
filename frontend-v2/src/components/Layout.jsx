export default function Layout({children}) {
  return (
    <div className="rag-app">
      <header className="rag-header">
        <div className="flex items-center gap-3">
          <div className="ai-avatar overflow-hidden">
            <img
              src="/81827305_1278039172384147_8186309804793266176_n (1).jpg"
              alt="Logo"
              className="w-full h-full object-cover"
            />
          </div>
          <div className="flex flex-col">
            <span className="font-semibold text-(--color-navy) leading-tight">
              Sistem Pencarian Skripsi
            </span>
            <span className="text-xs text-(--color-text-secondary)">Teknik Informatika</span>
          </div>
        </div>
        <span className="hidden sm:inline">UIN Alauddin Makassar</span>
      </header>
      {children}
    </div>
  )
}
