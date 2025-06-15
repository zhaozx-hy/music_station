import pygame
import os
import time
import math
import random
import sys
from mutagen.mp3 import MP3  # 用于获取音频文件时长
from mutagen.wave import WAVE  # 用于获取 WAV 文件时长

# 全局窗口尺寸常量
WIDTH = 1200
HEIGHT = 800

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("音乐播放器")

# 根据图片设计的配色方案
BACKGROUND = (240, 245, 255)  # 浅蓝色背景
PLAYER_BG = (20, 25, 40)  # 播放器背景深色
TEXT_COLOR = (240, 240, 240)  # 文字颜色
ACCENT_COLOR = (255, 204, 0)  # 金色/黄色 来自图片
SECONDARY_COLOR = (180, 190, 210)  # 辅助颜色
PROGRESS_COLOR = (150, 200, 255)  # 进度条颜色
PLAYLIST_BG = (255, 255, 255, 200)  # 播放列表背景 (半透明白色)
VOLUME_BAR_COLOR = (255, 204, 0)  # 金色音量条颜色

# 加载字体 - 修复中文显示问题
try:
    # 尝试加载支持中文的字体
    font_small = pygame.font.Font("simhei.ttf", 16) or pygame.font.SysFont("SimHei", 16)
    font_medium = pygame.font.Font("simhei.ttf", 20) or pygame.font.SysFont("SimHei", 20)
    font_large = pygame.font.Font("simhei.ttf", 28) or pygame.font.SysFont("SimHei", 28)
    font_title = pygame.font.Font("simhei.ttf", 32) or pygame.font.SysFont("SimHei", 32)
    font_track = pygame.font.Font("simhei.ttf", 24) or pygame.font.SysFont("SimHei", 24)
except:
    # 如果找不到支持中文的字体，使用默认系统字体
    font_small = pygame.font.SysFont(None, 16)
    font_medium = pygame.font.SysFont(None, 20)
    font_large = pygame.font.SysFont(None, 28)
    font_title = pygame.font.SysFont(None, 32)
    font_track = pygame.font.SysFont(None, 24)


# 获取音乐文件 - 根据文件夹结构
def get_music_files():
    """从music文件夹中获取音乐文件"""
    music_dir = "../music"

    try:
        music_files = []
        if os.path.exists(music_dir):
            for file in os.listdir(music_dir):
                if file.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                    # 确保文件名正确处理中文
                    try:
                        music_files.append(os.path.join(music_dir, file))
                    except UnicodeDecodeError:
                        # 如果遇到编码问题，尝试使用utf-8
                        music_files.append(os.path.join(music_dir, file.encode('utf-8').decode('utf-8')))

        if music_files:
            print(f"找到 {len(music_files)} 个音乐文件")
            return music_files
        else:
            print("音乐文件夹为空")
            return []
    except Exception as e:
        print(f"扫描音乐文件夹错误: {e}")
        return []


# 获取歌曲时长
def get_song_duration(file_path):
    """获取音频文件的时长（秒）"""
    try:
        # 根据文件扩展名使用不同的解析器
        if file_path.lower().endswith('.mp3'):
            audio = MP3(file_path)
        elif file_path.lower().endswith('.wav'):
            audio = WAVE(file_path)
        else:
            # 对于其他格式，尝试通用方法
            try:
                audio = MP3(file_path)
            except:
                audio = WAVE(file_path)

        return int(audio.info.length)
    except Exception as e:
        print(f"获取音频文件时长错误 {file_path}: {e}")
        # 默认返回180秒
        return 180


