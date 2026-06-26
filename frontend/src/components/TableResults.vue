<script setup>
import { ref, reactive } from 'vue'

defineProps({
  documents: {
    type: Array,
    default: () => []
  }
})

// State untuk track tombol copy mana yang baru saja disalin
const copiedCards = reactive(new Set())

/**
 * Salin teks abstrak ke clipboard dengan visual feedback.
 * Ganti icon menjadi checkmark selama 2 detik.
 */
const copyToClipboard = async (text, event, index) => {
  event.stopPropagation()
  try {
    await navigator.clipboard.writeText(text)
    copiedCards.add(index)
    setTimeout(() => {
      copiedCards.delete(index)
    }, 2000)
  } catch (err) {
    console.error('Gagal menyalin teks:', err)
  }
}

// State untuk track kartu mana yang expand
const expandedCards = ref(new Set())

const toggleExpand = (index) => {
  if (expandedCards.value.has(index)) {
    expandedCards.value.delete(index)
  } else {
    expandedCards.value.add(index)
  }
}

const isExpanded = (index) => expandedCards.value.has(index)

/**
 * Ambil skor relevansi dari dokumen.
 * Backend sekarang mengirim similarity_score di dalam metadata (0-100 float).
 * Format response: { page_content: "...", metadata: { similarity_score: 75.0, ... } }
 */
const getScore = (doc) => {
  const s = (doc.metadata && doc.metadata.similarity_score)
    ?? doc.similarity_score
    ?? doc.score
    ?? 0
  const num = Number(s) || 0
  // Score sudah 0-100 dari backend, clamp saja
  return Math.max(0, Math.min(100, num))
}

/** Format score ke integer persen. Score sudah 0-100. */
const formatPct = (v) => Math.round(v)

/**
 * Helper untuk ambil field dari doc.
 * Cek level doc dulu, lalu fallback ke doc.metadata.
 */
const getField = (doc, key, fallback = '') => {
  return doc[key] || (doc.metadata && doc.metadata[key]) || fallback
}

/** Helper untuk ambil isi abstrak dari doc. */
const getContent = (doc) => {
  return doc.page_content || doc.full_content || doc.content || ''
}
</script>

<template>
  <div class="space-y-4">
    <!-- Info text -->
    <p class="text-xs text-text-muted flex items-center !gap-1.5 !mb-2 !mt-1">
      <span class="material-symbols-outlined text-sm text-primary">info</span>
      Sistem menemukan {{ documents.length }} dokumen yang relevan.
    </p>

    <!-- Card List Container -->
    <div class="flex flex-col gap-4">
      <template v-for="(doc, index) in documents" :key="index">

        <!-- Document Card -->
        <div @click="toggleExpand(index)"
          class="flex flex-col bg-bg-elevated border border-border-subtle rounded-xl !p-4 !sm:p-5 transition-all duration-200 hover:border-primary/50 hover:bg-bg-elevated/80 cursor-pointer group">
          <!-- Card Header: Title & Score -->
          <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 !mb-3">
            <h3 class="text-sm sm:text-base font-bold text-primary leading-snug flex-1">
              <span class="text-text-muted mr-1.5">#{{ index + 1 }}</span>
              {{ getField(doc, 'judul', getField(doc, 'title', 'Judul Tidak Tersedia')) }}
            </h3>

            <!-- Relevance Badge -->
            <div
              class="flex items-center gap-2 bg-bg-surface !px-3 !py-1.5 rounded-full border border-border-subtle shrink-0">
              <div class="w-16 bg-[#1f1f1f] rounded-full h-1.5 overflow-hidden">
                <div class="progress-fill" :style="{ width: formatPct(getScore(doc)) + '%' }"></div>
              </div>
              <span class="text-xs font-bold text-text-base">{{ formatPct(getScore(doc)) }}%</span>
            </div>
          </div>

          <!-- Metadata Tags -->
          <div class="flex flex-wrap items-center gap-2 !mb-4">
            <span v-if="getField(doc, 'source')"
              class="inline-flex items-center gap-1 text-[11px] font-medium text-text-subdued bg-bg-surface !px-2 !py-1 rounded">
              <span class="material-symbols-outlined text-[14px]">description</span>
              {{ getField(doc, 'source') }}
            </span>
            <span v-if="getField(doc, 'tahun')"
              class="inline-flex items-center gap-1 text-[11px] font-medium text-text-subdued bg-bg-surface !px-2 !py-1 rounded">
              <span class="material-symbols-outlined text-[14px]">calendar_today</span>
              {{ getField(doc, 'tahun') }}
            </span>
            <span v-if="getField(doc, 'nama')"
              class="inline-flex items-center gap-1 text-[11px] font-medium text-text-subdued bg-bg-surface !px-2 !py-1 rounded">
              <span class="material-symbols-outlined text-[14px]">person</span>
              {{ getField(doc, 'nama') }}
            </span>
            <span v-if="getField(doc, 'pembimbing')"
              class="inline-flex items-center gap-1 text-[11px] font-medium text-text-subdued bg-bg-surface !px-2 !py-1 rounded">
              <span class="material-symbols-outlined text-[14px]">school</span>
              {{ getField(doc, 'pembimbing') }}
            </span>
          </div>

          <!-- Abstract Content with Line Clamp -->
          <div class="relative">
            <p class="text-sm text-text-subdued leading-relaxed whitespace-pre-wrap transition-all duration-300"
              :class="isExpanded(index) ? '' : 'line-clamp-3'">
              {{ getContent(doc) }}
            </p>
          </div>

          <!-- Card Footer: Actions -->
          <div class="flex items-center justify-between !mt-4 !pt-4 border-t border-border-subtle">
            <button class="flex items-center !gap-1.5 text-xs font-semibold transition-colors"
              :class="isExpanded(index) ? 'text-primary' : 'text-text-muted group-hover:text-text-base'">
              <span class="material-symbols-outlined text-[18px] transition-transform duration-300"
                :class="{ 'rotate-180': isExpanded(index) }">
                expand_more
              </span>
              {{ isExpanded(index) ? 'Tutup Detail' : 'Baca Selengkapnya' }}
            </button>

            <button v-if="isExpanded(index)" @click.stop="copyToClipboard(getContent(doc), $event, index)"
              class="flex items-center !gap-1.5 !px-3 !py-1.5 rounded text-xs font-medium transition-all duration-300"
              :class="copiedCards.has(index)
                ? 'bg-green-500/20 text-green-400'
                : 'bg-primary/10 hover:bg-primary/20 text-primary'">
              <span class="material-symbols-outlined text-[16px] transition-transform duration-300"
                :class="{ 'scale-110': copiedCards.has(index) }">
                {{ copiedCards.has(index) ? 'check' : 'content_copy' }}
              </span>
              {{ copiedCards.has(index) ? 'Tersalin!' : 'Salin Abstrak' }}
            </button>
          </div>
        </div>

      </template>
    </div>
  </div>
</template>

<style scoped>
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #1ed760, #17a84b);
  transition: width 500ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Animasi line-clamp transisi yang lebih halus */
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>