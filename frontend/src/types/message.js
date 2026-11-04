/**
 * ============================================================
 * 消息类型定义（全项目统一）
 * ------------------------------------------------------------
 * 书单推荐 SSE 事件类型：thinking / tool_call / book_recommend / done / error
 * 页面根据 msg.type 做分支渲染，格式必须严格统一。
 * ============================================================
 */

/**
 * 消息类型枚举
 */
export const MsgType = {
  /** 思考过程（后端检索前的思考文案） */
  THINKING: 'thinking',
  /** 工具调用（后端查询书单库的动作） */
  TOOL_CALL: 'tool_call',
  /** 推荐书籍（携带 data：书籍对象） */
  BOOK_RECOMMEND: 'book_recommend',
  /** 流式结束 */
  DONE: 'done',
  /** 错误（携带 data.msg / content：错误信息） */
  ERROR: 'error',
};

/**
 * @typedef {Object} BookData
 * @description 推荐书籍对象
 * @property {string} id 书籍id
 * @property {string} title 书名
 * @property {string} author 作者
 * @property {string} cover 封面（可空）
 * @property {string} desc 简介
 * @property {string[]} tags 标签
 */

/**
 * @typedef {Object} Message
 * @description 统一标准消息对象（SSE 解析后的结果，页面直接渲染）
 * @property {string} id 唯一标识
 * @property {MsgType} type 消息类型
 * @property {string} content 内容文本
 * @property {BookData|null} data 附加数据（book_recommend 携带书籍对象）
 * @property {boolean} isEnd 是否流式结束
 */

/**
 * 判断是否为合法消息类型
 * @param {*} type 要判断的值
 * @returns {boolean} true=合法类型
 */
export function isValidMsgType(type) {
  return Object.values(MsgType).includes(type);
}

/**
 * 生成简易唯一 id（时间戳 + 随机数）
 * @returns {string} 唯一标识
 */
export function generateId() {
  return 'msg_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
}

/**
 * 创建统一标准消息对象（工厂函数）
 * 所有消息都必须通过这个函数生成，保证结构统一
 *
 * @param {Partial<Message>} options 消息配置
 * @param {string} [options.id]      唯一标识，不传自动生成
 * @param {MsgType} [options.type]   消息类型，默认 thinking
 * @param {string} [options.content] 内容文本，默认空串
 * @param {Object} [options.data]    附加数据，默认 null
 * @param {boolean} [options.isEnd]  是否流式结束，默认 false
 * @returns {Message} 标准消息对象
 */
export function createMessage({ id, type, content, data, isEnd } = {}) {
  return {
    id: id || generateId(),
    type: type || MsgType.THINKING,
    content: content || '',
    data: data || null,
    isEnd: isEnd === undefined ? false : Boolean(isEnd),
  };
}