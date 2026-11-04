/**
 * ============================================================
 * 基础 fetch 封装
 * ------------------------------------------------------------
 * 职责：
 *   1. 统一后端地址
 *   2. JSON 请求（request）
 *   3. SSE 流式请求（requestStream），配合 AbortController 取消
 * ============================================================
 */

/** 后端地址（默认 8000，被占用时可改为 8001） */
export const BASE_URL = 'http://127.0.0.1:8000';

/**
 * 创建 AbortController（用于取消请求 / 终止流式生成）
 * @returns {AbortController}
 */
export function createAbortController() {
  return new AbortController();
}

/**
 * 普通 JSON 请求（如健康检查、非流式接口）
 *
 * @param {Object}    options
 * @param {string}    options.url        接口路径，如 '/health'
 * @param {string}    [options.method]   请求方法，默认 POST
 * @param {Object}    [options.data]     请求体（自动转 JSON）
 * @param {Object}    [options.headers]  额外请求头
 * @param {AbortSignal} [options.signal] 外部取消信号
 * @returns {Promise<Object>} 后端返回的 JSON
 */
export async function request({ url, method = 'POST', data = null, headers = {}, signal = null }) {
  const resp = await fetch(BASE_URL + url, {
    method,
    headers: { 'Content-Type': 'application/json', ...headers },
    body: data ? JSON.stringify(data) : undefined,
    signal,
  });
  if (!resp.ok) {
    throw new Error('HTTP ' + resp.status);
  }
  return resp.json();
}

/**
 * SSE 流式请求：发起请求并返回可读流
 *
 * @param {Object}    options
 * @param {string}    options.url        接口路径，如 '/chat'
 * @param {Object}    [options.data]     请求体（自动转 JSON）
 * @param {AbortSignal} [options.signal] 取消信号（终止生成时 abort）
 * @returns {Promise<ReadableStream>} 响应流（response.body）
 */
export async function requestStream({ url, data = null, signal = null }) {
  const resp = await fetch(BASE_URL + url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
    signal,
  });
  if (!resp.ok) {
    throw new Error('HTTP ' + resp.status);
  }
  if (!resp.body) {
    throw new Error('当前环境不支持流式响应');
  }
  return resp.body;
}