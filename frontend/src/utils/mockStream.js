/**
 * ============================================================
 * mock 模拟 SSE 流（联调用）
 * ------------------------------------------------------------
 * 职责：在不启动后端的情况下模拟流式推送书单推荐事件，
 *       方便前端调试页面。
 * 注意：mock 只从内置静态书单样例里按「关键词种子」轮换选取，
 *       不实现推荐算法（换关键词会换一批书，便于调试联调）。
 * 开关：mockEnabled 全局开关，setMockEnabled 动态切换。
 * ============================================================
 */

import { MsgType, createMessage } from '../types/message.js';

/** mock 开关（true=启用 mock） */
export let mockEnabled = true;

/**
 * 设置 mock 开关
 * @param {boolean} v true=启用 mock，false=使用真实后端
 */
export function setMockEnabled(v) {
  mockEnabled = Boolean(v);
}

/** 默认推送间隔（毫秒） */
const DEFAULT_INTERVAL = 600;

/** 内置静态书单样例（与后端书单同款） */
const SAMPLE_BOOKS = [
  { id: 'mock1', title: '活着', author: '余华', cover: '', desc: '在苦难中展现生命的坚韧与活着的意义。', tags: ['小说', '文学', '人生'] },
  { id: 'mock2', title: '三体', author: '刘慈欣', cover: '', desc: '中国科幻巅峰之作，关于宇宙与文明的宏大想象。', tags: ['科幻', '小说', '宇宙'] },
  { id: 'mock3', title: '人类简史', author: '尤瓦尔·赫拉利', cover: '', desc: '重新审视人类从认知革命到科学革命的发展历程。', tags: ['历史', '社科', '思维'] },
  { id: 'mock4', title: '深度工作', author: '卡尔·纽波特', cover: '', desc: '如何在碎片化时代培养深度工作的能力。', tags: ['效率', '成长', '职场'] },
  { id: 'mock5', title: '小王子', author: '圣埃克苏佩里', cover: '', desc: '一部写给大人的童话，关于爱、责任与驯养。', tags: ['童话', '哲学', '治愈'] },
  { id: 'mock6', title: '算法图解', author: '巴尔加瓦', cover: '', desc: '像小说一样有趣的算法入门书，零基础友好。', tags: ['编程', '计算机', '入门'] },
  { id: 'mock7', title: '被讨厌的勇气', author: '岸见一郎', cover: '', desc: '用对话体讲阿德勒心理学与课题分离。', tags: ['心理', '成长', '哲学'] },
  { id: 'mock8', title: '平凡的世界', author: '路遥', cover: '', desc: '普通人在大时代中的奋斗史诗。', tags: ['小说', '文学', '人生'] },
  { id: 'mock9', title: '思考，快与慢', author: '丹尼尔·卡尼曼', cover: '', desc: '揭示大脑两套思维系统如何影响决策。', tags: ['心理', '思维', '社科'] },
  { id: 'mock10', title: '代码整洁之道', author: '罗伯特·马丁', cover: '', desc: '写出整洁、可维护、可读的代码。', tags: ['编程', '工程', '成长'] },
  { id: 'mock11', title: '百年孤独', author: '加西亚·马尔克斯', cover: '', desc: '魔幻现实主义的巅峰之作。', tags: ['小说', '文学', '人生'] },
  { id: 'mock12', title: '明朝那些事儿', author: '当年明月', cover: '', desc: '轻松幽默地讲明朝三百年历史。', tags: ['历史', '中国', '趣味'] },
  { id: 'mock13', title: '非暴力沟通', author: '马歇尔·卢森堡', cover: '', desc: '基于同理心的沟通方式。', tags: ['心理', '沟通', '成长'] },
  { id: 'mock14', title: '时间简史', author: '史蒂芬·霍金', cover: '', desc: '用通俗语言讲透宇宙的起源与命运。', tags: ['科学', '宇宙', '科普'] },
  { id: 'mock15', title: '认知觉醒', author: '周岭', cover: '', desc: '用认知驱动行动与成长。', tags: ['成长', '心理', '思维'] },
  { id: 'mock16', title: '解忧杂货店', author: '东野圭吾', cover: '', desc: '温暖治愈的时空联结。', tags: ['小说', '治愈', '推理'] },
  { id: 'mock17', title: '掌控习惯', author: '詹姆斯·克利尔', cover: '', desc: '让好习惯显而易见、简单易行。', tags: ['成长', '习惯', '效率'] },
  { id: 'mock18', title: '小狗钱钱', author: '博多·舍费尔', cover: '', desc: '用童话讲理财。', tags: ['理财', '入门', '成长'] },
  { id: 'mock19', title: '银河帝国', author: '艾萨克·阿西莫夫', cover: '', desc: '心理史学与银河帝国的宏大叙事。', tags: ['科幻', '小说', '宇宙'] },
  { id: 'mock20', title: '富爸爸穷爸爸', author: '罗伯特·清崎', cover: '', desc: '让钱为你工作。', tags: ['理财', '成长', '入门'] },
];

