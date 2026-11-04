<template>
  <div class="app">
    <!-- 顶部栏 -->
    <header class="top-bar">
      <h1 class="logo">📚 书单推荐</h1>
      <div class="top-actions">
        <button class="chip-btn" @click="store.setMock(!isMock)">{{ isMock ? 'Mock 模式' : '真实后端' }}</button>
        <button class="chip-btn" @click="toggleStats">书单统计</button>
      </div>
    </header>

    <!-- 筛选面板 -->
    <section class="filter-panel">
      <div class="filter-row">
        <span class="filter-label">标签</span>
        <button
          v-for="tag in allTags"
          :key="tag"
          class="tag-chip"
          :class="{ active: selectedTags.includes(tag) }"
          @click="toggleTag(tag)"
        >{{ tag }}</button>
        <span v-if="allTags.length === 0" class="filter-hint">加载中…</span>
      </div>
      <div class="filter-row">
        <span class="filter-label">偏好</span>
        <input v-model="preference" class="text-input" placeholder="如：喜欢心理学 / 科幻" />
        <span class="filter-label count-label">数量</span>
        <select v-model.number="count" class="select-input">
          <option :value="3">3 本</option>
          <option :value="5">5 本</option>
          <option :value="8">8 本</option>
        </select>
        <button class="btn-primary" @click="startRecommend" :disabled="store.loading">开始推荐</button>
        <button v-if="store.loading" class="btn-stop" @click="store.stopGenerate()">停止</button>
      </div>
    </section>

    <!-- 流式提示（匹配 SSE thinking / tool_call） -->
    <div v-if="store.loading" class="stream-tip">
      <span class="dot"></span><span class="dot"></span><span class="dot"></span>
      <span class="tip-text">{{ store.toolCall || store.thinking || '正在检索书单库…' }}</span>
    </div>
    <div v-if="store.error" class="error-tip">⚠ {{ store.error }}</div>

    <!-- 流式推荐结果卡片 -->
    <main class="cards-area" ref="cardsRef">
      <div v-if="!store.loading && store.recommended.length === 0" class="empty-tip">
        选择标签和偏好，点击「开始推荐」试试吧～
      </div>
      <article
        v-for="book in store.recommended"
        :key="book.id"
        class="book-card"
        @click="openDetail(book)"
      >
        <div class="book-cover" :style="{ background: coverColor(book.id) }">
          <span v-if="!book.cover" class="cover-fallback">📖</span>
          <img v-else :src="book.cover" :alt="book.title" />
        </div>
        <div class="book-info">
          <h3 class="book-title">{{ book.title }}</h3>
          <p class="book-author">{{ book.author }}</p>
          <p class="book-desc">{{ book.desc }}</p>
          <div class="book-tags">
            <span v-for="tag in book.tags" :key="tag" class="tag-chip mini">{{ tag }}</span>
          </div>
        </div>
      </article>
    </main>

    <!-- 全部书单 -->
    <section class="all-books">
      <h2 class="section-title">全部书单（{{ store.books.length }} 本）</h2>
      <div class="book-list">
        <button
          v-for="book in store.books"
          :key="book.id"
          class="book-list-item"
          @click="openDetail(book)"
        >
          <span class="list-title">{{ book.title }}</span>
          <span class="list-author">{{ book.author }}</span>
        </button>
      </div>
    </section>

    <!-- 书籍详情弹窗 -->
    <div v-if="showDetail" class="modal-mask" @click.self="closeDetail">
      <div class="modal">
        <button class="modal-close" @click="closeDetail">×</button>
        <template v-if="store.selectedBook">
          <h2 class="modal-title">{{ store.selectedBook.title }}</h2>
          <p class="modal-author">{{ store.selectedBook.author }} · {{ (store.selectedBook.rating || '-') + ' 分' }}</p>
          <p class="modal-desc">{{ store.selectedBook.desc }}</p>
          <div class="modal-tags">
            <span v-for="tag in store.selectedBook.tags" :key="tag" class="tag-chip">{{ tag }}</span>
          </div>
          <h3 class="modal-sub">📝 读书笔记</h3>
          <ul class="notes-list">
            <li v-for="note in store.notes" :key="note.id" class="note-item">{{ note.content }}</li>
            <li v-if="store.notes.length === 0" class="note-empty">暂无笔记</li>
          </ul>
        </template>
        <p v-else class="modal-empty">加载中…</p>
      </div>
    </div>

    <!-- 统计弹窗 -->
    <div v-if="showStats" class="modal-mask" @click.self="toggleStats">
      <div class="modal stats-modal">
        <button class="modal-close" @click="toggleStats">×</button>
        <h2 class="modal-title">书单统计</h2>
        <template v-if="store.stats">
          <div class="stat-grid">
            <div class="stat-item"><strong>{{ store.stats.totalBooks }}</strong><span>书籍总数</span></div>
            <div class="stat-item"><strong>{{ store.stats.totalTags }}</strong><span>标签种类</span></div>
            <div class="stat-item"><strong>{{ store.stats.totalNotes }}</strong><span>笔记总数</span></div>
            <div class="stat-item"><strong>{{ store.stats.avgRating }}</strong><span>平均评分</span></div>
          </div>
        </template>
        <p v-else class="modal-empty">加载中…</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useChatStore } from '../store/chat.js'

