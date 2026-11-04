/**
 * ============================================================
 * 书单推荐接口封装（底层通信，唯一入口）
 * ------------------------------------------------------------
 * 职责：
 *   1. sendQuery：发起 SSE 流式推荐（mock / 真实后端一键切换）
 *   2. fetchBookList / fetchBookDetail / fetchBookNotes / fetchBookStats：书单查询
 *   3. stopGenerate：终止当前流式生成（mock 与真实后端都支持）
 *   4. setMock / isMock：mock 模式开关
 *
 * 推荐逻辑全部在后端，前端只做接口封装、SSE 解析、状态托管。
 * ============================================================
 */

import { mockStream, mockEnabled, setMockEnabled } from '../utils/mockStream.js';
import { MsgType } from '../types/message.js';
import { parseSSEChunk } from '../utils/msgParser.js';
import { BASE_URL, request, requestStream, createAbortController } from '../utils/request.js';

/** SSE 流式推荐接口路径 */
const RECOMMEND_URL = '/recommend/stream';

/** 当前正在进行的真实后端请求控制器（用于终止生成） */
let currentController = null;

/** 当前正在进行的 mock 推送取消函数（用于终止 mock 生成） */
let currentMockCancel = null;

/**
 * 设置 mock 模式开关
 * @param {boolean} v true=mock，false=真实后端
 */
export function setMock(v) {
  setMockEnabled(v);
}

/**
 * 当前是否为 mock 模式
 * @returns {boolean}
 */
export function isMock() {
  return mockEnabled;
}

/**
 * 按消息类型分发到对应回调
 * @param {Message} msg 标准消息对象
 * @param {Object}  handlers 回调集合
 */
function dispatchByType(msg, handlers) {
  const { onThinking, onToolCall, onMessage, onDone, onError } = handlers;
  switch (msg.type) {
    case MsgType.THINKING:
      onThinking && onThinking(msg);
      break;
    case MsgType.TOOL_CALL:
      onToolCall && onToolCall(msg);
      break;
    case MsgType.BOOK_RECOMMEND:
      onMessage && onMessage(msg);
      break;
    case MsgType.DONE:
      onDone && onDone();
      break;
    case MsgType.ERROR: {
      const err = new Error((msg.data && msg.data.msg) || msg.content || '未知错误');
      if (onError) onError(err);
      else console.error('[agent] 推荐出错：', err);
      break;
    }
    default:
      break;
  }
}

/**
 * 发起 SSE 流式书单推荐
 *
 * @param {Object}   params            参数
 * @param {string[]} [params.tags]     标签数组
 * @param {string}   [params.preference] 偏好文本
 * @param {number}   [params.count]    返回数量，默认 5
 * @param {Object}   [handlers]        回调集合
 * @param {Function} [handlers.onThinking]  收到 thinking 事件 (Message) => void
 * @param {Function} [handlers.onToolCall]  收到 tool_call 事件 (Message) => void
 * @param {Function} [handlers.onMessage]   收到 book_recommend 事件 (Message) => void
 * @param {Function} [handlers.onDone]      收到 done / 流结束 () => void
 * @param {Function} [handlers.onError]     出错 (Error) => void
 * @returns {Function} 取消函数（页面可在卸载时调用）
 */
export function sendQuery({ tags = [], preference = '', count = 5 } = {}, handlers = {}) {
  const { onThinking, onToolCall, onMessage, onDone, onError } = handlers;

  // 先终止上一次未完成的推荐，避免新旧结果混在一起
  if (currentController) {
    currentController.abort();
    currentController = null;
  }
  if (currentMockCancel) {
    currentMockCancel();
    currentMockCancel = null;
  }

  // onDone 只触发一次（后端 done 事件 + 流关闭都会走到这里）
  let finished = false;
  const finish = () => {
    if (!finished) {
      finished = true;
      onDone && onDone();
    }
  };

  // —— mock 模式：不请求后端，模拟推送静态书单 ——
  if (mockEnabled) {
    currentMockCancel = mockStream(
      (msg) => dispatchByType(msg, { onThinking, onToolCall, onMessage, onDone: finish, onError }),
      finish,
      { tags, preference, count }, // 传给 mock：换关键词换一批书
    );
    return function cancel() {
      if (currentMockCancel) currentMockCancel();
      currentMockCancel = null;
    };
  }

  // —— 真实后端：SSE 流式请求（可被 AbortController 终止）——
  const controller = createAbortController();
  currentController = controller;

  (async () => {
    try {
      // 1. 发起流式请求，拿到可读流
      const body = await requestStream({
        url: RECOMMEND_URL,
        data: { tags, preference, count },
        signal: controller.signal,
      });

      // 2. 循环读取流，逐行解析成标准消息并分发
      const reader = body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = ''; // 缓存半截行

      while (true) {
        const result = await reader.read();
        if (result.done) break;

        buffer += decoder.decode(result.value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // 最后一行可能是半截，留到下一次

        const msgs = parseSSEChunk(lines.join('\n'));
        msgs.forEach((m) => dispatchByType(m, { onThinking, onToolCall, onMessage, onDone: finish, onError }));
      }

      // 3. 流结束
      finish();
    } catch (err) {
      // 手动终止（AbortError）不算错误，按正常结束处理
      if (err && err.name === 'AbortError') {
        finish();
        return;
      }
      if (onError) onError(err);
      else console.error('[agent] sendQuery 出错：', err);
      finish();
    } finally {
      currentController = null;
    }
  })();

  // 返回取消函数
  return function cancel() {
    controller.abort();
    currentController = null;
  };
}

/**
 * 获取全部书单列表
 * @returns {Promise<BookData[]>} 书籍数组
 */
export async function fetchBookList() {
  const json = await request({ url: '/books/list', method: 'POST', data: {} });
  if (!json || json.success !== true) {
    throw new Error((json && (json.message || json.detail)) || '请求失败');
  }
  return (json.data && json.data.books) || [];
}

/**
 * 获取单本书详情
 * @param {string} bookId 书籍 id
 * @returns {Promise<BookData|null>} 书籍详情
 */
export async function fetchBookDetail(bookId) {
  const json = await request({ url: '/books/detail', method: 'POST', data: { bookId } });
  if (!json || json.success !== true) {
    throw new Error((json && (json.message || json.detail)) || '请求失败');
  }
  return (json.data && json.data.book) || null;
}

/**
 * 获取书籍笔记
 * @param {string} bookId 书籍 id
 * @returns {Promise<Object[]>} 笔记数组
 */
export async function fetchBookNotes(bookId) {
  const json = await request({ url: '/books/notes', method: 'POST', data: { bookId } });
  if (!json || json.success !== true) {
    throw new Error((json && (json.message || json.detail)) || '请求失败');
  }
  return (json.data && json.data.notes) || [];
}

/**
 * 获取书单统计信息
 * @returns {Promise<Object|null>} 统计对象
 */
export async function fetchBookStats() {
  const json = await request({ url: '/books/statistics', method: 'POST', data: {} });
  if (!json || json.success !== true) {
    throw new Error((json && (json.message || json.detail)) || '请求失败');
  }
  return (json.data && json.data.stats) || null;
}

/**
 * 终止当前流式生成（供 store.stopGenerate 调用）
 * mock 与真实后端模式均生效
 */
export function stopGenerate() {
  // 停止真实后端请求
  if (currentController) {
    currentController.abort();
    currentController = null;
  }
  // 停止 mock 推送
  if (currentMockCancel) {
    currentMockCancel();
    currentMockCancel = null;
  }
}