/**
 * 用关键词生成确定性种子（让换关键词能换一批书）
 * @param {string[]} tags 标签
 * @param {string}   preference 偏好文本
 * @returns {number} 种子
 */
function seedFrom(tags = [], preference = '') {
  let seed = 0;
  [...tags, preference || ''].forEach((s) => {
    for (const ch of String(s)) {
      seed = (seed * 31 + ch.codePointAt(0)) >>> 0;
    }
  });
  return seed || 1;
}

/**
 * 按种子从静态样例里轮换选取 count 本（确定性，不写推荐算法）
 * @param {string[]} tags
 * @param {string}   preference
 * @param {number}   count
 * @returns {Object[]} 选中的书籍
 */
function hashOrder(id, seed) {
  let h = seed;
  for (const ch of String(id)) h = (h * 33 + ch.codePointAt(0)) >>> 0;
  return h;
}

function pickSampleBooks(tags = [], preference = '', count = 5) {
  const pool = SAMPLE_BOOKS;
  const n = Math.max(1, Math.min(pool.length, count || 5));
  // 1) 优先取与选中标签有交集的书（确定性排序，同查询结果稳定）
  const matched = pool.filter((b) => (b.tags || []).some((t) => tags.includes(t)));
  const seed = seedFrom(tags, preference);
  const picked = [...matched].sort((a, b) => hashOrder(a.id, seed) - hashOrder(b.id, seed));
  if (picked.length > n) picked.length = n;
  // 2) 数量不足时，从其他书里按种子轮换补足（用固定数量，避免动态长度少推）
  const fillCount = n - picked.length;
  if (fillCount > 0) {
    const others = pool.filter((b) => !matched.includes(b));
    if (others.length) {
      const start = seed % others.length;
      const step = (seed % (others.length - 1)) + 1;
      for (let i = 0; i < fillCount; i += 1) {
        picked.push(others[(start + i * step) % others.length]);
      }
    }
  }
  return picked;
}

/**
 * 生成 mock 事件序列（静态样例，无推荐算法）
 * thinking -> tool_call -> book_recommend xN -> done
 * @param {Object} [options] { tags, preference, count }
 * @returns {Message[]} 标准消息对象数组
 */
function buildMockEvents(options = {}) {
  const events = [];
  events.push(createMessage({ type: MsgType.THINKING, content: '正在检索书单库' }));
  events.push(createMessage({ type: MsgType.TOOL_CALL, content: '查询书籍数据库' }));
  pickSampleBooks(options.tags, options.preference, options.count).forEach((book) => {
    events.push(createMessage({ type: MsgType.BOOK_RECOMMEND, data: book }));
  });
  events.push(createMessage({ type: MsgType.DONE })); // 最后一条标记流结束
  return events;
}

/**
 * 启动 mock 流式推送（逐条间隔推送，最后回调 onFinish）
 *
 * @param {Function} onEvent        每推送一条事件回调 (Message) => void
 * @param {Function} onFinish       全部推送完成回调 () => void
 * @param {Object}   [options]      可选配置
 * @param {string[]} [options.tags]       标签（影响轮换选择）
 * @param {string}   [options.preference] 偏好（影响轮换选择）
 * @param {number}   [options.count]      数量
 * @param {number}   [options.interval]   推送间隔毫秒，默认 600
 * @returns {Function} cancel 取消函数（中途调用可立即停止）
 */
export function mockStream(onEvent, onFinish, options = {}) {
  const interval = options.interval || DEFAULT_INTERVAL;
  const events = buildMockEvents(options);
  let index = 0;
  let stopped = false;

  const timer = setInterval(() => {
    if (stopped) return;
    if (index < events.length) {
      const msg = events[index];
      index += 1;
      if (onEvent) onEvent(msg);
    } else {
      clearInterval(timer);
      if (onFinish) onFinish();
    }
  }, interval);

  return function cancel() {
    stopped = true;
    clearInterval(timer);
  };
}