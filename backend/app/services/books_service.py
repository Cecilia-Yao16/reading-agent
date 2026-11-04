"""
书单数据与推荐逻辑

说明：
- 内置一份模拟书单数据（100 本），用于本地测试；
- 推荐筛选逻辑（按标签、偏好匹配）全部在这里实现，前端不做推荐计算。
"""
import re
from typing import List, Optional

# ==================== 内置模拟书单（100 本） ====================
BOOKS: List[dict] = [
    {
        "id": "b1", "title": "活着", "author": "余华",
        "cover": "",
        "desc": "讲述一个人一生的悲欢离合，在苦难中展现生命的坚韧与活着的意义。",
        "tags": ["小说", "文学", "人生"], "rating": 9.4,
        "notes": [{"id": "n1", "bookId": "b1", "content": "人是为了活着本身而活着，而不是为了活着之外的任何事物而活着。"}],
    },
    {
        "id": "b2", "title": "三体", "author": "刘慈欣",
        "cover": "",
        "desc": "中国科幻巅峰之作，讲述地球文明与三体文明的信息交流、生死搏杀。",
        "tags": ["科幻", "小说", "宇宙"], "rating": 9.3,
        "notes": [{"id": "n2", "bookId": "b2", "content": "给岁月以文明，而不是给文明以岁月。"}],
    },
    {
        "id": "b3", "title": "人类简史", "author": "尤瓦尔·赫拉利",
        "cover": "",
        "desc": "从认知革命、农业革命到科学革命，重新审视人类的发展历程。",
        "tags": ["历史", "社科", "思维"], "rating": 9.1,
        "notes": [{"id": "n3", "bookId": "b3", "content": "金钱是有史以来最成功的信任故事。"}],
    },
    {
        "id": "b4", "title": "深度工作", "author": "卡尔·纽波特",
        "cover": "",
        "desc": "如何在碎片化的时代培养深度工作的能力，创造真正有价值的结果。",
        "tags": ["效率", "成长", "职场"], "rating": 8.6,
        "notes": [{"id": "n4", "bookId": "b4", "content": "深度工作是少有人掌握的技能，也恰恰是价值所在。"}],
    },
    {
        "id": "b5", "title": "小王子", "author": "圣埃克苏佩里",
        "cover": "",
        "desc": "一部写给大人的童话，关于爱、责任与驯养。",
        "tags": ["童话", "哲学", "治愈"], "rating": 9.0,
        "notes": [{"id": "n5", "bookId": "b5", "content": "真正重要的东西，用眼睛是看不见的。"}],
    },
    {
        "id": "b6", "title": "算法图解", "author": "巴尔加瓦",
        "cover": "",
        "desc": "像小说一样有趣的算法入门书，配大量图示，零基础友好。",
        "tags": ["编程", "计算机", "入门"], "rating": 8.4,
        "notes": [{"id": "n6", "bookId": "b6", "content": "大 O 表示法让你关注算法的增速，而不是具体步数。"}],
    },
    {
        "id": "b7", "title": "被讨厌的勇气", "author": "岸见一郎",
        "cover": "",
        "desc": "用对话体讲阿德勒心理学：课题分离、被讨厌的勇气与自由。",
        "tags": ["心理", "成长", "哲学"], "rating": 8.9,
        "notes": [{"id": "n7", "bookId": "b7", "content": "自由就是不再寻求被认可。"}],
    },
    {
        "id": "b8", "title": "芯片战争", "author": "克里斯·米勒",
        "cover": "",
        "desc": "一部半导体产业史，解释芯片如何塑造现代世界格局。",
        "tags": ["科技", "商业", "历史"], "rating": 8.8,
        "notes": [{"id": "n8", "bookId": "b8", "content": "芯片是现代世界最稀缺的资源之一。"}],
    },
    {
        "id": "b9", "title": "平凡的世界", "author": "路遥",
        "cover": "",
        "desc": "以孙少安、孙少平两兄弟为中心，展现普通人在大时代中的奋斗。",
        "tags": ["小说", "文学", "人生"], "rating": 9.2,
        "notes": [{"id": "n9", "bookId": "b9", "content": "生活不能等待别人来安排，要自己去争取和奋斗。"}],
    },
    {
        "id": "b10", "title": "思考，快与慢", "author": "丹尼尔·卡尼曼",
        "cover": "",
        "desc": "诺贝尔经济学奖得主揭示大脑两套思维系统，影响决策判断。",
        "tags": ["心理", "思维", "社科"], "rating": 8.9,
        "notes": [{"id": "n10", "bookId": "b10", "content": "系统 1 快速直觉，系统 2 慢速理性，两者共同塑造判断。"}],
    },
    {
        "id": "b11", "title": "置身事内", "author": "兰小欢",
        "cover": "",
        "desc": "理解中国政府与经济发展，从地方政府的角度读懂中国经济。",
        "tags": ["经济", "社科", "中国"], "rating": 9.0,
        "notes": [{"id": "n11", "bookId": "b11", "content": "要理解中国经济，必须理解中国政府。"}],
    },
    {
        "id": "b12", "title": "代码整洁之道", "author": "罗伯特·马丁",
        "cover": "",
        "desc": "程序员必读：如何写出整洁、可维护、可读的代码。",
        "tags": ["编程", "工程", "成长"], "rating": 8.8,
        "notes": [{"id": "n12", "bookId": "b12", "content": "代码的阅读次数远多于编写次数，可读性就是生产力。"}],
    },
    {
        "id": "b13", "title": "百年孤独", "author": "加西亚·马尔克斯",
        "cover": "",
        "desc": "布恩迪亚家族七代人的传奇，魔幻现实主义的巅峰之作。",
        "tags": ["小说", "文学", "人生"], "rating": 9.3,
        "notes": [{"id": "n13", "bookId": "b13", "content": "生命中曾经有过的所有灿烂，终究都要用寂寞来偿还。"}],
    },
    {
        "id": "b14", "title": "明朝那些事儿", "author": "当年明月",
        "cover": "",
        "desc": "用轻松幽默的笔法讲述明朝三百年历史，读史像读小说。",
        "tags": ["历史", "中国", "趣味"], "rating": 9.1,
        "notes": [{"id": "n14", "bookId": "b14", "content": "历史本身很精彩，历史也可以写得很好看。"}],
    },
    {
        "id": "b15", "title": "非暴力沟通", "author": "马歇尔·卢森堡",
        "cover": "",
        "desc": "一种基于同理心的沟通方式：观察、感受、需要、请求。",
        "tags": ["心理", "沟通", "成长"], "rating": 8.8,
        "notes": [{"id": "n15", "bookId": "b15", "content": "当我们的语言和行动充满爱，冲突也会迎刃而解。"}],
    },
    {
        "id": "b16", "title": "金字塔原理", "author": "芭芭拉·明托",
        "cover": "",
        "desc": "结构化表达与逻辑思考的经典，让写作和汇报更有条理。",
        "tags": ["思维", "表达", "职场"], "rating": 8.6,
        "notes": [{"id": "n16", "bookId": "b16", "content": "结论先行，以上统下，归类分组，逻辑递进。"}],
    },
    {
        "id": "b17", "title": "精益创业", "author": "埃里克·莱斯",
        "cover": "",
        "desc": "用最小可行产品快速验证想法，在反馈中迭代的创业方法论。",
        "tags": ["商业", "创业", "效率"], "rating": 8.6,
        "notes": [{"id": "n17", "bookId": "b17", "content": "成功的创业是建立在学习和适应之上，而非完美计划。"}],
    },
    {
        "id": "b18", "title": "时间简史", "author": "史蒂芬·霍金",
        "cover": "",
        "desc": "从大爆炸到黑洞，用通俗语言讲透宇宙的起源与命运。",
        "tags": ["科学", "宇宙", "科普"], "rating": 9.0,
        "notes": [{"id": "n18", "bookId": "b18", "content": "宇宙有开端吗？如果有，开端之前又是什么？"}],
    },
    {
        "id": "b19", "title": "认知觉醒", "author": "周岭",
        "cover": "",
        "desc": "开启自我改变的原动力：如何用认知驱动行动与成长。",
        "tags": ["成长", "心理", "思维"], "rating": 8.9,
        "notes": [{"id": "n19", "bookId": "b19", "content": "认知越清晰，行动越坚定。"}],
    },
    {
        "id": "b20", "title": "围城", "author": "钱钟书",
        "cover": "",
        "desc": "城里的人想出去，城外的人想进来——一部关于婚姻与人生的讽刺经典。",
        "tags": ["小说", "文学", "人生"], "rating": 9.0,
        "notes": [{"id": "n20", "bookId": "b20", "content": "婚姻是一座围城，城外的人想进去，城里的人想出来。"}],
    },
    {
        "id": "b21", "title": "原则", "author": "瑞·达利欧",
        "cover": "",
        "desc": "桥水基金创始人的生活与工作原则：拥抱现实、极度求真。",
        "tags": ["成长", "职场", "思维"], "rating": 8.9,
        "notes": [{"id": "n21", "bookId": "b21", "content": "痛苦 + 反思 = 进步。"}],
    },
    {
        "id": "b22", "title": "动物庄园", "author": "乔治·奥威尔",
        "cover": "",
        "desc": "一部政治寓言：动物推翻人类统治后的乌托邦如何走向异化。",
        "tags": ["小说", "政治", "寓言"], "rating": 9.0,
        "notes": [{"id": "n22", "bookId": "b22", "content": "所有动物生来平等，但有些动物比其他动物更平等。"}],
    },
    {
        "id": "b23", "title": "增长黑客", "author": "范冰",
        "cover": "",
        "desc": "以数据驱动的方式实现产品的低成本快速增长。",
        "tags": ["商业", "运营", "互联网"], "rating": 8.5,
        "notes": [{"id": "n23", "bookId": "b23", "content": "增长黑客是用数据驱动的方式做产品推广。"}],
    },
    {
        "id": "b24", "title": "深入理解计算机系统", "author": "兰德尔·布赖恩特",
        "cover": "",
        "desc": "从程序员视角理解计算机硬件与系统，经典 CSAPP 教材。",
        "tags": ["编程", "计算机", "工程"], "rating": 9.0,
        "notes": [{"id": "n24", "bookId": "b24", "content": "程序员对计算机系统的理解越深，写出的代码越好。"}],
    },
    {
        "id": "b25", "title": "万历十五年", "author": "黄仁宇",
        "cover": "",
        "desc": "以 1587 年为切片，剖析明代政治制度与社会的深层结构。",
        "tags": ["历史", "中国", "社科"], "rating": 9.0,
        "notes": [{"id": "n25", "bookId": "b25", "content": "以史为鉴，可知兴替；以大历史观看中国。"}],
    },
    {
        "id": "b26", "title": "断舍离", "author": "山下英子",
        "cover": "",
        "desc": "通过整理物品审视内心，学会放下，获得轻盈的生活。",
        "tags": ["生活", "整理", "成长"], "rating": 8.3,
        "notes": [{"id": "n26", "bookId": "b26", "content": "断舍离不是减少物品，而是找回自己的生活。"}],
    },
    {
        "id": "b27", "title": "史蒂夫·乔布斯传", "author": "沃尔特·艾萨克森",
        "cover": "",
        "desc": "乔布斯唯一授权的传记，记录他改变世界的产品哲学。",
        "tags": ["传记", "商业", "科技"], "rating": 8.9,
        "notes": [{"id": "n27", "bookId": "b27", "content": "Stay hungry, stay foolish."}],
    },
    {
        "id": "b28", "title": "经济学原理", "author": "N.格里高利·曼昆",
        "cover": "",
        "desc": "经济学入门圣经，十大经济学原理清晰易懂。",
        "tags": ["经济", "入门", "社科"], "rating": 9.0,
        "notes": [{"id": "n28", "bookId": "b28", "content": "人们面临权衡取舍，天下没有免费的午餐。"}],
    },
    {
        "id": "b29", "title": "白夜行", "author": "东野圭吾",
        "cover": "",
        "desc": "一桩命案牵出两个灵魂的漫长守护，悬疑推理经典。",
        "tags": ["小说", "悬疑", "推理"], "rating": 8.9,
        "notes": [{"id": "n29", "bookId": "b29", "content": "我的天空里没有太阳，总是黑夜，但并不暗。"}],
    },
    {
        "id": "b30", "title": "刻意练习", "author": "安德斯·艾利克森",
        "cover": "",
        "desc": "从新手到大师的路径：有目的、有反馈、走出舒适区地练习。",
        "tags": ["成长", "效率", "心理"], "rating": 8.7,
        "notes": [{"id": "n30", "bookId": "b30", "content": "杰出不是天赋，而是刻意练习的产物。"}],
    },
    {
        "id": "b31", "title": "长安的荔枝", "author": "马伯庸",
        "cover": "",
        "desc": "一个小吏运送鲜荔枝的古代职场历险，见微知著。",
        "tags": ["小说","历史","趣味"], "rating": 8.9,
        "notes": [{"id": "n31", "bookId": "b31", "content": "流程是弱者才要遵循的规矩，强者眼里没有流程。"}],
    },
    {
        "id": "b32", "title": "纳瓦尔宝典", "author": "埃里克·乔根森",
        "cover": "",
        "desc": "关于财富与幸福的底层逻辑：把自己产品化。",
        "tags": ["成长","财富","思维"], "rating": 8.7,
        "notes": [{"id": "n32", "bookId": "b32", "content": "致富不是靠运气，而是靠特定知识、责任感和杠杆。"}],
    },
    {
        "id": "b33", "title": "掌控习惯", "author": "詹姆斯·克利尔",
        "cover": "",
        "desc": "让好习惯显而易见、有吸引力、简单易行、令人愉悦。",
        "tags": ["成长","习惯","效率"], "rating": 8.9,
        "notes": [{"id": "n33", "bookId": "b33", "content": "每天进步 1%，一年后你会好 37 倍。"}],
    },
    {
        "id": "b34", "title": "呐喊", "author": "鲁迅",
        "cover": "",
        "desc": "中国现代文学的开山之作，直指国民性的经典小说集。",
        "tags": ["小说","文学","经典"], "rating": 9,
        "notes": [{"id": "n34", "bookId": "b34", "content": "横眉冷对千夫指，俯首甘为孺子牛。"}],
    },
    {
        "id": "b35", "title": "人类群星闪耀时", "author": "斯蒂芬·茨威格",
        "cover": "",
        "desc": "14 个决定世界历史的瞬间，传记文学的经典。",
        "tags": ["历史","传记","文学"], "rating": 9,
        "notes": [{"id": "n35", "bookId": "b35", "content": "历史是世界上最伟大的诗人和戏剧家。"}],
    },
    {
        "id": "b36", "title": "苏东坡传", "author": "林语堂",
        "cover": "",
        "desc": "一蓑烟雨任平生，看东坡先生的旷达与才情。",
        "tags": ["传记","文学","历史"], "rating": 8.9,
        "notes": [{"id": "n36", "bookId": "b36", "content": "人生到处知何似，应似飞鸿踏雪泥。"}],
    },
    {
        "id": "b37", "title": "小狗钱钱", "author": "博多·舍费尔",
        "cover": "",
        "desc": "用童话讲理财：储蓄、梦想、鹅与金蛋。",
        "tags": ["理财","入门","成长"], "rating": 8.9,
        "notes": [{"id": "n37", "bookId": "b37", "content": "你只有两个选择：想，还是行动。"}],
    },
    {
        "id": "b38", "title": "三体Ⅱ·黑暗森林", "author": "刘慈欣",
        "cover": "",
        "desc": "宇宙社会学与黑暗森林法则，科幻史诗的巅峰章节。",
        "tags": ["科幻","小说","宇宙"], "rating": 9.4,
        "notes": [{"id": "n38", "bookId": "b38", "content": "宇宙就是一座黑暗森林，每个文明都是带枪的猎人。"}],
    },
    {
        "id": "b39", "title": "银河帝国", "author": "艾萨克·阿西莫夫",
        "cover": "",
        "desc": "基地系列开篇，心理史学与银河帝国的宏大叙事。",
        "tags": ["科幻","小说","宇宙"], "rating": 9.2,
        "notes": [{"id": "n39", "bookId": "b39", "content": "暴力是无能者的最后手段。"}],
    },
    {
        "id": "b40", "title": "乡土中国", "author": "费孝通",
        "cover": "",
        "desc": "理解中国社会的经典之作：差序格局、礼治秩序。",
        "tags": ["社科","中国","历史"], "rating": 9,
        "notes": [{"id": "n40", "bookId": "b40", "content": "从土里长出过光荣的历史，自然也会受到土的束缚。"}],
    },
    {
        "id": "b41", "title": "牛奶可乐经济学", "author": "罗伯特·弗兰克",
        "cover": "",
        "desc": "用生活现象讲经济学原理，妙趣横生。",
        "tags": ["经济","趣味","入门"], "rating": 8.6,
        "notes": [{"id": "n41", "bookId": "b41", "content": "经济学不只是公式，更是理解世界的方式。"}],
    },
    {
        "id": "b42", "title": "乌合之众", "author": "古斯塔夫·勒庞",
        "cover": "",
        "desc": "群体心理学的开山之作：个人一旦融入群体便不再理性。",
        "tags": ["心理","社科","社会"], "rating": 8.7,
        "notes": [{"id": "n42", "bookId": "b42", "content": "群体中的个人是沙中之沙，风可以随意搅动他。"}],
    },
    {
        "id": "b43", "title": "第二性", "author": "西蒙娜·波伏娃",
        "cover": "",
        "desc": "女性主义奠基之作：女人不是天生的，而是后天形成的。",
        "tags": ["社科","哲学","社会"], "rating": 8.8,
        "notes": [{"id": "n43", "bookId": "b43", "content": "女人不是天生的，而是被塑造成的。"}],
    },
    {
        "id": "b44", "title": "禅与摩托车维修艺术", "author": "罗伯特·波西格",
        "cover": "",
        "desc": "在旅行与修理中探讨「良质」与人生的哲学之书。",
        "tags": ["哲学","成长","人生"], "rating": 8.7,
        "notes": [{"id": "n44", "bookId": "b44", "content": "对事物保持关注，良质就会自然浮现。"}],
    },
    {
        "id": "b45", "title": "解忧杂货店", "author": "东野圭吾",
        "cover": "",
        "desc": "一间能解答烦恼的杂货店，温暖治愈的时空联结。",
        "tags": ["小说","治愈","推理"], "rating": 8.9,
        "notes": [{"id": "n45", "bookId": "b45", "content": "你的地图是一张白纸，所以一切都可以自由地涂画。"}],
    },
    {
        "id": "b46", "title": "硅谷钢铁侠", "author": "阿什利·万斯",
        "cover": "",
        "desc": "埃隆·马斯克的早期传记：从 PayPal 到 SpaceX 与特斯拉。",
        "tags": ["传记","科技","商业"], "rating": 8.7,
        "notes": [{"id": "n46", "bookId": "b46", "content": "要么不做，要么做到最好。"}],
    },
    {
        "id": "b47", "title": "高效能人士的七个习惯", "author": "史蒂芬·柯维",
        "cover": "",
        "desc": "积极主动、以终为始、要事第一……个人效能的经典框架。",
        "tags": ["成长","效率","职场"], "rating": 8.8,
        "notes": [{"id": "n47", "bookId": "b47", "content": "先改变自己，再改变环境。"}],
    },
    {
        "id": "b48", "title": "三体Ⅲ·死神永生", "author": "刘慈欣",
        "cover": "",
        "desc": "宇宙的终局与文明的延续，黑暗森林故事的完结篇。",
        "tags": ["科幻","小说","宇宙"], "rating": 9.3,
        "notes": [{"id": "n48", "bookId": "b48", "content": "弱小和无知不是生存的障碍，傲慢才是。"}],
    },
    {
        "id": "b49", "title": "富爸爸穷爸爸", "author": "罗伯特·清崎",
        "cover": "",
        "desc": "财商启蒙经典：让钱为你工作，而不是为钱工作。",
        "tags": ["理财","成长","入门"], "rating": 8.7,
        "notes": [{"id": "n49", "bookId": "b49", "content": "资产是能把钱放进你口袋的东西。"}],
    },
    {
        "id": "b50", "title": "人间失格", "author": "太宰治",
        "cover": "",
        "desc": "太宰治的半自传小说，关于生而为人、我很抱歉。",
        "tags": ["小说","文学","人生"], "rating": 8.6,
        "notes": [{"id": "n50", "bookId": "b50", "content": "生而为人，我很抱歉。"}],
    },
    {
        "id": "b51", "title": "红楼梦", "author": "曹雪芹",
        "cover": "",
        "desc": "中国古典小说巅峰，以四大家族的兴衰写尽世态人情。",
        "tags": ["小说","文学","经典"], "rating": 9.6,
        "notes": [{"id": "n51", "bookId": "b51", "content": "世事洞明皆学问，人情练达即文章。"}],
    },
    {
        "id": "b52", "title": "三国演义", "author": "罗贯中",
        "cover": "",
        "desc": "群雄逐鹿的乱世画卷，权谋与忠义的古典史诗。",
        "tags": ["小说","历史","经典"], "rating": 9.2,
        "notes": [{"id": "n52", "bookId": "b52", "content": "天下大势，分久必合，合久必分。"}],
    },
    {
        "id": "b53", "title": "水浒传", "author": "施耐庵",
        "cover": "",
        "desc": "一百单八将的聚义与散落，写尽江湖恩怨与命运起伏。",
        "tags": ["小说","文学","经典"], "rating": 8.9,
        "notes": [{"id": "n53", "bookId": "b53", "content": "有恩必报，有仇必复，快意人生。"}],
    },
    {
        "id": "b54", "title": "西游记", "author": "吴承恩",
        "cover": "",
        "desc": "师徒四人西天取经，一路降妖除魔，也一路修心见性。",
        "tags": ["小说","奇幻","经典"], "rating": 9.1,
        "notes": [{"id": "n54", "bookId": "b54", "content": "敢问路在何方，路在脚下。"}],
    },
    {
        "id": "b55", "title": "骆驼祥子", "author": "老舍",
        "cover": "",
        "desc": "人力车夫祥子三起三落的一生，一部旧时代底层命运史。",
        "tags": ["小说","文学","人生"], "rating": 8.8,
        "notes": [{"id": "n55", "bookId": "b55", "content": "体面的、要强的，最终都成了自己不想成为的样子。"}],
    },
    {
        "id": "b56", "title": "边城", "author": "沈从文",
        "cover": "",
        "desc": "湘西小镇的清澈爱情与淡淡哀愁，田园牧歌式经典。",
        "tags": ["小说","文学","治愈"], "rating": 9.0,
        "notes": [{"id": "n56", "bookId": "b56", "content": "凡事都有偶然的凑巧，结果却又如宿命的必然。"}],
    },
    {
        "id": "b57", "title": "呼兰河传", "author": "萧红",
        "cover": "",
        "desc": "东北小城的风土与生死，在荒凉中透出温柔的追忆。",
        "tags": ["小说","文学","人生"], "rating": 8.8,
        "notes": [{"id": "n57", "bookId": "b57", "content": "人生为了什么，才有这样凄凉的夜。"}],
    },
    {
        "id": "b58", "title": "城南旧事", "author": "林海音",
        "cover": "",
        "desc": "小女孩英子眼中的北平往事，清澈又略带怅惘。",
        "tags": ["小说","文学","治愈"], "rating": 8.9,
        "notes": [{"id": "n58", "bookId": "b58", "content": "无论什么困难的事，只要硬着头皮去做，就闯过去了。"}],
    },
    {
        "id": "b59", "title": "朝花夕拾", "author": "鲁迅",
        "cover": "",
        "desc": "鲁迅对童年与师友的温情回忆，散文中的经典名篇。",
        "tags": ["散文","文学","经典"], "rating": 8.8,
        "notes": [{"id": "n59", "bookId": "b59", "content": "人生也许就是这样了，既然是路，就总有走过去的办法。"}],
    },
    {
        "id": "b60", "title": "我与地坛", "author": "史铁生",
        "cover": "",
        "desc": "在轮椅上与地坛对话，在苦难中寻找生命的意义。",
        "tags": ["散文","哲学","人生"], "rating": 9.1,
        "notes": [{"id": "n60", "bookId": "b60", "content": "死是一件不必急于求成的事，死是一个必然会降临的节日。"}],
    },
    {
        "id": "b61", "title": "局外人", "author": "阿尔贝·加缪",
        "cover": "",
        "desc": "荒诞哲学的文学宣言：一个对世界无动于衷的局外人。",
        "tags": ["小说","哲学","文学"], "rating": 9.0,
        "notes": [{"id": "n61", "bookId": "b61", "content": "人生在世，永远也不该演戏作假。"}],
    },
    {
        "id": "b62", "title": "老人与海", "author": "欧内斯特·海明威",
        "cover": "",
        "desc": "老渔夫与大鱼的搏斗，一个人可以被毁灭但不能被打败。",
        "tags": ["小说","文学","人生"], "rating": 8.9,
        "notes": [{"id": "n62", "bookId": "b62", "content": "一个人可以被毁灭，但不能被打败。"}],
    },
    {
        "id": "b63", "title": "了不起的盖茨比", "author": "菲茨杰拉德",
        "cover": "",
        "desc": "爵士时代的一场幻梦，关于美国梦的破灭与痴情。",
        "tags": ["小说","文学","美国"], "rating": 8.8,
        "notes": [{"id": "n63", "bookId": "b63", "content": "于是我们继续奋力向前，逆水行舟，被不断地向后推。"}],
    },
    {
        "id": "b64", "title": "麦田里的守望者", "author": "J.D.塞林格",
        "cover": "",
        "desc": "少年霍尔顿的愤怒与迷茫，战后美国的青春经典。",
        "tags": ["小说","成长","文学"], "rating": 8.5,
        "notes": [{"id": "n64", "bookId": "b64", "content": "记住该记住的，忘记该忘记的；改变能改变的，接受不能改变的。"}],
    },
    {
        "id": "b65", "title": "挪威的森林", "author": "村上春树",
        "cover": "",
        "desc": "爱与失去、生与死的青春物语，村上春树最畅销的作品。",
        "tags": ["小说","文学","爱情"], "rating": 8.7,
        "notes": [{"id": "n65", "bookId": "b65", "content": "每个人都有属于自己的一片森林。"}],
    },
    {
        "id": "b66", "title": "追风筝的人", "author": "卡勒德·胡赛尼",
        "cover": "",
        "desc": "关于友谊、背叛与救赎的故事，为你千千万万遍。",
        "tags": ["小说","文学","人生"], "rating": 8.9,
        "notes": [{"id": "n66", "bookId": "b66", "content": "为你，千千万万遍。"}],
    },
    {
        "id": "b67", "title": "岛上书店", "author": "加布瑞埃拉·泽文",
        "cover": "",
        "desc": "一座孤岛书店的温暖日常，书把孤独的人连在一起。",
        "tags": ["小说","治愈","文学"], "rating": 8.3,
        "notes": [{"id": "n67", "bookId": "b67", "content": "没有谁是一座孤岛，每本书都是一个世界。"}],
    },
    {
        "id": "b68", "title": "献给阿尔吉侬的花束", "author": "丹尼尔·凯斯",
        "cover": "",
        "desc": "智力实验的日记体科幻，追问智慧、情感与尊严。",
        "tags": ["科幻","小说","成长"], "rating": 8.9,
        "notes": [{"id": "n68", "bookId": "b68", "content": "如果没有人性情感的调和，智慧与教育根本毫无价值。"}],
    },
    {
        "id": "b69", "title": "沙丘", "author": "弗兰克·赫伯特",
        "cover": "",
        "desc": "沙漠星球上的权力、宗教与生态史诗，科幻文学的丰碑。",
        "tags": ["科幻","宇宙","小说"], "rating": 8.8,
        "notes": [{"id": "n69", "bookId": "b69", "content": "恐惧是思维的杀手。"}],
    },
    {
        "id": "b70", "title": "基地", "author": "艾萨克·阿西莫夫",
        "cover": "",
        "desc": "用心理史学预测银河命运，科幻黄金时代的代表作。",
        "tags": ["科幻","小说","宇宙"], "rating": 9.2,
        "notes": [{"id": "n70", "bookId": "b70", "content": "心理史学是未来的数学。"}],
    },
    {
        "id": "b71", "title": "2001太空漫游", "author": "阿瑟·克拉克",
        "cover": "",
        "desc": "从猿人到星孩，一部跨越数百万年的宇宙史诗。",
        "tags": ["科幻","宇宙","科普"], "rating": 8.8,
        "notes": [{"id": "n71", "bookId": "b71", "content": "在宇宙的无限面前，人类不过是瞬间的过客。"}],
    },
    {
        "id": "b72", "title": "仿生人会梦见电子羊吗", "author": "菲利普·迪克",
        "cover": "",
        "desc": "在真假难辨的未来，追问什么是人、什么是真实。",
        "tags": ["科幻","哲学","小说"], "rating": 8.7,
        "notes": [{"id": "n72", "bookId": "b72", "content": "真实与梦境之间的界限，比想象中模糊得多。"}],
    },
    {
        "id": "b73", "title": "火星救援", "author": "安迪·威尔",
        "cover": "",
        "desc": "被困火星的植物学家用科学自救，硬科幻与幽默的结合。",
        "tags": ["科幻","科普","幽默"], "rating": 8.7,
        "notes": [{"id": "n73", "bookId": "b73", "content": "在火星上，你只有靠自己。"}],
    },
    {
        "id": "b74", "title": "上帝掷骰子吗", "author": "曹天元",
        "cover": "",
        "desc": "量子物理的百年历史，把深奥的科学讲得引人入胜。",
        "tags": ["科普","物理","科学"], "rating": 9.1,
        "notes": [{"id": "n74", "bookId": "b74", "content": "量子世界告诉我们，观测本身就是一种参与。"}],
    },
    {
        "id": "b75", "title": "自私的基因", "author": "理查德·道金斯",
        "cover": "",
        "desc": "以基因视角重新理解生命演化，进化论的现代经典。",
        "tags": ["科普","生物","科学"], "rating": 9.0,
        "notes": [{"id": "n75", "bookId": "b75", "content": "我们以及其他一切动物都是自己基因所创造的工具。"}],
    },
    {
        "id": "b76", "title": "基因传", "author": "悉达多·穆克吉",
        "cover": "",
        "desc": "从孟德尔到 CRISPR 的基因科学全景，兼具医学与人文。",
        "tags": ["科普","生物","医学"], "rating": 8.9,
        "notes": [{"id": "n76", "bookId": "b76", "content": "基因是一本不断被改写的生命之书。"}],
    },
    {
        "id": "b77", "title": "未来简史", "author": "尤瓦尔·赫拉利",
        "cover": "",
        "desc": "当人工智能与数据主义崛起，人类将面临全新的议题。",
        "tags": ["社科","未来","思维"], "rating": 8.8,
        "notes": [{"id": "n77", "bookId": "b77", "content": "数据主义将取代人文主义，成为新的宗教。"}],
    },
    {
        "id": "b78", "title": "今日简史", "author": "尤瓦尔·赫拉利",
        "cover": "",
        "desc": "直面当下世界的挑战：技术、政治、战争与真相。",
        "tags": ["社科","未来","思维"], "rating": 8.6,
        "notes": [{"id": "n78", "bookId": "b78", "content": "在信息时代，真相需要比谎言传播得更快。"}],
    },
    {
        "id": "b79", "title": "枪炮、病菌与钢铁", "author": "贾雷德·戴蒙德",
        "cover": "",
        "desc": "从地理与环境解释人类社会的命运差异，宏大而深邃。",
        "tags": ["历史","社科","人类学"], "rating": 8.9,
        "notes": [{"id": "n79", "bookId": "b79", "content": "不同社会的命运，往往取决于地理与环境。"}],
    },
    {
        "id": "b80", "title": "叫魂", "author": "孔飞力",
        "cover": "",
        "desc": "1768 年妖术大恐慌背后，清代中国社会的权力运作。",
        "tags": ["历史","社会","中国"], "rating": 8.9,
        "notes": [{"id": "n80", "bookId": "b80", "content": "权力在民众与官府之间的流动，构成了中国社会的隐秘结构。"}],
    },
    {
        "id": "b81", "title": "中国近代史", "author": "蒋廷黻",
        "cover": "",
        "desc": "简明有力的近代中国通史，理解救亡与启蒙的经典读本。",
        "tags": ["历史","中国","社科"], "rating": 8.7,
        "notes": [{"id": "n81", "bookId": "b81", "content": "近代中国的主题，是向西方学习与民族自救。"}],
    },
    {
        "id": "b82", "title": "南渡北归", "author": "岳南",
        "cover": "",
        "desc": "抗战时期大师们南渡与北归的迁徙史，一代学人的精神图谱。",
        "tags": ["历史","传记","中国"], "rating": 8.9,
        "notes": [{"id": "n82", "bookId": "b82", "content": "大师远去，再无大师。"}],
    },
    {
        "id": "b83", "title": "洗澡", "author": "杨绛",
        "cover": "",
        "desc": "知识分子在时代浪潮中的自我洗炼，杨绛代表作之一。",
        "tags": ["小说","文学","人生"], "rating": 8.8,
        "notes": [{"id": "n83", "bookId": "b83", "content": "洗去身上的尘垢，也洗去心上的尘埃。"}],
    },
    {
        "id": "b84", "title": "我们仨", "author": "杨绛",
        "cover": "",
        "desc": "杨绛对钱钟书与女儿的家庭回忆，平淡中见深情。",
        "tags": ["散文","传记","治愈"], "rating": 9.0,
        "notes": [{"id": "n84", "bookId": "b84", "content": "我们仨，在一起，就是最好的时光。"}],
    },
    {
        "id": "b85", "title": "干校六记", "author": "杨绛",
        "cover": "",
        "desc": "特殊年代里的生活记录，苦难中仍有温情与幽默。",
        "tags": ["散文","历史","文学"], "rating": 8.6,
        "notes": [{"id": "n85", "bookId": "b85", "content": "生活的苦难，也会成为记忆里的风景。"}],
    },
    {
        "id": "b86", "title": "走到人生边上", "author": "杨绛",
        "cover": "",
        "desc": "九十岁杨绛对命运、灵魂与人生价值的思考。",
        "tags": ["哲学","人生","散文"], "rating": 8.7,
        "notes": [{"id": "n86", "bookId": "b86", "content": "人生最曼妙的风景，竟是内心的淡定与从容。"}],
    },
    {
        "id": "b87", "title": "沉默的大多数", "author": "王小波",
        "cover": "",
        "desc": "王小波杂文集，关于独立思考、自由与生活常识。",
        "tags": ["散文","社会","思想"], "rating": 8.9,
        "notes": [{"id": "n87", "bookId": "b87", "content": "沉默是一种生活方式，也是一种力量。"}],
    },
    {
        "id": "b88", "title": "黄金时代", "author": "王小波",
        "cover": "",
        "desc": "王小波代表作，写给青春、自由与荒诞的时代。",
        "tags": ["小说","文学","时代"], "rating": 8.8,
        "notes": [{"id": "n88", "bookId": "b88", "content": "那一天我二十一岁，在我一生的黄金时代。"}],
    },
    {
        "id": "b89", "title": "皮囊", "author": "蔡崇达",
        "cover": "",
        "desc": "从闽南小镇出发的成长故事，直面身体与灵魂的重量。",
        "tags": ["散文","成长","人生"], "rating": 8.5,
        "notes": [{"id": "n89", "bookId": "b89", "content": "肉体是拿来用的，不是拿来伺候的。"}],
    },
    {
        "id": "b90", "title": "你当像鸟飞往你的山", "author": "塔拉·韦斯特弗",
        "cover": "",
        "desc": "从大山家庭走向剑桥的自我教育史，关于挣脱与重生。",
        "tags": ["传记","成长","教育"], "rating": 8.9,
        "notes": [{"id": "n90", "bookId": "b90", "content": "教育不是改变你，而是让你看见另一种可能。"}],
    },
    {
        "id": "b91", "title": "月亮与六便士", "author": "毛姆",
        "cover": "",
        "desc": "理想与现实的抉择：满地都是六便士，他却抬头看见了月亮。",
        "tags": ["小说","哲学","人生"], "rating": 9.0,
        "notes": [{"id": "n91", "bookId": "b91", "content": "满地都是六便士，他却抬头看见了月亮。"}],
    },
    {
        "id": "b92", "title": "面纱", "author": "毛姆",
        "cover": "",
        "desc": "一场婚姻与救赎的故事，关于成长与自我觉醒。",
        "tags": ["小说","爱情","人生"], "rating": 8.7,
        "notes": [{"id": "n92", "bookId": "b92", "content": "人无法从别人那里获得救赎，只能自己寻找。"}],
    },
    {
        "id": "b93", "title": "刀锋", "author": "毛姆",
        "cover": "",
        "desc": "拉里对人生意义的追寻，一部精神成长的小说。",
        "tags": ["小说","哲学","成长"], "rating": 8.8,
        "notes": [{"id": "n93", "bookId": "b93", "content": "剃刀锋利，越之不易；智者有云，得渡人稀。"}],
    },
    {
        "id": "b94", "title": "人间词话", "author": "王国维",
        "cover": "",
        "desc": "以境界论词，中国古典文论的现代经典。",
        "tags": ["文学","理论","经典"], "rating": 9.0,
        "notes": [{"id": "n94", "bookId": "b94", "content": "古今之成大事业、大学问者，必经过三种之境界。"}],
    },
    {
        "id": "b95", "title": "美的历程", "author": "李泽厚",
        "cover": "",
        "desc": "从远古图腾到明清文艺，一部中国审美精神史。",
        "tags": ["美学","艺术","文化"], "rating": 8.9,
        "notes": [{"id": "n95", "bookId": "b95", "content": "美是积淀了社会内容的自然形式。"}],
    },
    {
        "id": "b96", "title": "悉达多", "author": "赫尔曼·黑塞",
        "cover": "",
        "desc": "婆罗门青年悉达多的求道之旅，关于觉醒与圆融。",
        "tags": ["哲学","小说","成长"], "rating": 9.0,
        "notes": [{"id": "n96", "bookId": "b96", "content": "智慧无法言传，智者试图传递智慧总像是在说傻话。"}],
    },
    {
        "id": "b97", "title": "德米安", "author": "赫尔曼·黑塞",
        "cover": "",
        "desc": "少年寻找自我的精神成长史，黑塞心理小说的代表作。",
        "tags": ["小说","成长","哲学"], "rating": 8.8,
        "notes": [{"id": "n97", "bookId": "b97", "content": "每个人都是自然向人提出的一个伟大的实验。"}],
    },
    {
        "id": "b98", "title": "程序员修炼之道", "author": "安德鲁·亨特",
        "cover": "",
        "desc": "从程序员到工匠的成长之路，务实与严谨并存。",
        "tags": ["编程","计算机","工程"], "rating": 8.9,
        "notes": [{"id": "n98", "bookId": "b98", "content": "你的代码会被阅读很多次，让它易于阅读。"}],
    },
    {
        "id": "b99", "title": "重构", "author": "马丁·福勒",
        "cover": "",
        "desc": "在不改变外部行为的前提下改善代码设计，工程实践经典。",
        "tags": ["编程","工程","成长"], "rating": 8.8,
        "notes": [{"id": "n99", "bookId": "b99", "content": "重构是改善现有代码设计的受控技术。"}],
    },
    {
        "id": "b100", "title": "浪潮之巅", "author": "吴军",
        "cover": "",
        "desc": "硅谷科技公司的兴衰史，站在浪潮之巅的启示录。",
        "tags": ["科技","商业","历史"], "rating": 9.0,
        "notes": [{"id": "n100", "bookId": "b100", "content": "总有一些公司很幸运地站在了技术革命的浪尖之上。"}],
    },

]

