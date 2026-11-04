/**
 * ============================================================
 * 书单推荐全局状态（Pinia）
 * ------------------------------------------------------------
 * state：  books / recommended / selectedBook / notes / stats / thinking / toolCall / loading / error
 * actions：sendQuery / fetchBookList / fetchBookDetail / fetchBookNotes / fetchBookStats / stopGenerate / setMock
 *
 * 约定：books / recommended 里的书籍都是后端返回的标准数据结构，
 *       页面直接渲染即可；推荐逻辑全部在后端，前端只做状态托管。
 * 持久化：全部书单保存到 localStorage，刷新页面不丢失。
 * ============================================================
 */

import { defineStore } from 'pinia';
import {
  sendQuery as agentSendQuery,
  fetchBookList as agentFetchBookList,
  fetchBookDetail as agentFetchBookDetail,
  fetchBookNotes as agentFetchBookNotes,
  fetchBookStats as agentFetchBookStats,
  stopGenerate as agentStopGenerate,
  setMock as agentSetMock,
} from '../api/agent.js';

/** localStorage 的 key */
const STORAGE_KEY = 'book_recommend_store_v1';

/** 推荐序号：用于丢弃上一次未完成流的结果，避免新旧结果串流 */
let querySeq = 0;

/**
 * 安全读取 localStorage（防止被禁用时报错）
 * @returns {Object} 保存过的数据
 */
function loadFromStorage() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : {};
  } catch (err) {
    console.warn('[chat] 读取本地缓存失败：', err);
    return {};
  }
}

/**
 * 安全写入 localStorage
 * @param {Object} data 要保存的数据
 */
function saveToStorage(data) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (err) {
    console.warn('[chat] 保存本地缓存失败：', err);
  }
}

export const useChatStore = defineStore('chat', {
  // ==================== 状态 ====================
  state: () => {
    const saved = loadFromStorage();
    return {
      /** 全部书单列表 */
      books: saved.books || [],
      /** 流式推荐结果（sendQuery 累积） */
      recommended: [],
      /** 当前选中书籍 */
      selectedBook: null,
      /** 当前选中书籍的笔记 */
      notes: [],
      /** 书单统计信息 */
      stats: null,
      /** 思考提示（SSE thinking 事件文案） */
      thinking: '',
      /** 工具调用提示（SSE tool_call 事件文案） */
      toolCall: '',
      /** 是否正在推荐中 */
      loading: false,
      /** 最近一次错误信息（null=无错误） */
      error: null,
    };
  },

  // ==================== 计算属性 ====================
  getters: {
    /** 是否已有书单 */
    hasBooks: (state) => state.books.length > 0,
    /** 是否已有推荐结果 */
    hasRecommended: (state) => state.recommended.length > 0,
  },

  // ==================== 动作 ====================
  actions: {
    /**
     * 发起 SSE 流式书单推荐
     * @param {Object}   params
     * @param {string[]} [params.tags]      标签数组
     * @param {string}   [params.preference] 偏好文本
     * @param {number}   [params.count]     返回数量，默认 5
     */
    async sendQuery({ tags = [], preference = '', count = 5 } = {}) {
      if (this.loading) return;
      const seq = ++querySeq; // 本次推荐序号
      // 重置流式相关状态
      this.recommended = [];
      this.thinking = '';
      this.toolCall = '';
      this.error = null;
      this.loading = true;

      await agentSendQuery(
        { tags, preference, count },
        {
          onThinking: (msg) => {
            if (seq !== querySeq) return; // 旧流丢弃
            this.thinking = msg.content;
          },
          onToolCall: (msg) => {
            if (seq !== querySeq) return; // 旧流丢弃
            this.toolCall = msg.content;
          },
          onMessage: (msg) => {
            if (seq !== querySeq) return; // 旧流的结果丢弃
            // book_recommend：把书籍对象累积进推荐结果
            if (msg.data) this.recommended.push(msg.data);
          },
          onDone: () => {
            if (seq !== querySeq) return; // 旧流丢弃
            this.loading = false;
          },
          onError: (err) => {
            if (seq !== querySeq) return; // 旧流丢弃
            this.error = err && err.message ? err.message : String(err);
            this.loading = false;
          },
        },
      );
    },

    /**
     * 获取全部书单列表
     */
    async fetchBookList() {
      try {
        this.books = await agentFetchBookList();
        this.persist();
      } catch (err) {
        this.error = err && err.message ? err.message : String(err);
      }
    },

    /**
     * 获取单本书详情
     * @param {string} bookId 书籍 id
     */
    async fetchBookDetail(bookId) {
      try {
        this.selectedBook = await agentFetchBookDetail(bookId);
      } catch (err) {
        this.error = err && err.message ? err.message : String(err);
      }
    },

    /**
     * 获取书籍笔记
     * @param {string} bookId 书籍 id
     */
    async fetchBookNotes(bookId) {
      try {
        this.notes = await agentFetchBookNotes(bookId);
      } catch (err) {
        this.error = err && err.message ? err.message : String(err);
      }
    },

    /**
     * 获取书单统计信息
     */
    async fetchBookStats() {
      try {
        this.stats = await agentFetchBookStats();
      } catch (err) {
        this.error = err && err.message ? err.message : String(err);
      }
    },

    /**
     * 终止当前推荐生成
     */
    stopGenerate() {
      agentStopGenerate();
      this.loading = false;
    },

    /**
     * 切换 mock / 真实后端模式
     * @param {boolean} v true=mock，false=真实后端
     */
    setMock(v) {
      agentSetMock(v);
    },

    /**
     * 清空推荐结果
     */
    clearRecommended() {
      this.recommended = [];
    },

    /**
     * 持久化书单到 localStorage
     */
    persist() {
      saveToStorage({ books: this.books });
    },
  },
});