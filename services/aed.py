"""
Audio Event Detection (AED) Service — 环境安全音检测 (状态机与滞回阈值重构版)
"""
import os
import logging
import tempfile
import time
from collections import deque
import numpy as np
import scipy.io.wavfile as wav

logger = logging.getLogger("virtualhuman.aed")

# ================================================================
# 危险声音字典：英文标签 -> (中文翻译, 危险等级, CSS类名)
# 扩展支持：火车、汽车、火警、警报等多种危险声音识别
# ================================================================
DANGER_SOUNDS = {
    # 警报/警笛类
    "siren": ("🚨 警报/警笛", "HIGH", "extreme-danger-alert"),
    "ambulance": ("🚑 救护车警笛", "HIGH", "extreme-danger-alert"),
    "fire alarm": ("🔥 火警铃声", "HIGH", "extreme-danger-alert"),
    "fire truck": ("🚒 消防车", "HIGH", "extreme-danger-alert"),
    "police siren": ("👮 警笛", "HIGH", "extreme-danger-alert"),
    "smoke detector": ("🔥 烟雾探测器", "HIGH", "extreme-danger-alert"),
    "alarm": ("🚨 警报声", "HIGH", "extreme-danger-alert"),
    
    # 汽车/车辆类
    "car horn": ("🚗 汽车鸣笛", "HIGH", "extreme-danger-alert"),
    "vehicle horn": ("🚗 汽车鸣笛", "HIGH", "extreme-danger-alert"),
    "car alarm": ("🚗 汽车防盗警报", "HIGH", "extreme-danger-alert"),
    "engine": ("🚗 发动机", "MEDIUM", "warning-alert"),
    "tire screeching": ("🚗 轮胎尖叫", "MEDIUM", "warning-alert"),
    "car": ("🚗 汽车", "MEDIUM", "warning-alert"),
    "vehicle": ("🚗 车辆", "MEDIUM", "warning-alert"),
    "motorcycle": ("🏍️ 摩托车", "MEDIUM", "warning-alert"),
    "truck": ("🚚 卡车", "MEDIUM", "warning-alert"),
    "bus": ("🚌 公交车", "MEDIUM", "warning-alert"),
    
    # 火车/铁路类
    "train": ("🚂 火车鸣笛", "HIGH", "extreme-danger-alert"),
    "train horn": ("🚂 火车鸣笛", "HIGH", "extreme-danger-alert"),
    "railway": ("🚂 铁路/火车", "HIGH", "extreme-danger-alert"),
    "locomotive": ("🚂 火车头", "HIGH", "extreme-danger-alert"),
    "rail": ("🚂 铁轨声", "MEDIUM", "warning-alert"),
    "subway": ("🚇 地铁", "MEDIUM", "warning-alert"),
    
    # 危险破坏类
    "glass": ("💥 玻璃碎裂", "HIGH", "extreme-danger-alert"),
    "glass break": ("💥 玻璃破碎", "HIGH", "extreme-danger-alert"),
    "smash": ("💥 砸碎声", "HIGH", "extreme-danger-alert"),
    "explosion": ("💥 爆炸声", "HIGH", "extreme-danger-alert"),
    "gunshot": ("🔫 枪声", "HIGH", "extreme-danger-alert"),
    "gun fire": ("🔫 枪声", "HIGH", "extreme-danger-alert"),
    
    # 需要关注的弱势群体声音
    "crying": ("👶 婴儿啼哭", "MEDIUM", "warning-alert"),
    "baby cry": ("👶 婴儿啼哭", "MEDIUM", "warning-alert"),
    "baby": ("👶 婴儿", "MEDIUM", "warning-alert"),
    "scream": ("😱 尖叫", "HIGH", "extreme-danger-alert"),
    "shout": ("📢 呼喊", "MEDIUM", "warning-alert"),
    "help": ("🆘 呼救", "HIGH", "extreme-danger-alert"),
}