# ==================== 推荐逻辑（后端实现） ====================


def _tokenize(text: str) -> List[str]:
    """把偏好文本按空白和常见分隔符拆成多个关键词。"""
    if not text:
        return []
    parts = re.split(r"[\s,，、;；/|]+", text)
    return [p.strip() for p in parts if p.strip()]


def _score(book: dict, tags: List[str], preference: str) -> int:
    """按标签重叠 + 偏好关键词匹配给书籍打分。"""
    score = 0
    # 标签命中：每个 +2
    for tag in tags or []:
        if tag in book["tags"]:
            score += 2

    # 偏好关键词：命中书名 +4 / 作者 +3 / 简介 +2 / 标签 +1
    for kw in _tokenize(preference):
        k = kw.lower()
        title = book["title"].lower()
        author = book["author"].lower()
        desc = book["desc"].lower()
        if k in title:
            score += 4
        elif k in author:
            score += 3
        if k in desc:
            score += 2
        for tag in book["tags"]:
            if k in tag.lower():
                score += 1
    return score


def _seed_from(tags: List[str], preference: str) -> int:
    """用查询内容生成一个确定性种子，让相同分数时排序随查询变化。"""
    seed = 0
    for s in list(tags or []) + ([preference] if preference else []):
        for ch in s:
            seed = (seed * 31 + ord(ch)) & 0xFFFFFFFF
    return seed or 1


