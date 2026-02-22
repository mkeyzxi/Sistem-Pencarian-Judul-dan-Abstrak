<script setup>
// Chat Area Component - Empty State
</script>

<template>
  <!-- Empty State / Welcome -->
  <div class="flex-1 flex flex-col items-center justify-center p-6 text-center space-y-6">
    <!-- Icon -->
    <div class="w-20 h-20 bg-primary/10 rounded-3xl flex items-center justify-center">
      <span class="material-symbols-outlined text-4xl text-primary">school</span>
    </div>

    <!-- Welcome Text -->
    <div>
      <h2 class="text-xl font-bold text-slate-900 dark:text-slate-100">Selamat datang di Chatbot Skripsi</h2>
      <p class="text-slate-500 dark:text-slate-400 mt-2 text-sm leading-relaxed">
        Temukan referensi penelitian tugas akhir mahasiswa Teknik Informatika dengan mudah.
        Silakan ketik topik atau kata kunci skripsi Anda.
      </p>
    </div>

    <!-- Example Buttons -->
    <div class="w-full grid grid-cols-1 gap-3">
      <button
        class="text-left p-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl hover:border-primary transition-colors group">
        <p class="text-xs font-semibold text-primary mb-1">Contoh Pencarian</p>
        <p class="text-sm text-slate-700 dark:text-slate-300">"Implementasi Algoritma CNN pada deteksi penyakit daun"
        </p>
      </button>
      <button
        class="text-left p-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl hover:border-primary transition-colors">
        <p class="text-xs font-semibold text-primary mb-1">Topik Populer</p>
        <p class="text-sm text-slate-700 dark:text-slate-300">"Analisis Sentimen Twitter menggunakan Naive Bayes"</p>
      </button>
    </div>
  </div>
</template>

<style scoped>
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}

.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