# ================================================================
# 过滤类声音：日常环境音，人声等不危险的声音
# 这些声音不会触发警报，但会被记录
# ================================================================
FILTER_SOUNDS = {
    # 人声/对话
    "speech": ("🗣️ 人声", "FILTER"),
    "conversation": ("🗣️ 对话", "FILTER"),
    "laughter": ("😂 笑声", "FILTER"),
    "laughing": ("😂 笑声", "FILTER"),
    "voice": ("🗣️ 声音", "FILTER"),
    "human voice": ("🗣️ 人声", "FILTER"),
    "male speech": ("👨 男性说话", "FILTER"),
    "female speech": ("👩 女性说话", "FILTER"),
    "children": ("👶 儿童", "FILTER"),
    "crowd": ("👥 人群", "FILTER"),
    "muted": ("🔇 静音", "FILTER"),
    
    # 自然环境音
    "wind": ("💨 风声", "FILTER"),
    "rain": ("🌧️ 雨声", "FILTER"),
    "thunder": ("⛈️ 雷声", "FILTER"),
    "water": ("💧 水声", "FILTER"),
    "stream": ("🌊 流水", "FILTER"),
    "birds": ("🐦 鸟叫", "FILTER"),
    "dog": ("🐕 狗叫", "FILTER"),
    "dog bark": ("🐕 狗吠", "FILTER"),
    "cat": ("🐱 猫叫", "FILTER"),
    "insects": ("🦗 虫鸣", "FILTER"),
    
    # 室内日常声音
    "footsteps": ("👣 脚步声", "FILTER"),
    "footstep": ("👣 脚步声", "FILTER"),
    "doorbell": ("🚪 门铃", "FILTER"),  # 门铃改为过滤，不触发警报
    "knock": ("🚪 敲门", "FILTER"),    # 敲门改为过滤
    "typing": ("⌨️ 打字", "FILTER"),
    "keyboard": ("⌨️ 键盘", "FILTER"),
    "washing": ("🧺 洗涤", "FILTER"),
    "vacuum": ("🧹 吸尘", "FILTER"),
    "clock": ("🕐 时钟", "FILTER"),
    
    # 电器/背景音
    "air conditioner": ("❄️ 空调", "FILTER"),
    "fan": ("🌀 风扇", "FILTER"),
    "refrigerator": ("🧊 冰箱", "FILTER"),
    "washing machine": ("🧺 洗衣机", "FILTER"),
    "drill": ("🔧 电钻", "FILTER"),
    "hammer": ("🔨 锤子", "FILTER"),
    "silence": ("🔇 静音", "FILTER"),
    "quiet": ("🔇 安静", "FILTER"),
}