# 播放器状态
class PlayerState:
    def __init__(self):
        self.music_files = get_music_files()
        self.current_index = 0  # 从第一首歌开始
        self.playing = False
        self.paused = True  # 初始为暂停状态
        self.current_song = ""
        self.volume = 0.5
        self.progress = 0.0
        self.duration = 0  # 初始时长为0
        self.start_time = 0
        self.song_progress = 0.0
        self.spectrum_data = []
        self.dragging_progress = False

        if self.music_files:
            self.current_song = self.music_files[self.current_index]
            self.set_volume(self.volume)
            self.duration = get_song_duration(self.current_song)  # 初始化时获取第一首歌的时长
            print(f"初始歌曲时长: {self.duration}秒")

    def play(self, index=None):
        if index is not None and 0 <= index < len(self.music_files):
            self.current_index = index
            self.current_song = self.music_files[index]
            self.progress = 0
            self.song_progress = 0

            # 每次播放歌曲时获取其真实时长
            self.duration = get_song_duration(self.current_song)
            print(f"开始播放: {os.path.basename(self.current_song)}, 时长: {self.duration}秒")

            try:
                # 使用pygame.mixer加载并播放音频
                pygame.mixer.music.load(self.current_song)
                pygame.mixer.music.play()
                self.playing = True
                self.paused = False
                self.start_time = time.time()
            except Exception as e:
                print(f"播放错误: {e}")
                self.playing = False
                self.paused = True

    def pause(self):
        if self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            self.song_progress = time.time() - self.start_time

    def unpause(self):
        if self.playing and self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.start_time = time.time() - self.song_progress

    def stop(self):
        if self.playing:
            pygame.mixer.music.stop()
            self.playing = False
        self.paused = False
        self.progress = 0
        self.song_progress = 0

    def next(self):
        if len(self.music_files) > 0:
            new_index = (self.current_index + 1) % len(self.music_files)
            self.play(new_index)

    def prev(self):
        if len(self.music_files) > 0:
            new_index = (self.current_index - 1) % len(self.music_files)
            self.play(new_index)

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)

    def get_current_progress(self):
        if not self.playing or self.paused:
            return self.progress

        elapsed = time.time() - self.start_time
        progress = min(1.0, elapsed / self.duration)

        if progress >= 1.0:
            self.next()
            return 0.0

        self.progress = progress
        return progress

    def get_current_time(self):
        if not self.playing or self.paused:
            return int(self.progress * self.duration)
        return int(time.time() - self.start_time)

    def skip_forward(self):
        """快进15秒"""
        if self.playing:
            new_time = min(self.duration, self.get_current_time() + 15)
            self.seek_to(new_time)

    def skip_backward(self):
        """后退15秒"""
        if self.playing:
            new_time = max(0, self.get_current_time() - 15)
            self.seek_to(new_time)

    def seek_to(self, position):
        """跳转到指定位置"""
        # 计算新的进度百分比
        new_progress = max(0.0, min(1.0, position / self.duration))
        self.progress = new_progress

        # 更新开始时间（相对于当前时间）
        if self.playing and not self.paused:
            pygame.mixer.music.stop()
            self.start_time = time.time() - position
            pygame.mixer.music.play()
            # 设置播放位置（秒）
            pygame.mixer.music.set_pos(position)
        elif self.paused:
            self.song_progress = position
        else:
            self.start_time = time.time() - position

    def get_spectrum(self):
        """生成模拟音频频谱数据"""
        if self.paused:
            return [max(0, d - 0.02) for d in self.spectrum_data]

        t = time.time()
        frequency = 2.0
        amplitude = 0.8
        spectrum = []

        for i in range(64):
            value = math.sin(t * frequency + i * 0.2) * amplitude
            value += math.sin(t * frequency * 1.5 + i * 0.3) * amplitude * 0.4
            value += math.cos(t * frequency * 2.0 + i * 0.4) * amplitude * 0.2
            value += random.uniform(-0.1, 0.1)
            value = max(0, min(1.0, value))
            spectrum.append(value)

        self.spectrum_data = spectrum
        return spectrum


# 创建播放器状态
player = PlayerState()