const store = useChatStore()
store.setMock(true) // 默认 mock 模式，方便不开后端调试

const selectedTags = ref([])
const preference = ref('')
const count = ref(5)
const showDetail = ref(false)
const showStats = ref(false)
const cardsRef = ref(null)

// 从全部书单里提取所有标签（去重）
const allTags = computed(() => {
  const set = new Set()
  store.books.forEach((b) => (b.tags || []).forEach((t) => set.add(t)))
  return [...set]
})

// 标签多选
const toggleTag = (tag) => {
  if (selectedTags.value.includes(tag)) {
    selectedTags.value = selectedTags.value.filter((t) => t !== tag)
  } else {
    selectedTags.value = [...selectedTags.value, tag]
  }
}

// 发起流式推荐（推荐逻辑在后端，这里只调用 store）
const startRecommend = () => {
  store.sendQuery({ tags: selectedTags.value, preference: preference.value, count: count.value })
}

// 打开详情：拉取详情 + 笔记
const openDetail = (book) => {
  store.fetchBookDetail(book.id)
  store.fetchBookNotes(book.id)
  showDetail.value = true
}

const closeDetail = () => {
  showDetail.value = false
}

const toggleStats = () => {
  if (!store.stats) store.fetchBookStats()
  showStats.value = !showStats.value
}

// 封面占位配色（无封面图时按 id 取柔和绿色系）
const coverColors = ['#dceee3', '#e3f1e8', '#f0f4dc', '#d7e9df', '#cfe6d8']
const coverColor = (id) => {
  let sum = 0
  String(id).split('').forEach((c) => { sum += c.charCodeAt(0) })
  return coverColors[sum % coverColors.length]
}

// 流式卡片自动滚动到底部（纯 UI 辅助）
watch(() => store.recommended.length, () => {
  setTimeout(() => {
    if (cardsRef.value) cardsRef.value.scrollTop = cardsRef.value.scrollHeight
  }, 50)
})

onMounted(() => {
  store.fetchBookList()
  store.fetchBookStats()
})
</script>

<style scoped>
/* ============ 地球绿色自然主题 ============ */
.app {
  min-height: 100vh;
  max-width: 900px;
  margin: 0 auto;
  padding: 20px 16px;
  box-sizing: border-box;
  background: #f4faf7;
  color: #2c3330;
  font-family: system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}