class AEDStateManager:
    """环境音状态管理器：使用滑动窗口与滞回阈值，解决误报与不解除问题
    支持双模式：1) 分贝模式（基于实际音量变化判断距离）2) 置信度模式（备用）"""
    
    def __init__(self, window_size=5, trigger_avg=0.6, trigger_single=0.8, release_avg=0.2, cooldown=3.0,
                 db_window_size=10, db_trigger=65.0, db_release=55.0, db_decrease_threshold=5.0):
        self.window_size = window_size          # 记录过去 5 帧
        self.trigger_avg = trigger_avg          # 触发阈值（置信度平均分）
        self.trigger_single = trigger_single    # 触发阈值（单帧极高分，应对急促短音）
        self.release_avg = release_avg          # 解除阈值（置信度平均分）
        self.cooldown = cooldown                # 警报冷却时间（秒）

        # ========== 新增：分贝/距离模式参数 ==========
        self.db_window_size = db_window_size   # 分贝历史记录窗口大小
        self.db_trigger = db_trigger           # 分贝触发阈值 (dB)
        self.db_release = db_release           # 分贝解除阈值 (dB)  
        self.db_decrease_threshold = db_decrease_threshold  # 分贝下降多少判定为远离 (dB)
        self.use_db_mode = True                # 是否启用分贝模式（更准确）
        # =============================================
        
        self.history = {}                       # 字典：存储不同 label 的 deque 得分队列
        self.db_history = deque(maxlen=db_window_size)  # 分贝历史记录
        self.is_alerting = False                # 当前是否处于报警状态
        self.last_alert_time = 0.0              # 上次触发/刷新报警的时间戳
        self.current_danger_info = None         # 当前报警的 UI 配置 (zh_label, level, css)
        self.current_alert_label = None         # 触发警报的原始英文 label
        self.alert_trigger_db = None           # 触发警报时的分贝值（用于判断是否降低）
        self.mode_used = "NONE"                 # 记录使用的模式：DB 或 CONFIDENCE

    def update_and_check(self, label: str, score: float, danger_info: tuple = None, db_level: float = None) -> dict:
        """更新状态并检查是否触发/解除警报
        
        Args:
            label: 识别到的声音标签
            score: 置信度分数 (0-1)
            danger_info: 危险信息元组 (中文标签, 危险等级, CSS类)
            db_level: 实际分贝值 (dB)，如果提供则使用分贝模式
        """
        current_time = time.time()
        
        # ========== 更新分贝历史 ==========
        if db_level is not None:
            self.db_history.append(db_level)
            logger.info(f"📊 [分贝模式] 当前: {db_level:.1f}dB, 历史均值: {np.mean(self.db_history):.1f}dB")
        # =================================

        # 1. 队列更新逻辑（处理静音与正常声音）
        if label is None or label == "silence":
            # 如果是静音，给所有正在追踪的队列都塞入 0.0，加速平均分稀释
            for k in self.history.keys():
                self.history[k].append(0.0)
            # 分贝历史也填入最小值
            if db_level is None:
                self.db_history.append(0.0)
        else:
            # 针对当前识别到的声音填入得分
            if label not in self.history:
                self.history[label] = deque([0.0] * self.window_size, maxlen=self.window_size)
            
            for k in self.history.keys():
                if k == label:
                    self.history[k].append(score)
                else:
                    self.history[k].append(0.0)

        # 2. 滞回阈值 (Schmitt Trigger) 计算逻辑
        if self.is_alerting:
            # --- 尝试解除警报 ---
            if self.current_alert_label in self.history:
                avg_score = sum(self.history[self.current_alert_label]) / self.window_size
            else:
                avg_score = 0.0
            
            # ========== 分贝模式：判断是否远离 ==========
            should_release_db = False
            release_reason = ""
            
            if self.use_db_mode and db_level is not None and len(self.db_history) >= 3:
                # 计算最近分贝变化趋势
                recent_dbs = list(self.db_history)[-5:]  # 最近5个
                avg_recent = np.mean(recent_dbs)
                
                # 判断是否正在远离（分贝显著下降）
                db_decrease = self.alert_trigger_db - db_level if self.alert_trigger_db else 0
                
                # 解除条件：
                # 1. 分贝下降到释放阈值以下，且
                # 2. 相比触发时下降了超过阈值（说明距离变远了），且
                # 3. 经过了冷却时间
                if (db_level < self.db_release and 
                    db_decrease >= self.db_decrease_threshold and
                    (current_time - self.last_alert_time) >= self.cooldown):
                    should_release_db = True
                    release_reason = f"分贝下降: {self.alert_trigger_db:.1f}dB → {db_level:.1f}dB (下降{db_decrease:.1f}dB，距离变远)"
                    self.mode_used = "DB"
                elif db_level < self.db_release and (current_time - self.last_alert_time) >= self.cooldown:
                    # 分贝降低了但没达到阈值，也释放（基于绝对值）
                    should_release_db = True
                    release_reason = f"分贝降至安全水平: {db_level:.1f}dB < {self.db_release}dB"
                    self.mode_used = "DB"
            
            # 如果分贝模式未能解除，使用置信度模式作为备用
            if not should_release_db:
                # 置信度模式解除条件
                if avg_score < self.release_avg and (current_time - self.last_alert_time) >= self.cooldown:
                    should_release_db = True
                    release_reason = f"置信度降至安全: {avg_score:.2f} < {self.release_avg}"
                    self.mode_used = "CONFIDENCE"
                else:
                    # 处于报警状态，且平均分仍在飙高，重置冷却时间 (刷新警报)
                    if avg_score > self.trigger_avg:
                        self.last_alert_time = current_time
            
            if should_release_db:
                logger.info(f"✅ 警报解除: {self.current_alert_label} ({release_reason})")
                self.is_alerting = False
                self.current_danger_info = None
                self.current_alert_label = None
                self.alert_trigger_db = None

        # 注意：不要用 elif，如果刚解除，同一帧可以触发新声音
        if not self.is_alerting and label and label != "silence" and danger_info:
            # --- 尝试触发新警报 ---
            avg_score = sum(self.history[label]) / self.window_size
            
            # ========== 双模式触发判断 ==========
            trigger_reason = ""
            triggered = False
            
            if self.use_db_mode and db_level is not None:
                # 分贝模式触发
                if db_level >= self.db_trigger:
                    triggered = True
                    trigger_reason = f"分贝触发: {db_level:.1f}dB >= {self.db_trigger}dB"
                    self.mode_used = "DB"
                    self.alert_trigger_db = db_level  # 记录触发时的分贝值
            
            # 如果分贝模式未触发，使用置信度模式
            if not triggered:
                if avg_score > self.trigger_avg or score > self.trigger_single:
                    triggered = True
                    trigger_reason = f"置信度触发: 单帧={score:.2f}, 均分={avg_score:.2f}"
                    self.mode_used = "CONFIDENCE"
                    self.alert_trigger_db = db_level  # 也记录分贝值以备后续判断
            
            if triggered:
                logger.info(f"🚨 触发警报: {label} ({trigger_reason})")
                self.is_alerting = True
                self.last_alert_time = current_time
                self.current_danger_info = danger_info
                self.current_alert_label = label

        # 3. 构造并返回结果
        if self.is_alerting and self.current_danger_info:
            zh_label, level, css = self.current_danger_info
            # 在返回结果中包含分贝信息和使用的模式
            current_db = db_level if db_level is not None else 0
            return {
                "is_danger": True, 
                "label": zh_label, 
                "level": level, 
                "css": css,
                "db_level": current_db,
                "mode": self.mode_used,
                "distance_status": self._get_distance_status(current_db)
            }
        else:
            current_db = db_level if db_level is not None else 0
            return {
                "is_danger": False, 
                "label": "安全环境音", 
                "level": "NONE", 
                "css": "",
                "db_level": current_db,
                "mode": self.mode_used,
                "distance_status": "SAFE"
            }
    
    def _get_distance_status(self, current_db: float) -> str:
        """根据分贝值判断距离状态"""
        if current_db >= 80:
            return "VERY_CLOSE"  # 非常近
        elif current_db >= 70:
            return "CLOSE"  # 较近
        elif current_db >= 60:
            return "MEDIUM"  # 中等距离
        elif current_db >= 50:
            return "FAR"  # 较远
        else:
            return "VERY_FAR"  # 很远