# 圆形按钮类 - 根据图片设计
class CircleButton:
    def __init__(self, x, y, radius, color, icon=None, action=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.icon = icon
        self.action = action
        self.hover = False
        self.hover_color = (
            min(255, int(color[0] * 1.2)),
            min(255, int(color[1] * 1.2)),
            min(255, int(color[2] * 1.2))
        )

    def draw(self, surface):
        # 按钮背景
        color = self.hover_color if self.hover else self.color
        pygame.draw.circle(surface, PLAYER_BG, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, color, (self.x, self.y), self.radius - 4)

        # 绘制图标
        if self.icon:
            icon_rect = self.icon.get_rect(center=(self.x, self.y))
            surface.blit(self.icon, icon_rect)

    def check_hover(self, pos):
        distance = math.sqrt((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2)
        self.hover = distance <= self.radius
        return self.hover

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover and self.action:
                self.action()
                return True
        return False


# 创建图标
def create_icon(icon_type, size=(28, 28), color=ACCENT_COLOR):
    surface = pygame.Surface(size, pygame.SRCALPHA)

    if icon_type == "play":
        pygame.draw.polygon(surface, color, [
            (10, 6),
            (size[0] - 10, size[1] // 2),
            (10, size[1] - 6)
        ])
    elif icon_type == "pause":
        pygame.draw.rect(surface, color, (8, 8, 8, size[1] - 16))
        pygame.draw.rect(surface, color, (size[0] - 16, 8, 8, size[1] - 16))
    elif icon_type == "prev":
        # 左侧箭头图标
        pygame.draw.polygon(surface, color, [
            (size[0] - 10, 8),
            (10, size[1] // 2),
            (size[0] - 10, size[1] - 8)
        ])
    elif icon_type == "next":
        # 右侧箭头图标
        pygame.draw.polygon(surface, color, [
            (10, 8),
            (size[0] - 10, size[1] // 2),
            (10, size[1] - 8)
        ])
    elif icon_type == "skip_forward":
        # 双箭头向右
        pygame.draw.polygon(surface, color, [
            (5, 8),
            (size[0] // 2 - 5, size[1] // 2),
            (5, size[1] - 8)
        ])
        pygame.draw.polygon(surface, color, [
            (size[0] // 2 + 5, 8),
            (size[0] - 5, size[1] // 2),
            (size[0] // 2 + 5, size[1] - 8)
        ])
    elif icon_type == "skip_backward":
        # 双箭头向左
        pygame.draw.polygon(surface, color, [
            (size[0] - 5, 8),
            (size[0] // 2 + 5, size[1] // 2),
            (size[0] - 5, size[1] - 8)
        ])
        pygame.draw.polygon(surface, color, [
            (size[0] // 2 - 5, 8),
            (5, size[1] // 2),
            (size[0] // 2 - 5, size[1] - 8)
        ])
    elif icon_type == "volume":
        # 音量图标
        pygame.draw.rect(surface, color, (8, size[1] - 20, 4, 8))  # 喇叭底部
        pygame.draw.polygon(surface, color, [
            (8, size[1] - 20),
            (8, size[1] - 25),
            (12, size[1] - 25),
            (15, size[1] - 22),
            (15, size[1] - 18),
            (12, size[1] - 15),
            (8, size[1] - 15)
        ])
        # 音量波浪
        pygame.draw.arc(surface, color, (15, size[1] - 25, 10, 20), math.pi / 2, 3 * math.pi / 2, 1)
        pygame.draw.arc(surface, color, (25, size[1] - 28, 10, 25), math.pi / 2, 3 * math.pi / 2, 1)

    return surface


# 创建图标按钮
play_icon = create_icon("play", (36, 36), ACCENT_COLOR)
pause_icon = create_icon("pause", (36, 36), ACCENT_COLOR)
prev_icon = create_icon("prev", (32, 32), ACCENT_COLOR)
next_icon = create_icon("next", (32, 32), ACCENT_COLOR)
skip_forward_icon = create_icon("skip_forward", (32, 32), ACCENT_COLOR)
skip_backward_icon = create_icon("skip_backward", (32, 32), ACCENT_COLOR)
volume_icon = create_icon("volume", (32, 32), ACCENT_COLOR)

# 创建控制按钮 - 根据图片布局
# 右侧区域中心点
right_center_x = 800
player_center = (right_center_x, HEIGHT // 2 - 20)
control_radius = 28
control_spacing = 80

buttons = [
    # 中央播放按钮
    CircleButton(player_center[0], player_center[1], 60, SECONDARY_COLOR,
                 icon=pause_icon if player.playing and not player.paused else play_icon,
                 action=lambda: player.pause() if player.playing and not player.paused else player.unpause() if player.paused else player.play(
                     player.current_index)),

    # 底部控制按钮
    CircleButton(player_center[0] - control_spacing * 1.5, HEIGHT // 2 + 230, control_radius,
                 SECONDARY_COLOR, icon=prev_icon, action=player.prev),

    CircleButton(player_center[0] - control_spacing * 0.5, HEIGHT // 2 + 230, control_radius,
                 SECONDARY_COLOR, icon=skip_backward_icon, action=player.skip_backward),

    CircleButton(player_center[0] + control_spacing * 0.5, HEIGHT // 2 + 230, control_radius,
                 SECONDARY_COLOR, icon=skip_forward_icon, action=player.skip_forward),

    CircleButton(player_center[0] + control_spacing * 1.5, HEIGHT // 2 + 230, control_radius,
                 SECONDARY_COLOR, icon=next_icon, action=player.next),

    # 添加音量按钮
    CircleButton(player_center[0], HEIGHT // 2 - 300, control_radius,
                 SECONDARY_COLOR, icon=volume_icon, action=None)  # 仅作为音量指示器
]


# 绘制弧形进度条
def draw_arc_progress(surface, x, y, radius, progress, color=ACCENT_COLOR, thickness=10):
    """绘制弧形进度条"""
    # 背景弧
    pygame.draw.arc(surface, (60, 70, 90), (x - radius, y - radius, radius * 2, radius * 2),
                    -math.pi / 2, 3 * math.pi / 2, thickness)

    # 进度弧
    end_angle = -math.pi / 2 + progress * 2 * math.pi
    pygame.draw.arc(surface, color, (x - radius, y - radius, radius * 2, radius * 2),
                    -math.pi / 2, end_angle, thickness)

    # 在进度条终点绘制一个金色圆点作为进度指示器
    handle_x = x + radius * math.cos(end_angle)
    handle_y = y - radius * math.sin(end_angle)  # 注意y轴方向
    pygame.draw.circle(surface, ACCENT_COLOR, (int(handle_x), int(handle_y)), 8)


# 绘制音量条
class VolumeBar:
    def __init__(self, center_x, center_y, radius, thickness=10, start_angle=0.0, end_angle=math.pi):
        self.center = (center_x, center_y)
        self.radius = radius
        self.thickness = thickness
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.dragging = False
        self.background_color = (60, 70, 90)  # 背景颜色
        self.fill_color = VOLUME_BAR_COLOR  # 填充颜色
        self.handle_radius = 12  # 滑块半径
        # 不需要在此处访问player，改为在事件处理中获取

    def calc_handle_pos(self, volume):
        """计算滑块位置"""
        angle = self.start_angle + (self.end_angle - self.start_angle) * volume
        handle_x = self.center[0] + math.cos(angle) * self.radius
        handle_y = self.center[1] - math.sin(angle) * self.radius  # 减去是因为y轴向下
        return (handle_x, handle_y)

    def draw(self, surface, volume):
        """绘制音量条"""
        # 绘制背景弧线
        pygame.draw.arc(surface, self.background_color,
                        (self.center[0] - self.radius, self.center[1] - self.radius,
                         self.radius * 2, self.radius * 2),
                        self.start_angle, self.end_angle, self.thickness)

        # 绘制填充弧线
        fill_end_angle = self.start_angle + (self.end_angle - self.start_angle) * volume
        pygame.draw.arc(surface, self.fill_color,
                        (self.center[0] - self.radius, self.center[1] - self.radius,
                         self.radius * 2, self.radius * 2),
                        self.start_angle, fill_end_angle, self.thickness)

        # 绘制滑块
        self.handle_pos = self.calc_handle_pos(volume)
        pygame.draw.circle(surface, self.fill_color, self.handle_pos, self.handle_radius)

    def handle_event(self, event, player):
        """处理音量条事件"""
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # 检查是否点击了滑块或音量条
            if self.is_over_handle(mouse_pos) or self.is_over_arc(mouse_pos):
                self.dragging = True
                # 更新音量
                self.update_volume(mouse_pos, player)
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_volume(mouse_pos, player)
                return True

        return False

    def is_over_handle(self, pos):
        """检查鼠标是否在滑块上"""
        # 需要先确保handle_pos存在
        if hasattr(self, 'handle_pos'):
            distance = math.sqrt((pos[0] - self.handle_pos[0]) ** 2 + (pos[1] - self.handle_pos[1]) ** 2)
            return distance <= self.handle_radius + 5
        return False

    def is_over_arc(self, pos):
        """检查鼠标是否在音量条上"""
        # 计算鼠标到圆心的距离和角度
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        distance = math.sqrt(dx * dx + dy * dy)

        # 计算角度 (注意y轴方向)
        angle = math.atan2(-dy, dx)  # dy取负因为y轴向下

        # 标准化角度到[0, 2π)范围
        if angle < 0:
            angle += 2 * math.pi

        # 检查角度在有效范围内
        if not (self.start_angle <= angle <= self.end_angle):
            # 处理跨越0度的情况
            if self.start_angle > self.end_angle and (angle >= self.start_angle or angle <= self.end_angle):
                return True
            return False

        return abs(distance - self.radius) <= self.thickness + 5

    def update_volume(self, mouse_pos, player):
        """根据鼠标位置更新音量"""
        dx = mouse_pos[0] - self.center[0]
        dy = mouse_pos[1] - self.center[1]

        # 计算鼠标位置相对于圆心的角度
        # 注意：由于在屏幕上y轴向下，所以我们需要取负值
        angle = math.atan2(-dy, dx)

        # 标准化角度到[0, 2π)范围
        if angle < 0:
            angle += 2 * math.pi

        # 计算音量值（0-1）
        if self.end_angle > self.start_angle:
            # 正常情况
            if angle < self.start_angle:
                volume = 0.0
            elif angle > self.end_angle:
                volume = 1.0
            else:
                volume = (angle - self.start_angle) / (self.end_angle - self.start_angle)
        else:
            # 处理圆弧跨越0度的特殊情况
            if angle >= self.start_angle:
                volume = (angle - self.start_angle) / (self.end_angle + (2 * math.pi - self.start_angle))
            else:
                volume = (angle + (2 * math.pi - self.start_angle)) / (
                        self.end_angle + (2 * math.pi - self.start_angle))

        player.set_volume(volume)


# 添加新的圆形进度条交互类
class ProgressBar:
    def __init__(self, center_x, center_y, radius, thickness=10):
        self.center = (center_x, center_y)
        self.radius = radius
        self.thickness = thickness
        self.dragging = False
        self.handle_radius = 8  # 进度条手柄大小

    def draw(self, surface, progress):
        """绘制进度条"""
        # 背景弧
        pygame.draw.arc(surface, (60, 70, 90),
                        (self.center[0] - self.radius, self.center[1] - self.radius, self.radius * 2, self.radius * 2),
                        -math.pi / 2, 3 * math.pi / 2, self.thickness)

        # 进度弧
        end_angle = -math.pi / 2 + progress * 2 * math.pi
        pygame.draw.arc(surface, ACCENT_COLOR,
                        (self.center[0] - self.radius, self.center[1] - self.radius, self.radius * 2, self.radius * 2),
                        -math.pi / 2, end_angle, self.thickness)

        # 在进度条终点绘制一个金色圆点作为进度指示器
        adjusted_radius = self.radius - self.thickness / 2
        handle_x = self.center[0] + adjusted_radius * math.cos(end_angle)
        handle_y = self.center[1] - adjusted_radius * math.sin(end_angle)  # 注意y轴方向
        pygame.draw.circle(surface, ACCENT_COLOR, (int(handle_x), int(handle_y)), self.handle_radius)

        # 返回当前手柄位置
        return (handle_x, handle_y)

    def handle_event(self, event, player):
        """处理进度条事件"""
        # 计算当前进度条手柄位置
        progress = player.get_current_progress()
        end_angle = -math.pi / 2 + progress * 2 * math.pi
        handle_x = self.center[0] + self.radius * math.cos(end_angle)
        handle_y = self.center[1] - self.radius * math.sin(end_angle)
        handle_pos = (handle_x, handle_y)

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # 检查是否点击了手柄或进度条
            if self.is_over_handle(mouse_pos, handle_pos) or self.is_over_arc(mouse_pos):
                self.dragging = True
                # 更新进度
                self.update_progress(mouse_pos, player)
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_progress(mouse_pos, player)
                return True

        return False

    def is_over_handle(self, mouse_pos, handle_pos):
        """检查鼠标是否在手柄上"""
        distance = math.sqrt((mouse_pos[0] - handle_pos[0]) ** 2 + (mouse_pos[1] - handle_pos[1]) ** 2)
        return distance <= self.handle_radius + 5

    def is_over_arc(self, mouse_pos):
        """检查鼠标是否在进度条上"""
        # 计算鼠标到圆心的距离
        dx = mouse_pos[0] - self.center[0]
        dy = mouse_pos[1] - self.center[1]
        distance = math.sqrt(dx * dx + dy * dy)

        # 检查是否在进度条附近
        return self.radius - self.thickness <= distance <= self.radius + self.thickness

    def update_progress(self, mouse_pos, player):
        """根据鼠标位置更新播放进度"""
        # 计算相对于圆心的角度
        dx = mouse_pos[0] - self.center[0]
        dy = self.center[1] - mouse_pos[1]  # 注意y轴方向反转
        angle = math.atan2(dy, dx)

        # 标准化角度到0-2π范围
        if angle < 0:
            angle += 2 * math.pi

        # 将角度转换为进度
        start_angle = 3 * math.pi / 2
        end_angle = 7 * math.pi / 2

        # 计算当前角度对应的进度
        progress_angle = (angle - start_angle) % (2 * math.pi)
        progress = progress_angle / (2 * math.pi)

        # 更新播放进度
        player.seek_to(progress * player.duration)


# 音量条角度
def degrees_to_radians(degrees):
    return degrees * (math.pi / 180)


# 创建音量条对象
volume_bar_radius = 230  # 音量条半径
# 将音量条放在圆形播放区域正上方，上方75像素的位置
volume_bar_center = (player_center[0], player_center[1] - 95)

# 设置音量条的角度范围
start_angle = degrees_to_radians(30)
end_angle = degrees_to_radians(150)

volume_bar = VolumeBar(volume_bar_center[0], volume_bar_center[1],
                       volume_bar_radius, thickness=10,
                       start_angle=start_angle, end_angle=end_angle)

# 创建圆形进度条对象（外部的大圆环）
progress_bar_radius = 220  # 进度条半径
progress_bar_center = player_center
progress_bar = ProgressBar(progress_bar_center[0], progress_bar_center[1], progress_bar_radius, thickness=12)


# 绘制播放器 - 移至右侧区域中心并增大尺寸
def draw_player(surface):
    """绘制音乐播放器，移至右侧区域中心并增大尺寸"""
    # 增大圆形控件尺寸
    player_radius = 180

    # 绘制深蓝色背景圆
    pygame.draw.circle(surface, PLAYER_BG, player_center, player_radius + 25)

    # 绘制内圆
    pygame.draw.circle(surface, (40, 50, 70), player_center, player_radius, 0)

    # 绘制金色边框
    pygame.draw.circle(surface, ACCENT_COLOR, player_center, player_radius, 5)

    # 绘制圆形进度条（外部大圆环）
    progress = player.get_current_progress()
    handle_pos = progress_bar.draw(surface, progress)

    # 绘制曲目编号 - TRACK 01
    track_text = font_track.render(f"TRACK {player.current_index + 1:02d}", True, SECONDARY_COLOR)
    track_rect = track_text.get_rect(center=(player_center[0], player_center[1] - 90))
    surface.blit(track_text, track_rect)

    # 绘制曲目名称
    if player.current_song:
        song_name = os.path.basename(player.current_song)
        song_name = os.path.splitext(song_name)[0]

        # 处理中文文件名显示
        try:
            # 尝试直接渲染
            name_text = font_medium.render(song_name, True, TEXT_COLOR)
        except:
            try:
                # 如果失败，尝试使用UTF-8编码
                name_text = font_medium.render(song_name.encode('utf-8').decode('utf-8'), True, TEXT_COLOR)
            except:
                # 如果还不行，显示简单信息
                name_text = font_medium.render("当前曲目", True, TEXT_COLOR)

        name_rect = name_text.get_rect(center=(player_center[0], player_center[1] + 90))
        surface.blit(name_text, name_rect)

    # 绘制时间显示
    current_time = player.get_current_time()
    total_time = player.duration
    current_min = current_time // 60
    current_sec = current_time % 60
    total_min = total_time // 60
    total_sec = total_time % 60

    time_str = f"{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}"
    time_text = font_medium.render(time_str, True, SECONDARY_COLOR)
    time_rect = time_text.get_rect(center=(player_center[0], player_center[1] + 120))
    surface.blit(time_text, time_rect)

    # 绘制控制按钮
    for button in buttons:
        button.draw(surface)

    # 在音量按钮下方显示当前音量百分比
    volume_percent = int(player.volume * 100)
    volume_text = font_medium.render(f"{volume_percent}%", True, ACCENT_COLOR)
    volume_rect = volume_text.get_rect(center=(player_center[0], HEIGHT // 2 -260))
    surface.blit(volume_text, volume_rect)


# 绘制播放列表 - 根据图片调整内容
def draw_playlist(surface):
    """绘制播放列表 - 左侧"""
    playlist_width = 320
    playlist_height = HEIGHT - 40
    playlist_x = 40
    playlist_y = 20

    # 绘制播放列表背景
    playlist_bg = pygame.Surface((playlist_width, playlist_height), pygame.SRCALPHA)
    playlist_bg.fill(PLAYLIST_BG)
    surface.blit(playlist_bg, (playlist_x, playlist_y))

    # 绘制标题
    title_text = font_large.render("播放列表", True, (40, 45, 60))
    surface.blit(title_text, (playlist_x + 30, playlist_y + 20))

    # 绘制分隔线
    pygame.draw.line(surface, (200, 210, 230),
                     (playlist_x + 20, playlist_y + 70),
                     (playlist_x + playlist_width - 20, playlist_y + 70), 2)

    # 绘制歌曲列表
    for i, song in enumerate(player.music_files):
        y_pos = playlist_y + 90 + i * 50
        is_current = i == player.current_index

        # 绘制歌曲项背景
        if is_current:
            pygame.draw.rect(surface, (230, 235, 245),
                             (playlist_x + 20, y_pos - 10, playlist_width - 40, 40),
                             border_radius=5)

        # 绘制编号
        num_text = font_medium.render(f"{i + 1:02d}.", True, (100, 110, 130))
        surface.blit(num_text, (playlist_x + 40, y_pos))

        # 绘制歌曲名
        base_name = os.path.basename(song)
        display_name = os.path.splitext(base_name)[0]

        # 根据图片仅显示文件名，不显示扩展名
        try:
            # 尝试直接渲染
            text_surf = font_medium.render(display_name, True, (40, 45, 60))
        except:
            try:
                # 如果失败，尝试使用UTF-8编码
                text_surf = font_medium.render(display_name.encode('utf-8').decode('utf-8'), True, (40, 45, 60))
            except:
                # 如果还不行，显示文件序号
                text_surf = font_medium.render(f"歌曲 {i + 1:02d}", True, (40, 45, 60))

        surface.blit(text_surf, (playlist_x + 90, y_pos))

    return pygame.Rect(playlist_x, playlist_y, playlist_width, playlist_height)


# 主循环
running = True
clock = pygame.time.Clock()

# 初始播放曲目 - 第一首
if player.music_files:
    player.play(0)
    player.pause()

while running:
    mouse_pos = pygame.mouse.get_pos()
    progress = player.get_current_progress()

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 处理按钮点击
        for button in buttons:
            button.check_hover(mouse_pos)
            button.handle_event(event)

        # 处理音量条事件
        volume_bar.handle_event(event, player)

        # 处理进度条事件
        progress_bar.handle_event(event, player)

        # 处理播放列表点击
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            playlist_rect = pygame.Rect(40, 20, 320, HEIGHT - 40)
            if playlist_rect.collidepoint(mouse_pos):
                # 计算点击了哪首歌 - 根据位置计算索引
                relative_y = mouse_pos[1] - (20 + 90)  # 减去标题和分隔线高度
                index = relative_y // 50
                if 0 <= index < len(player.music_files):
                    player.play(index)
                    player.unpause()

        # 处理全局进度条拖动
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            player.dragging_progress = True
        elif event.type == pygame.MOUSEBUTTONUP:
            player.dragging_progress = False

    # 更新按钮悬停状态
    for button in buttons:
        button.check_hover(mouse_pos)

    # 更新中央播放按钮图标
    if buttons:  # 确保buttons列表不为空
        buttons[0].icon = pause_icon if player.playing and not player.paused else play_icon

    # 绘制界面
    screen.fill(BACKGROUND)

    # 绘制播放器 - 移至右侧区域中心
    if player.music_files:  # 有歌曲时才绘制
        draw_player(screen)

    # 绘制播放列表
    draw_playlist(screen)

    # 绘制音量条
    if player.music_files:  # 有歌曲时才绘制
        volume_bar.draw(screen, player.volume)

    pygame.display.flip()
    clock.tick(60)

# 退出
pygame.mixer.music.stop()
pygame.quit()