def _tie_breaker(book: dict, seed: int) -> int:
    """同分时的确定性错序：不同查询种子 -> 不同排序，避免每次都是前几本。"""
    h = seed
    for ch in book["id"]:
        h = (h * 33 + ord(ch)) & 0xFFFFFFFF
    return h


def recommend_books(tags: List[str], preference: str, count: int = 5) -> List[dict]:
    """
    按标签 + 偏好筛选排序，返回前 count 本。
    分数优先；同分时按「查询种子」错序，因此不同关键词会得到不同的书单。
    """
    seed = _seed_from(tags, preference)
    scored = sorted(
        BOOKS,
        key=lambda b: (-_score(b, tags, preference), _tie_breaker(b, seed)),
    )
    return scored[:count]


def get_all_books() -> List[dict]:
    """返回全部书单。"""
    return BOOKS


def get_book_detail(book_id: str) -> Optional[dict]:
    """根据 id 返回单本书详情。"""
    return next((b for b in BOOKS if b["id"] == book_id), None)


def get_book_notes(book_id: str) -> List[dict]:
    """根据 id 返回书籍笔记。"""
    book = get_book_detail(book_id)
    return book["notes"] if book else []


def get_statistics() -> dict:
    """书单统计：总数、标签数、笔记数、平均评分。"""
    total = len(BOOKS)
    all_tags = set()
    total_notes = 0
    rating_sum = 0
    for b in BOOKS:
        all_tags.update(b["tags"])
        total_notes += len(b.get("notes", []))
        rating_sum += b.get("rating", 0)
    return {
        "totalBooks": total,
        "totalTags": len(all_tags),
        "totalNotes": total_notes,
        "avgRating": round(rating_sum / total, 1) if total else 0,
    }
