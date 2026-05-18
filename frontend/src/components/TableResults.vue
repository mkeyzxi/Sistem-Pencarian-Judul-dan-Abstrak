<script setup>
import { ref } from 'vue'

defineProps({
  documents: {
    type: Array,
    default: () => []
  }
})

// State untuk track row mana yang expand
const expandedRows = ref(new Set())

const toggleExpand = (index) => {
  if (expandedRows.value.has(index)) {
    expandedRows.value.delete(index)
  } else {
    expandedRows.value.add(index)
  }
}

const isExpanded = (index) => expandedRows.value.has(index)
</script>

<template>
  <div class="space-y-3">
    <!-- Info text -->
    <p class="text-xs text-text-muted flex items-center gap-1">
      <span class="material-symbols-outlined text-sm">info</span>
      Klik baris untuk melihat abstrak lengkap
    </p>

    <!-- Table -->
    <div class="overflow-x-auto rounded-lg border border-border-subtle">
      <table class="w-full text-xs sm:text-sm">
        <!-- Header -->
        <thead>
          <tr class="bg-primary text-black border-b border-border-subtle">
            <th class="px-3 py-2.5 text-left font-bold w-8">#</th>
            <th class="px-3 py-2.5 text-left font-bold">Judul</th>
            <th class="px-3 py-2.5 text-left font-bold">Sumber</th>
            <th class="px-3 py-2.5 text-left font-bold">Ringkasan</th>
            <th class="px-3 py-2.5 text-center font-bold w-10"></th>
          </tr>
        </thead>

        <!-- Body -->
        <tbody>
          <template v-for="(doc, index) in documents" :key="index">
            <!-- Main Row -->
            <tr @click="toggleExpand(index)"
              class="border-b border-border-subtle hover:bg-bg-elevated/50 transition-colors cursor-pointer group">
              <td class="px-3 py-3 text-text-muted font-semibold">{{ index + 1 }}</td>
              <td class="px-3 py-3 text-primary font-semibold line-clamp-2">
                {{ doc.title }}
              </td>
              <td class="px-3 py-3 text-text-subdued text-xs line-clamp-1">
                {{ doc.source }}
              </td>
              <td class="px-3 py-3 text-text-subdued line-clamp-2">
                {{ doc.content && doc.content.substring(0, 100) + '...' || 'N/A' }}
              </td>
              <td class="px-3 py-3 text-center">
                <span class="material-symbols-outlined text-primary transition-transform duration-300"
                  :class="{ 'rotate-180': isExpanded(index) }">
                  expand_more
                </span>
              </td>
            </tr>

            <!-- Expanded Content Row -->
            <tr v-if="isExpanded(index)" class="bg-bg-elevated/50 border-b border-border-subtle">
              <td colspan="5" class="px-4 py-4">
                <div class="space-y-3">
                  <!-- Title Section -->
                  <div>
                    <h4 class="text-xs font-bold text-primary uppercase tracking-wider mb-1">
                      Judul Lengkap
                    </h4>
                    <p class="text-sm text-text-base font-medium">{{ doc.title }}</p>
                  </div>

                  <!-- Source Section -->
                  <div>
                    <h4 class="text-xs font-bold text-primary uppercase tracking-wider mb-1">
                      Sumber
                    </h4>
                    <p class="text-sm text-text-subdued">{{ doc.source }}</p>
                  </div>

                  <!-- Full Abstract Section -->
                  <div>
                    <h4 class="text-xs font-bold text-primary uppercase tracking-wider mb-2">
                      Abstrak Lengkap
                    </h4>
                    <div class="bg-bg-surface rounded p-3 border border-border-subtle">
                      <p class="text-sm text-text-subdued leading-relaxed whitespace-pre-wrap">
                        {{ doc.full_content || doc.content }}
                      </p>
                    </div>
                  </div>

                  <!-- Action Buttons -->
                  <div class="flex gap-2 pt-2">
                    <button @click.stop="() => {
                      navigator.clipboard.writeText(doc.full_content || doc.content)
                    }"
                      class="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 hover:bg-primary/20 text-primary rounded text-xs font-medium transition-colors">
                      <span class="material-symbols-outlined text-sm">content_copy</span>
                      Salin Abstrak
                    </button>
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
/* Smooth transitions */
tr {
  transition: background-color 0.2s ease;
}

table {
  border-collapse: collapse;
}
</style>
