/**
 * ============================================================
 * 消息解析器（SSE → 标准消息）
 * ------------------------------------------------------------
 * 职责：接收后端原始 SSE 分片（或 JSON 对象），
 *       只解析 thinking / tool_call / book_recommend / done / error 五种类型，
 *       输出统一标准消息对象（见 types/message.js）。
 *
 * 页面只消费标准消息，不接触后端原始格式。
 * ============================================================
 */

import { MsgType, createMessage, isValidMsgType } from '../types/message.js';

/**
 * 将后端原始 JSON 对象转换为统一标准消息对象（核心函数）
 * 只处理约定的 5 种类型；其他类型返回 null（跳过）。
 *
 * @param {Object} raw 后端原始对象
 * @returns {Message|null} 标准消息对象；非法类型返回 null
 */
export function normalizeMessage(raw) {
  // 空数据保护
  if (!raw || typeof raw !== 'object') return null;

  const type = raw.type;
  // 只处理这 5 种类型
  if (!isValidMsgType(type)) return null;

  let content = '';
  let data = null;

  if (type === MsgType.THINKING || type === MsgType.TOOL_CALL) {
    // 思考 / 工具调用：取 content 文案
    content = raw.content || '';
  } else if (type === MsgType.BOOK_RECOMMEND) {
    // 推荐书籍：data 携带完整书籍对象
    data = raw.data || null;
    content = (data && data.title) || '';
  } else if (type === MsgType.ERROR) {
    // 错误：msg / content 都是错误信息
    content = raw.msg || raw.content || '未知错误';
    data = { msg: content };
  }
  // DONE：content 为空，isEnd=true

  return createMessage({
    id: raw.id || undefined,
    type: type,
    content: content,
    data: data,
    isEnd: type === MsgType.DONE,
  });
}

/**
 * 解析一行 SSE 文本（形如 "data: {json}"）
 * @param {string} line 一行 SSE 数据
 * @returns {Message|null} 标准消息对象；非数据行或解析失败返回 null
 */
export function parseSSELine(line) {
  const text = String(line || '').trim();
  // 只处理以 data: 开头的行（SSE 标准格式）
  if (text.indexOf('data:') !== 0) return null;

  const jsonStr = text.replace(/^data:/, '').trim();
  // 兼容 SSE 结束标记：data: [DONE]
  if (jsonStr === '[DONE]') return null;

  try {
    return normalizeMessage(JSON.parse(jsonStr));
  } catch (err) {
    console.warn('[msgParser] SSE 数据解析失败，已跳过：', jsonStr, err);
    return null;
  }
}

/**
 * 解析一段 SSE 原始分片（可能包含多行）
 * @param {string} chunk 原始文本
 * @returns {Message[]} 标准消息对象数组（可能为空）
 */
export function parseSSEChunk(chunk) {
  if (!chunk) return [];
  const lines = String(chunk).split('\n');
  const result = [];
  for (let i = 0; i < lines.length; i += 1) {
    const msg = parseSSELine(lines[i]);
    if (msg) result.push(msg);
  }
  return result;
}