/* ============ 顶部栏 ============ */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}
.logo {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #2b6b48;
}
.top-actions {
  display: flex;
  gap: 8px;
}
.chip-btn {
  padding: 6px 14px;
  border: 1px solid #d7e9df;
  border-radius: 999px;
  background: #ffffff;
  color: #556660;
  font-family: inherit;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.chip-btn:hover {
  border-color: #73a88c;
  color: #2b6b48;
}

/* ============ 筛选面板 ============ */
.filter-panel {
  padding: 14px 16px;
  border: 1px solid #d7e9df;
  border-radius: 14px;
  background: #ffffff;
  box-shadow: 0 1px 4px rgba(43, 107, 72, 0.06);
  margin-bottom: 14px;
}
.filter-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
.filter-row + .filter-row {
  margin-top: 12px;
}
.filter-label {
  font-size: 13px;
  color: #556660;
  white-space: nowrap;
}
.count-label {
  margin-left: 8px;
}
.filter-hint {
  font-size: 13px;
  color: #9db8aa;
}
.tag-chip {
  padding: 4px 12px;
  border: 1px solid #d7e9df;
  border-radius: 999px;
  background: #f8fbf9;
  color: #556660;
  font-family: inherit;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.tag-chip:hover {
  border-color: #73a88c;
}
.tag-chip.active {
  background: #2b6b48;
  border-color: #2b6b48;
  color: #ffffff;
}
.tag-chip.mini {
  font-size: 12px;
  padding: 2px 8px;
}
.text-input,
.select-input {
  padding: 7px 12px;
  border: 1px solid #d7e9df;
  border-radius: 10px;
  background: #ffffff;
  color: #2c3330;
  font-family: inherit;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.text-input {
  flex: 1;
  min-width: 160px;
}
.text-input:focus,
.select-input:focus {
  border-color: #2b6b48;
  box-shadow: 0 0 0 3px rgba(43, 107, 72, 0.12);
}
.btn-primary {
  padding: 8px 20px;
  border: none;
  border-radius: 10px;
  background: #2b6b48;
  color: #ffffff;
  font-family: inherit;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s ease;
}
.btn-primary:hover:not(:disabled) {
  background: #245a3d;
}
.btn-primary:disabled {
  background: #b9cdc0;
  cursor: not-allowed;
}
.btn-stop {
  padding: 8px 18px;
  border: none;
  border-radius: 10px;
  background: #73a88c;
  color: #ffffff;
  font-family: inherit;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s ease;
}
.btn-stop:hover {
  background: #5f9277;
}

/* ============ 流式提示（thinking / tool_call） ============ */
.stream-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  margin-bottom: 12px;
  border-radius: 12px;
  background: #eef7f0;
  color: #2b6b48;
  font-size: 14px;
}
.stream-tip .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #73a88c;
  animation: dotBounce 1.2s ease-in-out infinite;
}
.stream-tip .dot:nth-child(2) {
  animation-delay: 0.15s;
}
.stream-tip .dot:nth-child(3) {
  animation-delay: 0.3s;
}
@keyframes dotBounce {
  0%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  50% {
    transform: translateY(-3px);
    opacity: 1;
  }
}
.error-tip {
  padding: 10px 14px;
  margin-bottom: 12px;
  border-radius: 12px;
  background: #fbeae7;
  color: #b3554a;
  border: 1px solid #f0d3ce;
  font-size: 14px;
}

/* ============ 流式推荐卡片区 ============ */
.cards-area {
  max-height: 420px;
  overflow-y: auto;
  padding: 4px 6px 10px;
}
.cards-area::-webkit-scrollbar {
  width: 8px;
}
.cards-area::-webkit-scrollbar-thumb {
  background: #c5ddd2;
  border-radius: 8px;
}
.cards-area::-webkit-scrollbar-thumb:hover {
  background: #a9cbb8;
}
.empty-tip {
  padding: 40px 0;
  text-align: center;
  color: #9db8aa;
  font-size: 15px;
}
.book-card {
  display: flex;
  gap: 14px;
  padding: 14px;
  margin: 10px 0;
  border: 1px solid #d7e9df;
  border-radius: 14px;
  background: #ffffff;
  box-shadow: 0 1px 4px rgba(43, 107, 72, 0.06);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.2s ease;
}
.book-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(43, 107, 72, 0.12);
}
.book-cover {
  flex-shrink: 0;
  width: 86px;
  height: 120px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
}
.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}
.book-info {
  flex: 1;
  min-width: 0;
}
.book-title {
  margin: 0 0 2px;
  font-size: 17px;
  font-weight: 600;
  color: #2b6b48;
}
.book-author {
  margin: 0 0 6px;
  font-size: 13px;
  color: #556660;
}
.book-desc {
  margin: 0 0 8px;
  font-size: 14px;
  color: #2c3330;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.book-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* ============ 全部书单 ============ */
.all-books {
  margin-top: 18px;
}
.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #2b6b48;
  margin-bottom: 10px;
}
.book-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.book-list-item {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 6px 14px;
  border: 1px solid #d7e9df;
  border-radius: 999px;
  background: #ffffff;
  font-family: inherit;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.book-list-item:hover {
  border-color: #73a88c;
}
.list-title {
  color: #2c3330;
}
.list-author {
  color: #9db8aa;
  font-size: 12px;
}

/* ============ 弹窗 ============ */
.modal-mask {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(43, 107, 72, 0.25);
  padding: 20px;
}
.modal {
  position: relative;
  width: 100%;
  max-width: 480px;
  max-height: 82vh;
  overflow-y: auto;
  padding: 24px;
  border-radius: 16px;
  background: #ffffff;
  box-shadow: 0 8px 30px rgba(43, 107, 72, 0.2);
}
.modal-close {
  position: absolute;
  top: 12px;
  right: 14px;
  border: none;
  background: transparent;
  font-size: 22px;
  line-height: 1;
  color: #556660;
  cursor: pointer;
}
.modal-title {
  margin: 0 0 4px;
  font-size: 20px;
  color: #2b6b48;
}
.modal-author {
  margin: 0 0 10px;
  font-size: 13px;
  color: #556660;
}
.modal-desc {
  margin: 0 0 12px;
  font-size: 15px;
  color: #2c3330;
}
.modal-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 14px;
}
.modal-sub {
  margin: 0 0 8px;
  font-size: 15px;
  color: #2b6b48;
}
.notes-list {
  margin: 0;
  padding: 0;
  list-style: none;
}
.note-item {
  padding: 10px 12px;
  margin-bottom: 8px;
  border-radius: 10px;
  background: #f0f4dc;
  color: #2c3330;
  font-size: 14px;
}
.note-empty,
.modal-empty {
  color: #9db8aa;
  font-size: 14px;
}
.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 12px;
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 10px;
  border-radius: 12px;
  background: #eef7f0;
}
.stat-item strong {
  font-size: 26px;
  color: #2b6b48;
}
.stat-item span {
  font-size: 13px;
  color: #556660;
}
</style>