# ==========================================
# 全局单例实例化
# ==========================================
_aed_pipeline = None
state_manager = AEDStateManager(
    window_size=5, 
    trigger_avg=0.6, 
    trigger_single=0.8, 
    release_avg=0.2, 
    cooldown=3.0,
    db_window_size=10,       # 记录最近10个分贝值
    db_trigger=65.0,         # 65dB以上触发警报
    db_release=55.0,         # 降至55dB以下可解除
    db_decrease_threshold=5.0  # 分贝下降5dB表示远离
)

def load_aed_model():
    """懒加载魔搭社区的环境音分类小模型"""
    global _aed_pipeline
    if _aed_pipeline is None:
        try:
            from modelscope.pipelines import pipeline
            logger.info("正在加载环境音分类 AED 模型...")
            _aed_pipeline = pipeline(
                task='audio-classification', 
                model='damo/speech_ced_base'
            )
            logger.info("✅ AED 模型加载成功！")
        except ImportError:
            logger.error("缺少 modelscope 库，请确保已安装。")
            _aed_pipeline = "MOCK"
        except Exception as e:
            logger.warning(f"AED 模型加载失败，将启用路演备用模拟器: {e}")
            _aed_pipeline = "MOCK"
    return _aed_pipeline

def detect_environmental_sound(audio_data: tuple) -> dict:
    """处理 Gradio 传来的实时音频流 chunk"""
    if audio_data is None:
        return state_manager.update_and_check("silence", 0.0, db_level=0.0)
        
    sr, y = audio_data
    
    # ====== 核心修复：正确处理不同数据类型的归一化 ==========
    # 将振幅转换为分贝 (dB SPL 近似值)
    if y.dtype == np.int16:
        norm_volume = np.max(np.abs(y)) / 32768.0
    elif y.dtype == np.int32:
        norm_volume = np.max(np.abs(y)) / 2147483648.0
    else:
        norm_volume = np.max(np.abs(y))  # float32 本身就在 0~1 之间

    # 计算实际分贝值
    if norm_volume > 0:
        db_level = 20 * np.log10(norm_volume) + 90
        db_level = max(0, min(120, db_level))
    else:
        db_level = 0.0

    logger.info(f"🔊 [诊断] 归一化振幅: {norm_volume:.6f}, 计算分贝: {db_level:.1f} dB")
    # =============================================
    
    # 遇到完全静音时
    if norm_volume < 0.01:
        return state_manager.update_and_check("silence", 0.0, db_level=db_level)
    
    tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    try:
        wav.write(tmp_wav.name, sr, y)
        model = load_aed_model()
        
        # --- 真实模型推理 ---
        if model != "MOCK":
            try:
                result = model(tmp_wav.name)
                # 提取模型返回的标签和得分
                labels = result[0].get('labels', []) if isinstance(result, list) else result.get('labels', [])
                scores = result[0].get('scores', []) if isinstance(result, list) else result.get('scores', [])
                
                if labels and scores:
                    top_label = str(labels[0]).lower()
                    top_score = float(scores[0])
                    
                    logger.info(f"🔍 [模型识别] label='{top_label}', confidence={top_score:.3f}")
                    
                    # ========== 多重过滤检查 ==========
                    # 1. 先检查是否在过滤列表中（人声、日常噪音等不触发警报）
                    is_filtered = False
                    filter_info = None
                    for key, info in FILTER_SOUNDS.items():
                        if key in top_label:
                            is_filtered = True
                            filter_info = info
                            break
                    
                    if is_filtered:
                        # 在过滤列表中，不触发危险警报，但记录日志
                        logger.info(f"🔇 [过滤] 检测到 {filter_info[0]}，不触发警报")
                        # 传递 None 作为 danger_info，不会触发警报
                        return state_manager.update_and_check(top_label, top_score, None, db_level=db_level)
                    
                    # 2. 检查是否在危险列表中
                    danger_info = None
                    if top_score > 0.3:  # 置信度阈值
                        for key, info in DANGER_SOUNDS.items():
                            if key in top_label:
                                danger_info = info
                                logger.info(f"🚨 [危险检测] 匹配到: {info[0]}")
                                break
                    
                    # 传递给状态机进行判断
                    return state_manager.update_and_check(top_label, top_score, danger_info, db_level=db_level)
                    
            except Exception as infer_err:
                logger.error(f"AED 推理出错: {infer_err}")
                return state_manager.update_and_check("error", 0.0, db_level=db_level)
                    
        # --- 路演容错/演示后门 ---
        else:
            # 核心修复：使用归一化后的 norm_volume 进行对比，警报就能正常解除了
            if norm_volume > 0.8:  # 音量极大时触发模拟警报
                logger.info(f"🔊 [模拟模式] 检测到高音量: {norm_volume:.4f}, 分贝: {db_level:.1f}dB")
                return state_manager.update_and_check(
                    "mock_high_volume", 
                    1.0, 
                    ("🚨 (模拟) 高分贝警报", "HIGH", "extreme-danger-alert"),
                    db_level=db_level
                )
            elif norm_volume > 0.3:  # 中等音量 - 模拟普通环境音
                # 检查是否是人声（日常说话）
                logger.info(f"🔇 [模拟模式] 检测到中等音量: {norm_volume:.4f}, 模拟人声/日常噪音")
                # 返回人声/对话（会被过滤掉）
                return state_manager.update_and_check(
                    "mock_conversation", 
                    0.7, 
                    None,  # 不触发危险警报
                    db_level=db_level
                )
            else:
                return state_manager.update_and_check("mock_normal", 0.0, db_level=db_level)
        
    finally:
        try:
            os.unlink(tmp_wav.name)
        except:
            pass
            
    return state_manager.update_and_check("silence", 0.0, db_level=db_level)