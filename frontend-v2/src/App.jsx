import React, { useState, Suspense, lazy } from 'react';
import './index.css';
import { useSearch } from './hooks/useSearch';
import { LazyMotion, domAnimation } from 'framer-motion';
import SearchSlip from './components/SearchSlip';
import CatalogDrawer from './components/CatalogDrawer';
import MetricStrip from './components/MetricStrip';

const DetailPanel = lazy(() => import('./components/DetailPanel'));

function App() {
  const searchState = useSearch();
  const [selectedDoc, setSelectedDoc] = useState(null);

  const handleViewDetail = (document, method) => {
    setSelectedDoc({ document, method });
  };

  return (
    <LazyMotion features={domAnimation}>
      <div className="min-h-screen bg-[var(--color-kraft-bg)] text-[var(--color-ink)] font-body relative pb-16">
        {/* Header Area */}
        <header className="w-full max-w-5xl mx-auto px-4 sm:px-8 py-6">
          <h1 className="font-display text-2xl md:text-3xl font-bold text-[var(--color-ink)] mb-1">
            Laci Katalog Skripsi
          </h1>
          <p className="font-body text-sm text-[var(--color-ink-muted)]">
            Pencarian dan Perbandingan Metode RAG vs HyDE
          </p>
        </header>

        {/* Main Content */}
        <main>
          <SearchSlip 
            onSearch={searchState.performSearch} 
            activeQuery={searchState.query} 
          />
          
          <CatalogDrawer 
            resultsRag={searchState.resultsRag}
            resultsHyde={searchState.resultsHyde}
            isSearching={searchState.isSearching}
            error={searchState.error}
            onViewDetail={handleViewDetail}
          />
        </main>

        {/* Footer Metrics */}
        <MetricStrip 
          metricsRag={searchState.metricsRag}
          metricsHyde={searchState.metricsHyde}
          isSearching={searchState.isSearching}
        />

        {/* Slide-in Detail Panel */}
        {selectedDoc && (
          <Suspense fallback={null}>
            <DetailPanel 
              document={selectedDoc.document} 
              method={selectedDoc.method} 
              onClose={() => setSelectedDoc(null)} 
            />
          </Suspense>
        )}
      </div>
    </LazyMotion>
  );
}

export default App;
